from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadedFileInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    file_name: str
    file_path: str
    file_size: int
    content_type: str | None = None
    created_at: datetime


class UploadResponse(BaseModel):
    success: bool = True
    uploaded_files: list[UploadedFileInfo]