import math
import re
from dataclasses import dataclass

from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.services.jd_parser import jd_parser
from app.services.resume_parser import resume_parser


@dataclass(slots=True)
class CandidateScore:
    resume_id: int
    jd_id: int
    final_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    experience_score: float
    education_score: float
    semantic_score: float
    skill_match_score: float
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

    def _semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        resume_tokens = self._tokenize(resume_text)
        jd_tokens = self._tokenize(jd_text)
        if not resume_tokens or not jd_tokens:
            return 0.0

        return round((len(resume_tokens & jd_tokens) / len(resume_tokens | jd_tokens)) * 100, 2)

    def _education_score(self, resume_education: list[str], required_education: list[str]) -> float:
        if not required_education:
            return 100.0

        resume_text = " ".join(resume_education).lower()
        matches = sum(1 for requirement in required_education if requirement.lower() in resume_text)
        return round((matches / len(required_education)) * 100, 2)

    def calculate_candidate_score(self, resume: Resume, job_description: JobDescription) -> CandidateScore:
        resume_text = resume.extracted_text or ""
        jd_text = job_description.jd_text or ""

        resume_details = resume_parser.parse_text(resume_text)
        jd_requirements = jd_parser.parse_text(jd_text)

        resume_skill_lookup = {skill.lower(): skill for skill in resume_details.skills}
        jd_skill_lookup = {skill.lower(): skill for skill in jd_requirements.required_skills}

        matching_skill_keys = [skill.lower() for skill in jd_requirements.required_skills if skill.lower() in resume_skill_lookup]
        matching_skills = [resume_skill_lookup[key] for key in matching_skill_keys]
        missing_skills = [jd_skill_lookup[key] for key in jd_skill_lookup if key not in resume_skill_lookup]

        skill_match_score = 100.0 if not jd_skill_lookup else round((len(matching_skills) / len(jd_skill_lookup)) * 100, 2)

        resume_years = self._extract_years(resume_details.experience)
        required_years = self._extract_years(jd_requirements.required_experience)
        if required_years <= 0:
            experience_score = 100.0 if resume_years > 0 else 75.0
        elif resume_years <= 0:
            experience_score = 0.0
        else:
            experience_score = round(min(resume_years / required_years, 1.0) * 100, 2)

        education_score = self._education_score(resume_details.education, jd_requirements.required_education)
        semantic_score = self._semantic_similarity(resume_text, jd_text)

        final_score = round(
            (skill_match_score * 0.4)
            + (experience_score * 0.3)
            + (education_score * 0.1)
            + (semantic_score * 0.2),
            2,
        )

        return CandidateScore(
            resume_id=resume.id,
            jd_id=job_description.id,
            final_score=max(0.0, min(final_score, 100.0)),
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            experience_score=experience_score,
            education_score=education_score,
            semantic_score=semantic_score,
            skill_match_score=skill_match_score,
        )


scoring_service = ScoringService()