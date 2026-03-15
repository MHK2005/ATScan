import re, sys, os, pdfplumber
from docx import Document
from constants import (
    REQUIRED_SECTIONS,
    ATS_KEYWORDS,
    ACTION_VERBS,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    SPECIAL_CHARS_PATTERN,
)


def main():
    while True:
        print("1. Analyze resume")
        print("2. Exit\n")

        choice = input("Enter your choice (1/2): ").strip()

        if choice == "1":
            filepath = input("\nEnter the path to your resume file: ").strip("\"'\\ ")
            try:
                text = extract_text(filepath)
            except (FileNotFoundError, ValueError) as e:
                print(f"\nError: {e}\n")
                continue
            if not text.strip():
                print("\nError: The file appears to be empty.\n")
                continue

            result = score_resume(text)
            score = result["total_score"]

            print(f"\n{'─' * 50}")
            print(f"ATS SCORE: {score} / 100")
            print(f"{'─' * 50}\n")

            breakdown = result["breakdown"]
            print("Score Breakdown:")
            print(f"  Sections Present: {breakdown['sections']} / 30")
            print(f"  ATS Keywords: {breakdown['keywords']} / 25")
            print(f"  Action Verbs: {breakdown['action_verbs']} / 20")
            print(f"  Word Count: {breakdown['word_count']} / 15")
            print(f"  Formatting: {breakdown['formatting']} / 10")

            print("\nFeedback:")
            for line in result["feedback"]:
                print(f"  {line}")
            print()

        elif choice == "2":
            print("\nExiting...\n")
            sys.exit(0)

        else:
            print("\nInvalid choice.\n")


def extract_text(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        with open(filepath, "r") as f:
            return f.read()

    elif ext == ".pdf":
        with pdfplumber.open(filepath) as pdf:
            pages = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
            return "\n".join(pages)

    elif ext == ".docx":
        with open(filepath, "rb") as f:
            doc = Document(f)
            return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"Unsupported file type: '{ext}'. Use (.txt / .pdf / .docx)")


def check_sections(text):
    results = {}
    for section_name, pattern in REQUIRED_SECTIONS.items():
        results[section_name] = bool(re.search(pattern, text.lower()))
    return results


def score_resume(text):
    feedback = []
    word_count = len(text.split())

    # Sections (30 points)
    sections = check_sections(text)
    sections_found = sum(sections.values())
    sections_score = int((sections_found / len(REQUIRED_SECTIONS)) * 30)
    missing_sections = [name.title() for name, found in sections.items() if not found]
    if missing_sections:
        feedback.append(f"Missing sections: {', '.join(missing_sections)}")
    else:
        feedback.append("All key sections found")

    # Keywords (25 points)
    keywords_found = [k for k in ATS_KEYWORDS if k in text.lower()]
    keywords_score = int(min(len(keywords_found) / 8, 1.0) * 25)
    feedback.append(f"{len(keywords_found)} ATS keywords found")

    # Action Verbs (20 points)
    found_verbs = [v for v in ACTION_VERBS if v in text.lower()]
    verbs_score = int(min(len(found_verbs) / 6, 1.0) * 20)
    feedback.append(f"{len(found_verbs)} action verbs found")

    # Word Count (15 points)
    if 300 <= word_count <= 800:
        word_count_score = 15
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        word_count_score = 10
    else:
        word_count_score = 5
    feedback.append(f"Word count: {word_count} (best: 300-800)")

    # Formatting (10 points)
    formatting_score = 0

    if re.search(EMAIL_PATTERN, text):
        formatting_score += 4
        feedback.append("Email found")
    else:
        feedback.append("No email found")

    if re.search(PHONE_PATTERN, text):
        formatting_score += 3
        feedback.append("Phone number found")
    else:
        feedback.append("No phone number found")

    if not re.findall(SPECIAL_CHARS_PATTERN, text):
        formatting_score += 3
        feedback.append("Clean formatting")
    else:
        feedback.append("Special symbols found that may confuse ATS")

    total_score = sections_score + keywords_score + verbs_score + word_count_score + formatting_score

    return {
        "total_score": total_score,
        "breakdown": {
            "sections": sections_score,
            "keywords": keywords_score,
            "action_verbs": verbs_score,
            "word_count": word_count_score,
            "formatting": formatting_score,
        },
        "feedback": feedback,
    }


if __name__ == "__main__":
    main()

