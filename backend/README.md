# Resume Screening System Backend

FastAPI backend scaffold for an AI resume screening and candidate ranking system.

## Included

- FastAPI app with CORS, health check, logging, and exception handling
- PostgreSQL-ready SQLAlchemy models
- Alembic migration scaffold
- File upload routes for resumes and job descriptions
- Analysis and export route skeletons
- Parser and service layer stubs for future AI integration

## Local Setup

1. Create a virtual environment with Python 3.12.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment settings:

```bash
cp .env.example .env
```

4. Run the API:

```bash
uvicorn app.main:app --reload
```

## Notes

- `PDF` and `DOCX` parsing are supported through `PyMuPDF` and `python-docx`.
- `.doc` uploads are accepted and routed through a fallback text reader until a dedicated converter is added.
- Gemini integration is isolated in `app/services/gemini_service.py` and reads its API key from the environment.