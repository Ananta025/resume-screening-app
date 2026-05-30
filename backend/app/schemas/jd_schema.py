from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    jd_text: str = Field(min_length=1)


class JobDescriptionRead(JobDescriptionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class JDUploadResponse(JobDescriptionRead):
    message: str = "Job description uploaded successfully"