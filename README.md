# Resume Screening & Candidate Ranking System

A full-stack application for screening resumes against a job description, ranking candidates, previewing resumes, and exporting results.

## Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy

### AI
- Gemini API

## Features
- Multi resume upload
- Job description upload
- AI resume analysis
- Candidate scoring
- Candidate ranking
- Resume preview
- CSV export

## Project Structure
- `frontend/` - Next.js client application
- `backend/` - FastAPI server and database models

## Setup

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables

Backend:
```env
DATABASE_URL=
GEMINI_API_KEY=
```

Frontend:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Scoring Method
- Skills Match = 40%
- Experience Match = 30%
- Education Match = 10%
- Semantic Similarity = 20%
- Final Score = Weighted Sum

## Deployment
- Frontend: Vercel
- Backend: Render
- Database: Neon PostgreSQL

## Notes
- The backend stores uploaded resumes and job descriptions on disk and in the database.
- Resume preview uses the stored resume file served from the backend.
- Make sure the upload directories exist in deployment or are created at startup.
