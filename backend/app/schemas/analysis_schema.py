from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRequest(BaseModel):
    resume_id: int | None = Field(default=None, ge=1)
    jd_id: int | None = Field(default=None, ge=1)
    analysis_request_id: str | None = Field(default=None, min_length=8, max_length=64)


class ScoreBreakdownRead(BaseModel):
    skills_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    final_score: float


class AnalysisResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    jd_id: int
    analysis_request_id: str | None = None
    score: float
    final_score: float
    rank: int
    skills_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    experience_score: float
    education_score: float
    semantic_score: float
    score_breakdown: ScoreBreakdownRead
    created_at: datetime


class AnalysisResponse(BaseModel):
    message: str
    results: list[AnalysisResultRead]


class ExportResponse(BaseModel):
    file_name: str
    download_url: str