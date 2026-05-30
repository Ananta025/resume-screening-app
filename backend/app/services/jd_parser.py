import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


STOPWORDS = {
    "a",
    "about",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "this",
    "to",
    "we",
    "will",
    "with",
    "you",
    "your",
}


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
    "Machine Learning",
    "NLP",
    "Excel",
    "Power BI",
    "Tableau",
}


EDUCATION_PATTERNS = [
    r"(?:Bachelor|Bachelor's|B\.Tech|BTech|B\.Sc|BSc|BCA|B\.A|BA|Master|Master's|M\.Tech|MTech|M\.Sc|MSc|MBA|PhD)[^\n,.;:]*",
    r"(?:Education|Academic Qualification|Qualifications)[:\-]\s*[^\n]+",
]


EXPERIENCE_PATTERNS = [
    r"(?:\d+(?:\.\d+)?\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience[^\n,.;:]*)",
    r"(?:Experience|Work Experience|Professional Experience|Relevant Experience)[:\-]\s*[^\n]+",
    r"(?:minimum|min\.?|at least)\s*\d+(?:\.\d+)?\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience[^\n,.;:]*",
]


@dataclass(slots=True)
class ParsedJD:
    required_skills: list[str]
    required_experience: str
    required_education: list[str]
    keywords: list[str]
    full_text: str


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_required_skills(text: str) -> list[str]:
    lowered_text = text.lower()
    found_skills: list[str] = []

    for skill in SKILL_KEYWORDS:
        if skill.lower() in lowered_text:
            found_skills.append(skill)

    return sorted(set(found_skills), key=found_skills.index)


def _extract_required_experience(text: str) -> str:
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _normalize_text(match.group(0))

    year_match = re.search(r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\b", text, flags=re.IGNORECASE)
    if year_match:
        return f"{year_match.group(1)} years"

    return ""


def _extract_required_education(text: str) -> list[str]:
    results: list[str] = []

    for pattern in EDUCATION_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = _normalize_text(match.group(0))
            if value and value not in results:
                results.append(value)

    return results


def _extract_keywords(text: str, max_keywords: int = 12) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}", text.lower())
    counts = Counter(token for token in tokens if token not in STOPWORDS and len(token) > 2)
    keywords: list[str] = []

    for skill in _extract_required_skills(text):
        normalized_skill = skill.lower()
        if normalized_skill not in keywords:
            keywords.append(normalized_skill)

    for token, _ in counts.most_common():
        if token not in keywords:
            keywords.append(token)
        if len(keywords) >= max_keywords:
            break

    return keywords[:max_keywords]


class JDParser:
    def parse_text(self, text: str) -> ParsedJD:
        normalized_text = text.strip()
        return ParsedJD(
            required_skills=_extract_required_skills(normalized_text),
            required_experience=_extract_required_experience(normalized_text),
            required_education=_extract_required_education(normalized_text),
            keywords=_extract_keywords(normalized_text),
            full_text=normalized_text,
        )

    def parse(self, title: str, text: str) -> dict[str, Any]:
        parsed_jd = self.parse_text(text)
        return {
            "title": title.strip(),
            "required_skills": parsed_jd.required_skills,
            "required_experience": parsed_jd.required_experience,
            "required_education": parsed_jd.required_education,
            "keywords": parsed_jd.keywords,
            "full_text": parsed_jd.full_text,
        }


jd_parser = JDParser()