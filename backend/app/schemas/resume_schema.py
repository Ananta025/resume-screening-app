from pydantic import BaseModel


class ResumeFileResponse(BaseModel):
    pdf_url: str