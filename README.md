# ATScan - Resume Analyzer
#### Video Demo: https://youtu.be/XozKlDLyTB8

## What is ATScan?

Most job applications today go through an ATS before a human ever sees them. ATS stands for Applicant Tracking System, and it is software that companies use to scan resumes automatically. It looks for specific keywords, section headings, and clean formatting. If your resume does not pass, it gets filtered out.

ATScan is a Python tool that lets you run that same kind of check on your own resume before you apply anywhere. You provide it a resume file, and it gives you a score out of 100 with a full breakdown and feedback on what is missing or needs work. It supports `.txt`, `.pdf`, and `.docx` files.


## How It Works

When you run the program, a simple menu appears with two options: analyze a resume or exit. If you choose to analyze, you provide the file path to your resume. The program reads it, runs it through the scoring logic, and prints your ATS score, a category breakdown, and a list of feedback points.

The score is split across five categories. Sections are worth 30 points because having clearly labeled headings like Summary, Experience, Education, and Skills is the single most important thing an ATS looks for. Keywords are worth 25 points, checked against a list of 24 common ATS terms like "teamwork", "Python", "data analysis", and "agile". Action verbs are worth 20 points, checked against 30 strong verbs like "managed", "built", "led", and "delivered". Word count is worth 15 points, with the ideal range being 300 to 800 words. Formatting is worth the remaining 10 points, checking for a valid email, a phone number, and the absence of special symbols like stars and arrows that ATS systems often cannot read correctly.


## Project Files

**`project.py`** is the main file. It contains the `main()` function and three additional functions: `extract_text()`, `check_sections()`, and `score_resume()`.

`extract_text()` takes a file path and returns the plain text content of the resume. It handles .txt files with Python's built-in file reader, .pdf files using the `pdfplumber` library, and .docx files using `python-docx`. If the file does not exist or uses an unsupported format, it raises an error so the user knows exactly what went wrong.

`check_sections()` takes the resume text and checks whether each of the four required sections is present. It uses regex patterns rather than exact string matching, so it catches variations. For example, it does not just look for "summary" but also accepts "objective", "profile", and "about me". It returns a dictionary mapping each section name to True or False.

`score_resume()` is the core of the project. It calls `check_sections()` and then runs four more checks independently. It returns a dictionary with the total score, a breakdown by category, and a list of feedback messages.

**`constants.py`** holds all the fixed data the program needs: the regex patterns for each section, the ATS keywords list, the action verbs list, and the regex patterns for email, phone, and special characters. Mixing long lists of strings into the middle of scoring logic makes the code harder to read and harder to update. If someone wants to add more keywords or action verbs later, they only need to open `constants.py` and add to the list without touching the logic in `project.py`.

**`test_project.py`** contains 7 pytest tests covering all three testable functions. The `extract_text` tests check that it reads a .txt file correctly, raises a `ValueError` for unsupported file types, and raises a `FileNotFoundError` for missing files. The `check_sections` tests use a strong sample resume and a weak one to verify that sections are correctly detected as present or absent. The `score_resume` tests verify that a well-written resume scores at least 70 and that a poorly written one scores no more than 30.

**`requirements.txt`** lists the three pip libraries the project depends on: `pdfplumber`, `python-docx` and `pytest`


## Design Choices

One decision worth explaining is why the scoring thresholds are set the way they are. For keywords, full score require 8 out of 24 keywords found. That is one third of the list, which felt like a fair target. A resume does not need every possible keyword, but it should have a reasonable number of relevant ones. For action verbs, full marks require 6 out of 30, which is also roughly one fifth of the list. The idea is that a resume with at least 6 strong action verbs reads noticeably better than one without.

The section detection uses flexible regex patterns on purpose. People label resume sections differently. "Work History", "Professional Experience", and "Employment" all mean the same thing to a human reader, and the patterns in `constants.py` are written to catch all of them. Requiring exact matches would have caused false negatives on resumes that are otherwise well formatted.


## How to Run

Install dependencies:

```
pip install -r requirements.txt
```

Run the program:

```
python project.py
```

Run the tests:

```
pytest test_project.py
```
