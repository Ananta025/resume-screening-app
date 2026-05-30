import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis_result import AnalysisResult
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.analysis_schema import AnalysisRequest, AnalysisResponse, AnalysisResultRead
from app.services.gemini_service import gemini_service
from app.services.ranking_service import ranking_service
from app.services.scoring_service import CandidateScore
from app.services.scoring_service import scoring_service


router = APIRouter(tags=["Analysis"])
logger = logging.getLogger(__name__)


def _serialize_analysis_result(result: AnalysisResult) -> AnalysisResultRead:
    matching_skills = json.loads(result.matching_skills or "[]")
    missing_skills = json.loads(result.missing_skills or "[]")

    return AnalysisResultRead(
        id=result.id,
        resume_id=result.resume_id,
        jd_id=result.jd_id,
        score=float(result.score),
        final_score=float(result.score),
        rank=result.rank,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        experience_score=float(result.experience_score),
        education_score=float(result.education_score),
        semantic_score=float(result.semantic_score),
        created_at=result.created_at,
    )


def _build_candidate_score(resume: Resume, job_description: JobDescription) -> tuple[CandidateScore, str]:
    local_score = scoring_service.calculate_candidate_score(resume, job_description)
    comparison = gemini_service.compare_resume_with_jd(resume.extracted_text or "", job_description.jd_text or "")
    analysis_source = str(comparison.get("analysis_source", "local_fallback"))

    if analysis_source != "gemini":
        logger.info("Using local fallback analysis for resume_id=%s jd_id=%s", resume.id, job_description.id)
        return local_score, analysis_source

    skill_match_score = float(comparison.get("match_score", local_score.skill_match_score))
    matched_skills = list(comparison.get("matched_skills", local_score.matching_skills))
    missing_skills = list(comparison.get("missing_skills", local_score.missing_skills))

    final_score = round(
        (skill_match_score * 0.4)
        + (local_score.experience_score * 0.3)
        + (local_score.education_score * 0.1)
        + (local_score.semantic_score * 0.2),
        2,
    )

    candidate_score = CandidateScore(
        resume_id=local_score.resume_id,
        jd_id=local_score.jd_id,
        final_score=max(0.0, min(final_score, 100.0)),
        matching_skills=matched_skills,
        missing_skills=missing_skills,
        experience_score=local_score.experience_score,
        education_score=local_score.education_score,
        semantic_score=local_score.semantic_score,
        skill_match_score=skill_match_score,
    )

    return candidate_score, analysis_source


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_candidates(payload: AnalysisRequest, db: Session = Depends(get_db)) -> AnalysisResponse:
    resume_query = db.query(Resume)
    jd_query = db.query(JobDescription)

    if payload.resume_id:
        resume_query = resume_query.filter(Resume.id == payload.resume_id)
    if payload.jd_id:
        jd_query = jd_query.filter(JobDescription.id == payload.jd_id)

    resumes = resume_query.all()
    job_descriptions = jd_query.all()

    if not resumes or not job_descriptions:
        raise HTTPException(status_code=404, detail="Resume or job description not found")

    target_jd = job_descriptions[0]
    scored_candidates_with_source = [_build_candidate_score(resume, target_jd) for resume in resumes]
    scored_candidates = [candidate_score for candidate_score, _ in scored_candidates_with_source]
    ranked_candidates = ranking_service.rank(scored_candidates)

    results: list[AnalysisResult] = []

    for candidate in ranked_candidates:
        result = AnalysisResult(
            resume_id=candidate.resume_id,
            jd_id=candidate.jd_id,
            score=candidate.final_score,
            rank=candidate.rank,
            matching_skills=json.dumps(candidate.matching_skills),
            missing_skills=json.dumps(candidate.missing_skills),
            experience_score=candidate.experience_score,
            education_score=candidate.education_score,
            semantic_score=candidate.semantic_score,
        )
        db.add(result)
        results.append(result)

    db.commit()
    for result in results:
        db.refresh(result)

    response_results = [_serialize_analysis_result(result) for result in results]

    used_gemini = any(source == "gemini" for _, source in scored_candidates_with_source)
    message = "Analysis completed with Gemini-assisted scoring" if used_gemini else "Analysis completed with local fallback scoring"

    return AnalysisResponse(message=message, results=response_results)


@router.get("/results", response_model=list[AnalysisResultRead])
def get_results(db: Session = Depends(get_db)) -> list[AnalysisResultRead]:
    results = db.query(AnalysisResult).order_by(AnalysisResult.rank.asc(), AnalysisResult.score.desc()).all()
    return [_serialize_analysis_result(result) for result in results]


@router.get("/results/{result_id}", response_model=AnalysisResultRead)
def get_result(result_id: int, db: Session = Depends(get_db)) -> AnalysisResultRead:
    result = db.get(AnalysisResult, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    return _serialize_analysis_result(result)