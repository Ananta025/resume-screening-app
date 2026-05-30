from app.models.analysis_result import AnalysisResult
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.services.scoring_service import scoring_service


STRONG_RESUME = """
Jane Doe
Senior Frontend Engineer with 8 years of experience building React, TypeScript, Next.js, Tailwind CSS,
Node.js, FastAPI integrations, AWS deployments, Docker workflows, and PostgreSQL-backed applications.
Experience: 8+ years in React and TypeScript, 5+ years leading frontend architecture.
Education: Bachelor of Computer Science.
"""

MEDIUM_RESUME = """
John Smith
Frontend Developer with 4 years of experience building React interfaces and JavaScript applications.
Worked with CSS, HTML, and some TypeScript. Familiar with REST APIs and basic cloud deployments.
Education: Bachelor of Information Technology.
"""

POOR_RESUME = """
Alex Johnson
Content writer with 1 year of experience creating blog posts and marketing copy.
Skilled in communication, editing, and research. No technical background.
Education: Bachelor of Arts in English.
"""

JOB_DESCRIPTION = """
We are hiring a Senior Frontend Engineer with 5+ years of experience in React, TypeScript, Next.js,
Tailwind CSS, Node.js, AWS, Docker, PostgreSQL, and FastAPI. Bachelor degree preferred.
"""


def _build_resume(resume_id: int, text: str) -> Resume:
    return Resume(
        id=resume_id,
        candidate_name=f"Candidate {resume_id}",
        file_name=f"candidate-{resume_id}.pdf",
        file_path=f"/tmp/candidate-{resume_id}.pdf",
        extracted_text=text,
    )


def _build_job_description(jd_id: int, text: str) -> JobDescription:
    return JobDescription(
        id=jd_id,
        title="Senior Frontend Engineer",
        jd_text=text,
    )


def test_candidate_scores_vary_significantly_across_match_levels():
    job_description = _build_job_description(1, JOB_DESCRIPTION)

    strong = scoring_service.calculate_candidate_score(_build_resume(1, STRONG_RESUME), job_description)
    medium = scoring_service.calculate_candidate_score(_build_resume(2, MEDIUM_RESUME), job_description)
    poor = scoring_service.calculate_candidate_score(_build_resume(3, POOR_RESUME), job_description)

    assert strong.final_score > medium.final_score > poor.final_score
    assert strong.skills_score > medium.skills_score > poor.skills_score
    assert strong.semantic_score >= medium.semantic_score >= poor.semantic_score
    assert strong.final_score - poor.final_score >= 20
    assert strong.final_score != medium.final_score
    assert medium.final_score != poor.final_score
