import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from app.utils.docx_reader import read_docx_text
from app.utils.pdf_reader import read_pdf_text


SKILL_KEYWORDS = {
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Next.js",
    "Node.js",
    "FastAPI",
    "Django",
    "Flask",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "AWS",
    "Docker",
    "Kubernetes",
    "Git",
    "Tailwind CSS",
    "HTML",
    "CSS",
    "Redux",
    "GraphQL",
    "REST APIs",
    "Figma",
    "Jest",
    "pytest",
}


@dataclass(slots=True)
class ParsedResume:
    name: str
    email: str
    phone_number: str
    skills: list[str]
    education: list[str]
    experience: str
    full_text: str


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_email(text: str) -> str:
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return email_match.group(0) if email_match else ""


def _extract_phone_number(text: str) -> str:
    phone_match = re.search(r"(?:\+?\d{1,3}[\s-]?)?(?:\d{10}|\d{3}[\s-]\d{3}[\s-]\d{4})", text)
    return phone_match.group(0) if phone_match else ""


def _extract_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""

    first_line = lines[0]
    if _extract_email(first_line):
        return ""

    cleaned = re.sub(r"[^A-Za-z\s.']", "", first_line).strip()
    if 2 <= len(cleaned.split()) <= 5:
        return cleaned

    for line in lines[:5]:
        cleaned_line = re.sub(r"[^A-Za-z\s.']", "", line).strip()
        if 2 <= len(cleaned_line.split()) <= 5 and not _extract_email(cleaned_line):
            return cleaned_line

    return ""


def _extract_skills(text: str) -> list[str]:
    found_skills: list[str] = []
    lowered_text = text.lower()

    for skill in SKILL_KEYWORDS:
        if skill.lower() in lowered_text:
            found_skills.append(skill)

    return sorted(set(found_skills), key=found_skills.index)


def _extract_education(text: str) -> list[str]:
    education_patterns = [
        r"(?:Bachelor|Bachelor's|B\.Tech|BTech|BSc|B\.Sc|BCA|BA|Master|Master's|M\.Tech|MTech|MSc|M\.Sc|MBA|PhD)[^\n,.]*",
        r"(?:Education|Academic Background)[:\-]\s*[^\n]+",
    ]
    results: list[str] = []

    for pattern in education_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = _normalize_text(match.group(0))
            if value and value not in results:
                results.append(value)

    return results


def _extract_experience(text: str) -> str:
    experience_patterns = [
        r"(?:\d+(?:\.\d+)?\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience[^\n,.]*)",
        r"(?:Experience|Work Experience|Professional Experience)[:\-]\s*[^\n]+",
    ]

    for pattern in experience_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _normalize_text(match.group(0))

    year_match = re.search(r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\b", text, flags=re.IGNORECASE)
    if year_match:
        return f"{year_match.group(1)} years"

    return ""


class ResumeParser:
    supported_extensions = {".pdf", ".doc", ".docx"}

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return read_pdf_text(path)
        if suffix == ".docx":
            return read_docx_text(path)
        if suffix == ".doc":
            return path.read_text(encoding="utf-8", errors="ignore")

        raise ValueError(f"Unsupported resume format: {suffix}")

    def parse_file(self, file_path: str) -> ParsedResume:
        full_text = self.extract_text(file_path)
        return self.parse_text(full_text)

    def parse_text(self, text: str) -> ParsedResume:
        normalized_text = text.strip()
        return ParsedResume(
            name=_extract_name(normalized_text),
            email=_extract_email(normalized_text),
            phone_number=_extract_phone_number(normalized_text),
            skills=_extract_skills(normalized_text),
            education=_extract_education(normalized_text),
            experience=_extract_experience(normalized_text),
            full_text=normalized_text,
        )

    def parse_resume(self, file_path: str) -> dict[str, Any]:
        parsed_resume = self.parse_file(file_path)
        return {
            "name": parsed_resume.name,
            "email": parsed_resume.email,
            "skills": parsed_resume.skills,
            "education": parsed_resume.education,
            "experience": parsed_resume.experience,
        }


resume_parser = ResumeParser()