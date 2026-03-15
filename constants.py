REQUIRED_SECTIONS = {
    "summary": r"\b(summary|objective|profile|about\s*me)\b",
    "experience": r"\b(experience|work\s*history|employment|professional\s*experience)\b",
    "education": r"\b(education|academic|qualifications|certifications?)\b",
    "skills": r"\b(skills|technical\s*skills|competencies|proficiencies)\b",
}

ATS_KEYWORDS = [
    "teamwork", "communication", "leadership", "problem solving",
    "project management", "analytical", "detail oriented",
    "time management", "collaboration", "critical thinking",
    "data analysis", "strategic planning", "customer service",
    "presentation", "negotiation", "research", "microsoft office",
    "python", "java", "sql", "excel", "agile", "scrum",
]

ACTION_VERBS = [
    "managed", "developed", "implemented", "designed", "created",
    "led", "coordinated", "achieved", "improved", "increased",
    "reduced", "delivered", "organized", "analyzed", "built",
    "launched", "established", "trained", "supervised", "resolved",
    "streamlined", "optimized", "executed", "maintained", "generated",
    "negotiated", "collaborated", "presented", "initiated", "transformed",
]

EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(\+?\d[\d\s\-().]{7,}\d)"
SPECIAL_CHARS_PATTERN = r"[★●◆■►▸◦‣⁃✦✧]"

