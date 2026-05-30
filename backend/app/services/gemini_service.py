from __future__ import annotations

import json
import logging
import os
import random
import re
import time
from dataclasses import asdict
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.services.jd_parser import jd_parser
from app.services.resume_parser import resume_parser


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class ResumeDetailsModel(BaseModel):
    name: str = ""
    email: str = ""
    phone_number: str = ""
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: str = ""


class JDRequirementsModel(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    required_experience: str = ""
    required_education: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class ResumeJDComparisonModel(BaseModel):
    match_score: float = Field(default=0, ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    summary: str = ""
    recommendation: str = ""
    analysis_source: str = "gemini"
    resume_details: ResumeDetailsModel
    jd_requirements: JDRequirementsModel


class GeminiService:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = settings.gemini_model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._client: genai.Client | None = None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise RuntimeError("GEMINI_API_KEY is not configured")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _build_config(self, schema_model: type[BaseModel]) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=schema_model,
        )

    def _parse_json_payload(self, raw_text: str, schema_model: type[T]) -> dict[str, Any]:
        def extract_json_fragment(text: str) -> str:
            stripped_text = text.strip()

            if not stripped_text:
                raise ValueError("Gemini response text was empty")

            if stripped_text.startswith("```"):
                stripped_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped_text, flags=re.IGNORECASE | re.DOTALL).strip()

            logger.debug("Gemini extracted text before JSON parse for %s: %s", schema_model.__name__, stripped_text)

            try:
                json.loads(stripped_text)
                return stripped_text
            except json.JSONDecodeError:
                pass

            fragment_starts = [index for index in (stripped_text.find("{"), stripped_text.find("[")) if index != -1]
            if not fragment_starts:
                raise ValueError("Gemini response did not contain JSON")

            start_index = min(fragment_starts)
            fragment = stripped_text[start_index:]

            depth = 0
            in_string = False
            escaped = False
            closing_char = "}" if fragment[0] == "{" else "]"

            for offset, character in enumerate(fragment):
                if escaped:
                    escaped = False
                    continue

                if character == "\\":
                    escaped = True
                    continue

                if character == '"' and not escaped:
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if character in "[{":
                    depth += 1
                elif character in "]}":
                    depth -= 1
                    if depth == 0 and character == closing_char:
                        return fragment[: offset + 1].strip()

            raise ValueError("Gemini response contained an incomplete JSON fragment")

        try:
            json_fragment = extract_json_fragment(raw_text)
            logger.debug("Gemini JSON fragment for %s: %s", schema_model.__name__, json_fragment)
            parsed_payload = json.loads(json_fragment)
            if not isinstance(parsed_payload, dict):
                raise ValueError(f"Gemini JSON payload for {schema_model.__name__} must be an object")
            logger.debug("Gemini JSON parsed payload for %s: %s", schema_model.__name__, json.dumps(parsed_payload, ensure_ascii=False, default=str))
            return parsed_payload
        except Exception:
            logger.exception("Gemini JSON parsing failed for %s", schema_model.__name__)
            raise

    def _generate_structured_json(
        self,
        prompt: str,
        schema_model: type[T],
        fallback_payload: dict[str, Any],
        retries: int = 3,
    ) -> dict[str, Any]:
        def merge_with_defaults(defaults: Any, payload: Any) -> Any:
            if isinstance(defaults, dict) and isinstance(payload, dict):
                merged_payload: dict[str, Any] = {}

                for key, default_value in defaults.items():
                    if key in payload:
                        payload_value = payload[key]
                        if isinstance(default_value, dict) and isinstance(payload_value, dict):
                            merged_payload[key] = merge_with_defaults(default_value, payload_value)
                        else:
                            merged_payload[key] = payload_value
                    else:
                        merged_payload[key] = default_value

                for key, payload_value in payload.items():
                    if key not in merged_payload:
                        merged_payload[key] = payload_value

                return merged_payload

            return payload if payload is not None else defaults

        def read_response_text(response: Any) -> tuple[str, str]:
            response_text = ""
            candidate_text = ""

            try:
                response_text = getattr(response, "text", "") or ""
            except Exception as exc:  # noqa: BLE001 - third-party SDK attribute access
                raise ValueError(f"Unable to read Gemini response.text: {exc}") from exc

            candidates = getattr(response, "candidates", None) or []
            candidate_fragments: list[str] = []

            for candidate_index, candidate in enumerate(candidates):
                candidate_content = getattr(candidate, "content", None)
                parts = getattr(candidate_content, "parts", None) or []
                part_texts = [getattr(part, "text", "") or "" for part in parts if getattr(part, "text", None)]
                candidate_text = "".join(part_texts).strip()
                logger.debug(
                    "Gemini candidate[%s] parts text for %s: %s",
                    candidate_index,
                    schema_model.__name__,
                    candidate_text if candidate_text else "<empty>",
                )
                if candidate_text:
                    candidate_fragments.append(candidate_text)

            candidate_text = "\n".join(candidate_fragments).strip()
            return response_text.strip(), candidate_text

        if not self.is_configured():
            logger.info("Using local fallback because: GEMINI_API_KEY is not configured")
            return schema_model.model_validate(fallback_payload).model_dump()

        client = self._get_client()
        last_failure_reason = "Gemini analysis was not completed"

        for attempt in range(1, retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self._build_config(schema_model),
                )
                logger.info("Gemini response received")
                logger.debug("Gemini raw response for %s: %r", schema_model.__name__, response)

                response_text, candidate_text = read_response_text(response)
                logger.debug(
                    "Gemini response.text for %s: %s",
                    schema_model.__name__,
                    response_text if response_text else "<empty>",
                )
                if candidate_text:
                    logger.debug(
                        "Gemini candidates.parts text for %s: %s",
                        schema_model.__name__,
                        candidate_text,
                    )

                response_sources = [
                    ("response.text", response_text),
                    ("candidates.parts", candidate_text),
                ]

                parsed_payload: dict[str, Any] | None = None
                parsed_source = ""

                for source_name, source_text in response_sources:
                    if not source_text:
                        continue

                    try:
                        parsed_payload = self._parse_json_payload(source_text, schema_model)
                        parsed_source = source_name
                        logger.info("Gemini JSON parsed successfully from %s", source_name)
                        break
                    except Exception as exc:  # noqa: BLE001 - parsing failures are expected fallback triggers
                        last_failure_reason = f"Gemini JSON parsing failed from {source_name}: {exc}"
                        logger.exception("Using local fallback because: %s", last_failure_reason)

                if parsed_payload is None:
                    last_failure_reason = "Gemini response was empty or did not contain parseable JSON"
                    raise ValueError(last_failure_reason)

                normalized_payload = merge_with_defaults(fallback_payload, parsed_payload)
                if schema_model is ResumeJDComparisonModel:
                    normalized_payload["analysis_source"] = "gemini"

                logger.debug(
                    "Gemini normalized payload for %s from %s: %s",
                    schema_model.__name__,
                    parsed_source,
                    json.dumps(normalized_payload, ensure_ascii=False, default=str),
                )

                try:
                    validated_model = schema_model.model_validate(normalized_payload)
                except ValidationError as exc:
                    last_failure_reason = f"Gemini schema validation failed after normalization: {exc}"
                    logger.exception("Using local fallback because: %s", last_failure_reason)
                    raise

                logger.info("Pydantic validation passed for %s", schema_model.__name__)
                logger.info("Using Gemini analysis")
                return validated_model.model_dump()

            except ValidationError:
                if attempt < retries:
                    time.sleep((2 ** (attempt - 1)) + random.random())
                continue
            except ValueError as exc:
                if last_failure_reason == "Gemini analysis was not completed":
                    last_failure_reason = str(exc)
                if attempt < retries:
                    time.sleep((2 ** (attempt - 1)) + random.random())
                continue
            except Exception as exc:  # noqa: BLE001 - third-party SDK/network failures
                last_failure_reason = f"Gemini request failed: {exc}"
                logger.exception("Using local fallback because: %s", last_failure_reason)
                if attempt < retries:
                    time.sleep((2 ** (attempt - 1)) + random.random())

        logger.warning("Using local fallback because: %s", last_failure_reason)
        return schema_model.model_validate(fallback_payload).model_dump()

    def _local_comparison(self, resume_text: str, jd_text: str) -> dict[str, Any]:
        resume_details = resume_parser.parse_text(resume_text)
        jd_requirements = jd_parser.parse_text(jd_text)

        resume_skill_lookup = {skill.lower(): skill for skill in resume_details.skills}
        jd_skill_lookup = {skill.lower(): skill for skill in jd_requirements.required_skills}

        matched_skill_keys = sorted(resume_skill_lookup.keys() & jd_skill_lookup.keys())
        matched_skills = [resume_skill_lookup[key] for key in matched_skill_keys]
        missing_skills = [jd_skill_lookup[key] for key in sorted(jd_skill_lookup.keys() - resume_skill_lookup.keys())]

        total_required = max(len(jd_skill_lookup), 1)
        match_score = round((len(matched_skills) / total_required) * 100, 2)

        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "summary": "Local fallback comparison generated because Gemini is not configured.",
            "recommendation": "Connect a Gemini API key to enable AI-generated comparison output.",
            "analysis_source": "local_fallback",
            "resume_details": asdict(resume_details),
            "jd_requirements": asdict(jd_requirements),
        }

    def extract_resume_details(self, text: str) -> dict[str, Any]:
        fallback_payload = asdict(resume_parser.parse_text(text))
        prompt = (
            "Extract resume details from the following resume text and return JSON only. "
            "Include the fields: name, email, phone_number, skills, education, experience. "
            "Use empty strings or empty arrays when information is missing.\n\n"
            f"Resume text:\n{text}"
        )
        return self._generate_structured_json(prompt, ResumeDetailsModel, fallback_payload)

    def extract_jd_requirements(self, text: str) -> dict[str, Any]:
        fallback_payload = asdict(jd_parser.parse_text(text))
        prompt = (
            "Extract job description requirements from the following text and return JSON only. "
            "Include the fields: required_skills, required_experience, required_education, keywords. "
            "Use empty strings or empty arrays when information is missing.\n\n"
            f"Job description text:\n{text}"
        )
        return self._generate_structured_json(prompt, JDRequirementsModel, fallback_payload)

    def compare_resume_with_jd(self, resume_text: str, jd_text: str) -> dict[str, Any]:
        fallback_payload = self._local_comparison(resume_text, jd_text)
        prompt = (
            "Compare the resume against the job description and return JSON only. "
            "Include the fields: match_score, matched_skills, missing_skills, summary, recommendation, analysis_source, resume_details, jd_requirements. "
            "The resume_details object must contain name, email, phone_number, skills, education, experience. "
            "The jd_requirements object must contain required_skills, required_experience, required_education, keywords. "
            "match_score must be a number between 0 and 100.\n\n"
            f"Resume text:\n{resume_text}\n\nJob description text:\n{jd_text}"
        )
        return self._generate_structured_json(prompt, ResumeJDComparisonModel, fallback_payload)


gemini_service = GeminiService()