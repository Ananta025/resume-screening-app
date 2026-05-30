# API Documentation

All backend endpoints are served under the FastAPI prefix configured in `API_V1_PREFIX`, which defaults to `/api`.

## Common Conventions

- Request bodies are JSON unless the route accepts `multipart/form-data`.
- Upload routes accept files and may also accept optional text fields.
- Error responses return a JSON object with `detail` and `message` keys.

## Health

### `GET /health`
Returns service health information.

Response:
```json
{
  "status": "ok",
  "service": "Resume Screening System"
}
```

## Resume Endpoints

### `POST /api/resumes/upload`
Uploads one or more resume files.

Request type: `multipart/form-data`

Fields:
- `files` - one or more PDF/DOCX files
- `candidate_name` - optional display name override

Response:
```json
{
  "success": true,
  "uploaded_files": [
    {
      "id": 1,
      "display_name": "Jane Doe",
      "file_name": "jane_doe.pdf",
      "file_path": "uploads/resumes/....pdf",
      "file_size": 12345,
      "content_type": "application/pdf",
      "created_at": "2026-05-31T10:00:00"
    }
  ]
}
```

### `GET /api/resumes/{resume_id}/file`
Returns the backend URL used by the frontend to preview the stored file.

Response:
```json
{
  "pdf_url": "http://localhost:8000/api/resumes/1/file/content"
}
```

### `GET /api/resumes/{resume_id}/file/content`
Streams the stored resume file inline so browsers can preview PDFs in an iframe.

## Job Description Endpoints

### `POST /api/jd/upload`
Uploads a job description file.

Request type: `multipart/form-data`

Fields:
- `file` - JD file
- `title` - optional title override

Response:
```json
{
  "success": true,
  "uploaded_files": [
    {
      "id": 1,
      "display_name": "Senior Frontend Engineer",
      "file_name": "job-description.docx",
      "file_path": "uploads/jds/....docx",
      "file_size": 12000,
      "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "created_at": "2026-05-31T10:00:00"
    }
  ]
}
```

## Analysis Endpoints

### `POST /api/analyze`
Runs candidate scoring and ranking.

Request body:
```json
{
  "resume_id": 1,
  "jd_id": 1,
  "analysis_request_id": "analysis-uuid-or-random-id"
}
```

Notes:
- `resume_id` and `jd_id` are optional filters.
- If omitted, the backend analyzes all resumes against the selected JD.
- `analysis_request_id` is used to prevent duplicate Gemini calls and duplicate DB writes.

Response:
```json
{
  "message": "Analysis completed with local fallback scoring",
  "results": [
    {
      "id": 10,
      "resume_id": 1,
      "jd_id": 1,
      "analysis_request_id": "...",
      "score": 83,
      "final_score": 83,
      "rank": 1,
      "skills_score": 35,
      "matching_skills": ["React", "TypeScript"],
      "missing_skills": ["AWS"],
      "experience_score": 20,
      "education_score": 10,
      "semantic_score": 18,
      "score_breakdown": {
        "skills_score": 35,
        "experience_score": 20,
        "education_score": 10,
        "semantic_score": 18,
        "final_score": 83
      },
      "created_at": "2026-05-31T10:00:00"
    }
  ]
}
```

### `GET /api/results`
Returns all analysis results ordered by rank and score.

### `GET /api/results/{result_id}`
Returns a single analysis result by ID.

## Export Endpoints

### `GET /api/export/csv`
Exports ranked results as CSV text.

Response type: `text/csv`

## Frontend Usage Notes

- The frontend stores the latest upload context in session storage.
- The results page deduplicates rows by `resume_id` before rendering.
- The analysis flow disables the Analyze button while a request is in progress.
