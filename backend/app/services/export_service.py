import csv
import io
from collections.abc import Iterable

from app.models.analysis_result import AnalysisResult


class ExportService:
    def to_csv(self, results: Iterable[AnalysisResult]) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "id",
            "resume_id",
            "jd_id",
            "score",
            "rank",
            "matching_skills",
            "missing_skills",
            "experience_score",
            "education_score",
            "semantic_score",
            "created_at",
        ])

        for result in results:
            writer.writerow([
                result.id,
                result.resume_id,
                result.jd_id,
                result.score,
                result.rank,
                result.matching_skills,
                result.missing_skills,
                result.experience_score,
                result.education_score,
                result.semantic_score,
                result.created_at.isoformat() if result.created_at else "",
            ])

        return buffer.getvalue()


export_service = ExportService()