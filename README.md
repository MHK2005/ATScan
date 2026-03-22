# ATScan — ATS Resume Analyzer & Builder

## What is ATScan?

Most job applications today go through an ATS before a human ever sees them. ATS stands for Applicant Tracking System, and it is software that companies use to scan resumes automatically. It looks for specific keywords, section headings, and clean formatting. If your resume does not pass, it gets filtered out — no callback, no explanation.

ATScan is a Python desktop application that gives you two tools in one: an ATS resume analyzer and an ATS-friendly resume builder. You can either check an existing resume and see exactly what is wrong, or build a new one from scratch that comes out formatted and scored correctly right away. It runs completely offline, requires no paid APIs, and supports `.txt`, `.pdf`, and `.docx` resume files.


## Features

**Analyze Resume** — drop in any resume file and get an ATS score out of 100 with a full breakdown across five categories and specific feedback on what to fix.

**Build Resume** — enter your details in plain text, however you want, and the tool figures out the structure automatically. It generates a properly formatted `.docx` resume, injects any missing ATS keywords, and shows you the score of the generated file immediately.


## How the Analyzer Works

The score is split across five categories. Sections are worth 30 points because having clearly labeled headings like Summary, Experience, Education, and Skills is the single most important thing an ATS looks for. Keywords are worth 25 points, checked against a list of 24 common ATS terms like "teamwork", "Python", "data analysis", and "agile". Action verbs are worth 20 points, checked against 30 strong verbs like "managed", "built", "led", and "delivered". Word count is worth 15 points, with the ideal range being 300 to 800 words. Formatting is worth the remaining 10 points, checking for a valid email, a phone number, and the absence of special symbols like stars and arrows that ATS systems often cannot read correctly.


## Project Files

**`project.py`** is the main file. It contains the `main()` function which launches the GUI, plus four core functions: `extract_text()`, `check_sections()`, `score_resume()`, and `build_resume()`.

`extract_text()` takes a file path and returns the plain text content of the resume. It handles `.txt` files with Python's built-in file reader, `.pdf` files using `pdfplumber`, and `.docx` files using `python-docx`. If the file does not exist or uses an unsupported format, it raises a descriptive error.

`check_sections()` takes the resume text and checks whether each of the four required sections is present using regex patterns rather than exact string matching. It catches variations — for example it accepts "objective", "profile", and "about me" in addition to "summary". It returns a dictionary mapping each section name to True or False.

`score_resume()` is the core of the analyzer. It calls `check_sections()` and runs four more checks independently, then returns a dictionary with the total score, a breakdown by category, and a list of feedback messages.

`build_resume()` takes a dictionary of user details, passes each field through the smart parser, builds a properly formatted `.docx` document using `python-docx`, and returns the file path along with its ATS score.

**`parser.py`** is the smart input parser. It contains five functions — `parse_experience()`, `parse_education()`, `parse_projects()`, `parse_certifications()`, and `parse_skills()` — that accept free-form text in any format and extract structured data from it. For example `parse_experience()` uses date pattern detection and action verb recognition to figure out which line is a job title, which is a company name, and which are bullet points, regardless of how the user typed them. This means the builder imposes no strict format on the user.

**`gui.py`** is the desktop interface built with `customtkinter`. It has two tabs: Analyze and Build. The Analyze tab has a file picker and displays results with color-coded progress bars and feedback. The Build tab has plain text input fields for every resume section with no format restrictions. All file operations run on a background thread so the UI never freezes.

**`constants.py`** holds all the fixed data: regex patterns for section detection, the ATS keywords list, the action verbs list, and patterns for email, phone, and special character detection. Keeping these separate from the logic in `project.py` means anyone can add new keywords or verbs by editing one file without touching the scoring code.

**`test_project.py`** contains 9 pytest tests covering all core functions. The `extract_text` tests cover reading a `.txt` file, rejecting unsupported formats, and handling missing files. The `check_sections` tests use a strong and weak sample resume to verify detection works correctly. The `score_resume` tests verify scoring accuracy. The `build_resume` tests verify that the output file is created, scores well, and injects keywords when the input has none.

**`requirements.txt`** lists all pip dependencies.


## Design Choices

The scoring thresholds are intentionally lenient. Full marks for keywords require 8 out of 24 found, which is one third of the list. Full marks for action verbs require 6 out of 30. A resume does not need to hit every possible keyword — it just needs enough to signal relevance to an ATS system.

The section detection uses flexible regex patterns because people label sections differently. "Work History", "Professional Experience", and "Employment" all mean the same thing to a human, and the patterns in `constants.py` catch all of them.

The parser in `parser.py` was added so the builder does not force users into a rigid input format. It detects dates, degree keywords, institution names, and action verbs to infer structure from whatever text is given.

The GUI was built with `customtkinter` because it is pure Python, produces a modern dark-themed interface, and compiles cleanly to a standalone `.exe` using PyInstaller.


## How to Run

Install dependencies:

```
pip install -r requirements.txt
```

Run the app:

```
python project.py
```


## Download

A prebuilt Windows `.exe` is available in [Releases](../../releases). Download `ATScan.zip`, extract it, and run `ATScan.exe`.