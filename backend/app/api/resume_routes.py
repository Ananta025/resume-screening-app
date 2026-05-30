import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.resume import Resume
from app.services.resume_parser import resume_parser
from app.schemas.resume_schema import ResumeFileResponse
from app.schemas.upload_schema import UploadResponse, UploadedFileInfo
from app.utils.helpers import (
    build_candidate_display_name,
    build_storage_filename,
    ensure_upload_directories,
    read_and_validate_upload_file,
    validate_upload_extension,
)


router = APIRouter(prefix="/resumes", tags=["Resumes"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    files: list[UploadFile] = File(...),
    candidate_name: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> UploadResponse:
    ensure_upload_directories()

    if not files:
        raise HTTPException(status_code=400, detail="At least one resume file is required")

    uploaded_files: list[UploadedFileInfo] = []
    stored_paths: list[Path] = []

    try:
        for file in files:
            validate_upload_extension(file.filename, {".pdf", ".docx"})

            storage_name = build_storage_filename(file.filename or "resume")
            storage_path = Path(settings.upload_dir) / "resumes" / storage_name
            contents = await read_and_validate_upload_file(file)
            storage_path.write_bytes(contents)
            stored_paths.append(storage_path)

            try:
                parsed_resume = resume_parser.parse_resume(str(storage_path))
            except Exception as exc:
                logger.exception("Resume parsing failed")
                raise HTTPException(
                    status_code=500,
                    detail=f"Resume parsing failed: {str(exc)}",
                ) from exc

            extracted_text = parsed_resume.get("full_text", "")
            display_name = (
                candidate_name.strip()
                if candidate_name and candidate_name.strip()
                else parsed_resume.get("name") or build_candidate_display_name(file.filename)
            )

            resume = Resume(
                candidate_name=display_name,
                file_name=file.filename or storage_name,
                file_path=str(storage_path),
                extracted_text=extracted_text,
            )
            db.add(resume)
            db.flush()
            db.refresh(resume)

            uploaded_files.append(
                UploadedFileInfo(
                    id=resume.id,
                    display_name=resume.candidate_name,
                    file_name=resume.file_name,
                    file_path=resume.file_path,
                    file_size=len(contents),
                    content_type=file.content_type,
                    created_at=resume.created_at,
                )
            )

        db.commit()
        logger.info("Uploaded %s resume file(s)", len(uploaded_files))

        return UploadResponse(uploaded_files=uploaded_files)
    except HTTPException:
        db.rollback()
        for stored_path in stored_paths:
            if stored_path.exists():
                stored_path.unlink(missing_ok=True)
        logger.warning("Resume upload rejected")
        raise
    except Exception as exc:
        db.rollback()
        for stored_path in stored_paths:
            if stored_path.exists():
                stored_path.unlink(missing_ok=True)
        logger.exception("Unexpected error while uploading resumes")
        raise HTTPException(status_code=500, detail="Failed to upload resume files") from exc


@router.get("/{resume_id}/file", response_model=ResumeFileResponse)
def get_resume_file_url(resume_id: int, request: Request, db: Session = Depends(get_db)) -> ResumeFileResponse:
    logger.info("Resume file URL requested for resume_id=%s", resume_id)
    resume = db.get(Resume, resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    pdf_url = str(request.url_for("get_resume_file_content", resume_id=resume.id))
    return ResumeFileResponse(pdf_url=pdf_url)


@router.get("/{resume_id}/file/content", name="get_resume_file_content")
def get_resume_file_content(resume_id: int, db: Session = Depends(get_db)) -> FileResponse:
    logger.info("Resume file content requested for resume_id=%s", resume_id)
    resume = db.get(Resume, resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = Path(resume.file_path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Resume file not found")

    media_type = "application/pdf"
    suffix = file_path.suffix.lower()
    if suffix == ".docx":
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif suffix == ".doc":
        media_type = "application/msword"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{resume.file_name}"'},
    )