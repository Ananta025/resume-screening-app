from dataclasses import dataclass


@dataclass(slots=True)
class CandidateProfile:
    name: str
    resume_id: int | None = None