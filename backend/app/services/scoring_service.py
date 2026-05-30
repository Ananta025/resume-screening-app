import math
import re
import logging
from collections import Counter
from dataclasses import dataclass

from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.services.jd_parser import jd_parser
from app.services.resume_parser import resume_parser


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CandidateScore:
    resume_id: int
    jd_id: int
    final_score: float
    skills_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    experience_score: float
    education_score: float
    semantic_score: float
    rank: int = 0


class ScoringService:
    def _extract_years(self, text: str) -> float:
        if not text:
            return 0.0

        match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))

        return 0.0

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}", text.lower())
        return {token for token in tokens if len(token) > 2}

    def _token_counts(self, text: str) -> Counter[str]:
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}", text.lower())
        return Counter(token for token in tokens if len(token) > 2)

    def _overlap_score(self, left_text: str, right_text: str) -> float:
        left_tokens = self._token_counts(left_text)
        right_tokens = self._token_counts(right_text)

        if not left_tokens or not right_tokens:
            return 0.0

        shared_tokens = set(left_tokens) & set(right_tokens)
        if not shared_tokens:
            return 0.0

        shared_weight = sum(min(left_tokens[token], right_tokens[token]) for token in shared_tokens)
        total_weight = sum(max(left_tokens[token], right_tokens[token]) for token in set(left_tokens) | set(right_tokens))

        if total_weight <= 0:
            return 0.0

        return round((shared_weight / total_weight) * 100, 2)

    def _cosine_similarity(self, left_text: str, right_text: str) -> float:
        left_tokens = self._token_counts(left_text)
        right_tokens = self._token_counts(right_text)

        if not left_tokens or not right_tokens:
            return 0.0

        shared_tokens = set(left_tokens) & set(right_tokens)
        if not shared_tokens:
            return 0.0

        dot_product = sum(left_tokens[token] * right_tokens[token] for token in shared_tokens)
        left_magnitude = math.sqrt(sum(count * count for count in left_tokens.values()))
        right_magnitude = math.sqrt(sum(count * count for count in right_tokens.values()))

        if left_magnitude <= 0 or right_magnitude <= 0:
            return 0.0

        return round((dot_product / (left_magnitude * right_magnitude)) * 100, 2)

    def _semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        overlap_score = self._overlap_score(resume_text, jd_text)
        cosine_score = self._cosine_similarity(resume_text, jd_text)

        if overlap_score == 0 and cosine_score == 0:
            return 0.0

        return round((overlap_score * 0.55) + (cosine_score * 0.45), 2)

    def _skills_score(self, resume_skills: list[str], jd_skills: list[str], resume_text: str, jd_text: str) -> tuple[float, list[str], list[str]]:
        resume_skill_lookup = {skill.lower(): skill for skill in resume_skills}
        jd_skill_lookup = {skill.lower(): skill for skill in jd_skills}

        matching_skill_keys = [skill.lower() for skill in jd_skills if skill.lower() in resume_skill_lookup]
        matching_skills = [resume_skill_lookup[key] for key in matching_skill_keys]
        missing_skills = [jd_skill_lookup[key] for key in jd_skill_lookup if key not in resume_skill_lookup]

        if jd_skill_lookup:
            skills_score = round((len(matching_skills) / len(jd_skill_lookup)) * 100, 2)
        else:
            skills_score = self._semantic_similarity(resume_text, jd_text)

        return skills_score, matching_skills, missing_skills

    def _education_score(self, resume_education: list[str], required_education: list[str]) -> float:
        if not required_education:
            if not resume_education:
                return 0.0
            return round(min(45.0 + (len(resume_education) * 12.5), 100.0), 2)

        resume_text = " ".join(resume_education).lower()
        matches = sum(1 for requirement in required_education if requirement.lower() in resume_text)
        return round((matches / len(required_education)) * 100, 2)

    def _experience_score(self, resume_experience: str, jd_experience: str, resume_years: float, required_years: float) -> float:
        experience_similarity = self._semantic_similarity(resume_experience, jd_experience)

        if required_years > 0 and resume_years > 0:
            years_ratio = min(resume_years / required_years, 1.0)
            return round(max(0.0, min((years_ratio * 85) + (experience_similarity * 0.15), 100.0)), 2)

        if required_years > 0 and resume_years <= 0:
            return round(min(experience_similarity * 0.75, 75.0), 2)

        if resume_years > 0:
            return round(min(35.0 + (resume_years * 8.0) + (experience_similarity * 0.35), 100.0), 2)

        return round(min(20.0 + (experience_similarity * 0.8), 100.0), 2)

    def calculate_candidate_score(self, resume: Resume, job_description: JobDescription) -> CandidateScore:
        resume_text = resume.extracted_text or ""
        jd_text = job_description.jd_text or ""

        resume_details = resume_parser.parse_text(resume_text)
        jd_requirements = jd_parser.parse_text(jd_text)

        skills_score, matching_skills, missing_skills = self._skills_score(
            resume_details.skills,
            jd_requirements.required_skills,
            resume_text,
            jd_text,
        )

        resume_years = self._extract_years(resume_details.experience)
        required_years = self._extract_years(jd_requirements.required_experience)
        experience_score = self._experience_score(
            resume_details.experience,
            jd_requirements.required_experience,
            resume_years,
            required_years,
        )

        education_score = self._education_score(resume_details.education, jd_requirements.required_education)
        semantic_score = self._semantic_similarity(resume_text, jd_text)

        final_score = round(
            (skills_score * 0.4)
            + (experience_score * 0.3)
            + (education_score * 0.1)
            + (semantic_score * 0.2),
            2,
        )

        logger.info(f"Skills Score: {skills_score}")
        logger.info(f"Experience Score: {experience_score}")
        logger.info(f"Education Score: {education_score}")
        logger.info(f"Semantic Score: {semantic_score}")
        logger.info(f"Final Score: {final_score}")

        return CandidateScore(
            resume_id=resume.id,
            jd_id=job_description.id,
            final_score=max(0.0, min(final_score, 100.0)),
            skills_score=skills_score,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            experience_score=experience_score,
            education_score=education_score,
            semantic_score=semantic_score,
        )


scoring_service = ScoringService()