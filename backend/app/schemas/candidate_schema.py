from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateBase(BaseModel):
    name: str


class CandidateCreate(CandidateBase):
    pass


class CandidateRead(CandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime