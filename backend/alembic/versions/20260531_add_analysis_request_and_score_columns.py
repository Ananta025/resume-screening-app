"""add analysis request tracking and score columns

Revision ID: 20260531_add_analysis_request_and_score_columns
Revises: 
Create Date: 2026-05-31 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260531_add_analysis_request_and_score_columns"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analysis_results", sa.Column("analysis_request_id", sa.String(length=64), nullable=True))
    op.add_column("analysis_results", sa.Column("skills_score", sa.Numeric(5, 2), nullable=False, server_default="0"))
    op.create_index(op.f("ix_analysis_results_analysis_request_id"), "analysis_results", ["analysis_request_id"], unique=False)
    op.create_unique_constraint("uq_analysis_results_resume_jd", "analysis_results", ["resume_id", "jd_id"])
    op.create_unique_constraint(
        "uq_analysis_results_request_resume_jd",
        "analysis_results",
        ["analysis_request_id", "resume_id", "jd_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_analysis_results_request_resume_jd", "analysis_results", type_="unique")
    op.drop_constraint("uq_analysis_results_resume_jd", "analysis_results", type_="unique")
    op.drop_index(op.f("ix_analysis_results_analysis_request_id"), table_name="analysis_results")
    op.drop_column("analysis_results", "skills_score")
    op.drop_column("analysis_results", "analysis_request_id")
