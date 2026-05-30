from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis_result import AnalysisResult
from app.services.export_service import export_service


router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db)) -> PlainTextResponse:
    results = db.query(AnalysisResult).order_by(AnalysisResult.rank.asc(), AnalysisResult.score.desc()).all()
    csv_content = export_service.to_csv(results)
    return PlainTextResponse(csv_content, media_type="text/csv")