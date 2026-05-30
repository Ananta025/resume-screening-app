from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    __table_args__ = (
        UniqueConstraint("resume_id", "jd_id", name="uq_analysis_results_resume_jd"),
        UniqueConstraint("analysis_request_id", "resume_id", "jd_id", name="uq_analysis_results_request_resume_jd"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    jd_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skills_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    matching_skills: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    missing_skills: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    experience_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    education_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    semantic_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    resume = relationship("Resume", back_populates="analysis_results")
    job_description = relationship("JobDescription", back_populates="analysis_results")