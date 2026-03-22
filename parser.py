import re

DATE_PATTERN = re.compile(
    r"\b("
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\-\.]*\d{2,4}"
    r"|\d{1,2}[\/\-]\d{2,4}"
    r"|\d{4}\s*[\-–—to]+\s*(\d{4}|present|now|current)"
    r"|\d{4}"
    r")\b",
    re.IGNORECASE,
)

DEGREE_WORDS = re.compile(
    r"\b(bachelor|master|phd|doctor|associate|b\.?s|m\.?s|b\.?e|m\.?e|"
    r"b\.?sc|m\.?sc|b\.?tech|m\.?tech|mba|bba|bs|ms|ba|ma|hnd|diploma|degree)\b",
    re.IGNORECASE,
)

INSTITUTION_WORDS = re.compile(
    r"\b(university|college|institute|school|academy|faculty|polytechnic|"
    r"ned|mit|harvard|stanford|cambridge|oxford)\b",
    re.IGNORECASE,
)

BULLET_PREFIXES = re.compile(r"^[\-\•\*\>\◦\–\—\▪\▸\►]+\s*")

ACTION_VERB_STARTS = re.compile(
    r"^(managed|developed|implemented|designed|created|led|coordinated|"
    r"achieved|improved|increased|reduced|delivered|organized|analyzed|"
    r"built|launched|established|trained|supervised|resolved|streamlined|"
    r"optimized|executed|maintained|generated|negotiated|collaborated|"
    r"presented|initiated|transformed|completed|supported|participated|"
    r"contributed|assisted|worked|used|applied|researched|wrote|tested|"
    r"deployed|configured|integrated|automated|monitored|reviewed|helped|"
    r"volunteered|toured|reached|earned|achieved)\b",
    re.IGNORECASE,
)


def clean_line(line):
    line = BULLET_PREFIXES.sub("", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def has_date(line):
    return bool(DATE_PATTERN.search(line))


def looks_like_bullet(line):
    return bool(BULLET_PREFIXES.match(line)) or bool(ACTION_VERB_STARTS.match(line))


def is_long_sentence(line):
    return len(line.split()) > 10


def split_date_from_line(line):
    match = re.search(
        r"[\|\-–—,]?\s*("
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\.\-]*\d{2,4}"
        r"[\s\-–—to]*"
        r"((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\.\-]*\d{2,4}|present|now|current)?"
        r"|\d{4}\s*[\-–—to]+\s*(\d{4}|present|now|current)"
        r"|\d{4}"
        r")\s*$",
        line,
        re.IGNORECASE,
    )
    if match:
        date_part = match.group(1).strip()
        main_part = line[:match.start()].strip().strip("|–—-,").strip()
        return main_part, date_part
    return line.strip(), ""


def parse_experience(raw_text):
    if not raw_text.strip():
        return []

    raw_blocks = re.split(r"\n\s*\n", raw_text.strip())
    if len(raw_blocks) == 1:
        raw_blocks = re.split(r"\n(?=[A-Z][^\n]{2,40}$)", raw_text.strip(), flags=re.MULTILINE)

    jobs = []

    for block in raw_blocks:
        lines = [clean_line(l) for l in block.strip().split("\n") if clean_line(l)]
        if not lines:
            continue

        job = {"title": "", "company": "", "date": "", "bullets": []}

        date_line_index = None
        for i, line in enumerate(lines):
            if has_date(line) and i <= 2:
                date_line_index = i
                break

        if date_line_index is not None and date_line_index == 0:
            main_part, date_part = split_date_from_line(lines[0])
            if "|" in main_part or "," in main_part:
                parts = re.split(r"[|,]", main_part, maxsplit=1)
                job["title"] = parts[0].strip()
                job["company"] = parts[1].strip() if len(parts) > 1 else ""
            else:
                job["title"] = main_part
            job["date"] = date_part
            bullet_start = 1

        elif date_line_index == 1:
            job["title"] = lines[0]
            main_part, date_part = split_date_from_line(lines[1])
            job["company"] = main_part
            job["date"] = date_part
            bullet_start = 2

        elif date_line_index == 2:
            job["title"] = lines[0]
            job["company"] = lines[1]
            main_part, date_part = split_date_from_line(lines[2])
            if not job["company"]:
                job["company"] = main_part
            job["date"] = date_part
            bullet_start = 3

        else:
            if len(lines) >= 2 and not is_long_sentence(lines[0]):
                job["title"] = lines[0]
                if len(lines) >= 3 and not is_long_sentence(lines[1]):
                    job["company"] = lines[1]
                    bullet_start = 2
                else:
                    bullet_start = 1
            else:
                job["title"] = lines[0]
                bullet_start = 1

        if "|" in job["title"] and not job["company"]:
            parts = job["title"].split("|", 1)
            job["title"] = parts[0].strip()
            remainder = parts[1].strip()
            if has_date(remainder):
                main_part, date_part = split_date_from_line(remainder)
                job["company"] = main_part
                job["date"] = date_part
            else:
                job["company"] = remainder

        if " at " in job["title"].lower() and not job["company"]:
            parts = re.split(r"\s+at\s+", job["title"], flags=re.IGNORECASE, maxsplit=1)
            job["title"] = parts[0].strip()
            job["company"] = parts[1].strip()

        for line in lines[bullet_start:]:
            if line:
                job["bullets"].append(clean_line(line))

        if job["title"] or job["bullets"]:
            jobs.append(job)

    return jobs


def parse_education(raw_text):
    if not raw_text.strip():
        return []

    raw_blocks = re.split(r"\n\s*\n", raw_text.strip())
    entries = []

    for block in raw_blocks:
        lines = [clean_line(l) for l in block.strip().split("\n") if clean_line(l)]
        if not lines:
            continue

        entry = {"degree": "", "specialization": "", "institution": "", "details": ""}

        degree_index = None
        for i, line in enumerate(lines):
            if DEGREE_WORDS.search(line):
                degree_index = i
                break

        if degree_index is not None:
            entry["degree"] = lines[degree_index]
            remaining = lines[degree_index + 1:]
        else:
            entry["degree"] = lines[0]
            remaining = lines[1:]

        if remaining and remaining[0].startswith("("):
            entry["specialization"] = remaining[0]
            remaining = remaining[1:]

        for line in remaining:
            if INSTITUTION_WORDS.search(line) or (has_date(line) and not entry["institution"]):
                main_part, date_part = split_date_from_line(line)
                if "|" in main_part:
                    parts = main_part.split("|", 1)
                    entry["institution"] = parts[0].strip()
                    entry["details"] = parts[1].strip()
                    if date_part:
                        entry["details"] += " | " + date_part
                else:
                    entry["institution"] = main_part
                    if date_part:
                        entry["details"] = date_part
            elif has_date(line):
                main_part, date_part = split_date_from_line(line)
                if not entry["institution"]:
                    entry["institution"] = main_part
                if date_part and not entry["details"]:
                    entry["details"] = date_part
            else:
                if not entry["institution"]:
                    entry["institution"] = line

        if entry["degree"] or entry["institution"]:
            entries.append(entry)

    return entries


def parse_projects(raw_text):
    if not raw_text.strip():
        return []

    raw_blocks = re.split(r"\n\s*\n", raw_text.strip())
    projects = []

    for block in raw_blocks:
        lines = [clean_line(l) for l in block.strip().split("\n") if clean_line(l)]
        if not lines:
            continue

        project = {"title": "", "date": "", "bullets": []}

        first_line = lines[0]
        if has_date(first_line):
            main_part, date_part = split_date_from_line(first_line)
            if "|" in main_part:
                parts = main_part.split("|", 1)
                project["title"] = parts[0].strip()
                extra = parts[1].strip()
                if has_date(extra):
                    _, date_part2 = split_date_from_line(extra)
                    project["date"] = date_part2 or date_part
                else:
                    project["date"] = date_part
            else:
                project["title"] = main_part
                project["date"] = date_part
        elif "|" in first_line:
            parts = first_line.split("|", 1)
            project["title"] = parts[0].strip()
            remainder = parts[1].strip()
            if has_date(remainder):
                main_part, date_part = split_date_from_line(remainder)
                project["date"] = date_part or main_part
            else:
                project["date"] = remainder
        else:
            project["title"] = first_line

        for line in lines[1:]:
            if line:
                project["bullets"].append(clean_line(line))

        if project["title"] or project["bullets"]:
            projects.append(project)

    return projects


def parse_certifications(raw_text):
    if not raw_text.strip():
        return []

    certs = []
    lines = [clean_line(l) for l in raw_text.strip().split("\n") if clean_line(l)]

    for line in lines:
        cert = {"name": "", "issuer": ""}

        for sep in [" | ", " · ", " - ", " by ", " from ", " @ "]:
            if sep.lower() in line.lower():
                idx = line.lower().find(sep.lower())
                cert["name"] = line[:idx].strip()
                cert["issuer"] = line[idx + len(sep):].strip()
                break
        else:
            cert["name"] = line

        if cert["name"]:
            certs.append(cert)

    return certs


def parse_skills(raw_text):
    if not raw_text.strip():
        return []

    lines = [clean_line(l) for l in raw_text.strip().split("\n") if clean_line(l)]
    return lines

