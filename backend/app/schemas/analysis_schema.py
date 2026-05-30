from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRequest(BaseModel):
    resume_id: int | None = Field(default=None, ge=1)
    jd_id: int | None = Field(default=None, ge=1)


class AnalysisResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    jd_id: int
    score: float
    final_score: float
    rank: int
    matching_skills: list[str]
    missing_skills: list[str]
    experience_score: float
    education_score: float
    semantic_score: float
    created_at: datetime


class AnalysisResponse(BaseModel):
    message: str
    results: list[AnalysisResultRead]


class ExportResponse(BaseModel):
    file_name: str
    download_url: str