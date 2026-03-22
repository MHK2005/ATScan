import os
import pytest
from project import extract_text, check_sections, score_resume, build_resume


STRONG_RESUME = """
John Doe
john.doe@email.com | +1-555-123-4567

SUMMARY
Experienced software engineer with strong analytical and problem solving skills.
Passionate about collaboration, leadership, and strategic planning.

EXPERIENCE
Software Engineer at TechCorp (2020-2024)
Managed a team of 5 developers and led the development of a new payment system.
Implemented agile and scrum workflows that improved delivery time by 30 percent.
Developed and optimized data analysis pipelines using Python and SQL.
Collaborated with cross-functional teams to deliver customer service solutions.
Built and launched internal tools that reduced manual work by 40 percent.
Coordinated project management efforts across multiple departments.

EDUCATION
Bachelor of Science in Computer Science
State University, 2020

SKILLS
Python, SQL, Excel, Java, Agile, Scrum, Microsoft Office,
teamwork, communication, leadership, time management,
data analysis, research, presentation, negotiation
"""


WEAK_RESUME = """
I worked at a company for a few years doing some stuff.
It was okay. I learned things and did tasks.
The job was in an office downtown.
"""


# extract_text Tests

def test_extract_text_txt(tmp_path):
    txt_file = tmp_path / "resume.txt"
    txt_file.write_text("Hello World")
    assert extract_text(str(txt_file)) == "Hello World"


def test_extract_text_invalid_extension(tmp_path):
    bad_file = tmp_path / "resume.csv"
    bad_file.write_text("data")
    with pytest.raises(ValueError):
        extract_text(str(bad_file))


def test_extract_text_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_text("nonexistent_file.txt")


# check_sections Tests

def test_check_sections_all_present():
    sections = check_sections(STRONG_RESUME)
    assert sections["summary"] is True
    assert sections["experience"] is True
    assert sections["education"] is True
    assert sections["skills"] is True


def test_check_sections_missing():
    sections = check_sections(WEAK_RESUME)
    assert sections["summary"] is False
    assert sections["experience"] is False
    assert sections["education"] is False
    assert sections["skills"] is False


# score_resume Tests

def test_score_resume_high():
    result = score_resume(STRONG_RESUME)
    assert result["total_score"] >= 70


def test_score_resume_low():
    result = score_resume(WEAK_RESUME)
    assert result["total_score"] <= 30


# build_resume Tests

def test_build_resume(tmp_path):
    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+1-555-999-8888",
        "summary": "Experienced professional with strong communication and teamwork skills.",
        "skills": "Python, Excel, Leadership",
        "experience": "Led a team of engineers at TechCorp\nDelivered key projects on time",
        "education": "Bachelor of Science, MIT, 2022",
    }
    result = build_resume(data, output_dir=str(tmp_path))
    assert result["score_result"]["total_score"] >= 70
    assert os.path.isfile(result["filepath"])
    assert result["filename"].endswith(".docx")


def test_build_resume_injects_keywords(tmp_path):
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "phone": "+1-555-000-0000",
        "summary": "A professional.",
        "skills": "",
        "experience": "Did work at a company for several years",
        "education": "University degree, 2020",
    }
    result = build_resume(data, output_dir=str(tmp_path))
    text = extract_text(result["filepath"]).lower()
    from constants import ATS_KEYWORDS
    found = sum(1 for k in ATS_KEYWORDS if k in text)
    assert found >= 5


