from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_UPLOAD_SIZE_BYTES = settings.max_upload_size_bytes


def ensure_upload_directories() -> None:
    Path(settings.upload_dir, "resumes").mkdir(parents=True, exist_ok=True)
    Path(settings.upload_dir, "jds").mkdir(parents=True, exist_ok=True)


def build_storage_filename(original_filename: str) -> str:
    safe_name = Path(original_filename).name
    return f"{uuid4().hex}_{safe_name}"


def json_list_to_string(items: list[str]) -> str:
    return str(items)


def get_file_extension(filename: str | None) -> str:
    return Path(filename or "").suffix.lower()


def validate_upload_extension(filename: str | None, allowed_extensions: set[str] | None = None) -> None:
    extension = get_file_extension(filename)
    if extension not in (allowed_extensions or ALLOWED_UPLOAD_EXTENSIONS):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension or 'unknown'}")


async def read_and_validate_upload_file(upload_file: UploadFile) -> bytes:
    contents = await upload_file.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
    return contents


def ensure_supported_upload(filename: str | None) -> None:
    validate_upload_extension(filename)


def build_candidate_display_name(filename: str | None) -> str:
    return Path(filename or "candidate").stem.replace("_", " ").strip() or "candidate"