import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.job_description import JobDescription
from app.schemas.upload_schema import UploadResponse, UploadedFileInfo
from app.services.jd_parser import jd_parser
from app.services.resume_parser import resume_parser
from app.utils.helpers import build_storage_filename, ensure_upload_directories, read_and_validate_upload_file, validate_upload_extension


router = APIRouter(prefix="/jd", tags=["Job Descriptions"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_job_description(
    title: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    ensure_upload_directories()

    storage_path: Path | None = None

    try:
        validate_upload_extension(file.filename)

        storage_name = build_storage_filename(file.filename or "job-description")
        storage_path = Path(settings.upload_dir) / "jds" / storage_name

        contents = await read_and_validate_upload_file(file)
        storage_path.write_bytes(contents)

        extracted_text = resume_parser.extract_text(str(storage_path))
        parsed_jd = jd_parser.parse(title=title or Path(file.filename or "job-description").stem, text=extracted_text)

        job_description = JobDescription(
            title=parsed_jd["title"],
            jd_text=parsed_jd["full_text"],
        )
        db.add(job_description)
        db.flush()
        db.refresh(job_description)

        uploaded_file = UploadedFileInfo(
            id=job_description.id,
            display_name=job_description.title,
            file_name=file.filename or storage_name,
            file_path=str(storage_path),
            file_size=len(contents),
            content_type=file.content_type,
            created_at=job_description.created_at,
        )
        db.commit()
        logger.info("Uploaded JD file %s", file.filename)

        return UploadResponse(uploaded_files=[uploaded_file])
    except HTTPException:
        db.rollback()
        if storage_path and storage_path.exists():
            storage_path.unlink(missing_ok=True)
        logger.warning("Job description upload rejected")
        raise
    except Exception as exc:
        db.rollback()
        if storage_path and storage_path.exists():
            storage_path.unlink(missing_ok=True)
        logger.exception("Unexpected error while uploading job description")
        raise HTTPException(status_code=500, detail="Failed to upload job description") from exc