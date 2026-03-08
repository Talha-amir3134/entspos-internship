"""
loader.py  –  CSV loading, validation, and fine calculation (async)
──────────────────────────────────────────────────────────────────
All heavy I/O (reading files, parsing rows) runs through asyncio so
multiple files can be processed concurrently with `asyncio.gather`.

Flow:
    load_students_csv()   →  raw rows  →  validate_record()  →  Student objects
    load_submissions_csv()  →  compute late fines per student
"""

from __future__ import annotations

import asyncio
import csv
import re
from datetime import datetime
from pathlib import Path

from decorators import log_action, timer
from exceptions import FileLoadError, FineCalculationError, ValidationError
from models import Student


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Validation helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

SUBJECT_COLUMNS = ["math", "science", "english", "history"]


def validate_record(row: dict[str, str]) -> Student:
    """Validate a single CSV row and return a Student object.

    Raises ValidationError with a clear message on any problem.
    """
    student_id = row.get("student_id", "").strip()

    # ── Name check ────────────────────────────────────────────
    name = row.get("name", "").strip()
    if not name:
        raise ValidationError("Name is empty", student_id=student_id, field="name")

    # ── Email check ───────────────────────────────────────────
    email = row.get("email", "").strip()
    if not email or not EMAIL_REGEX.match(email):
        raise ValidationError(
            f"Invalid email '{email}'", student_id=student_id, field="email"
        )

    # ── Marks check ───────────────────────────────────────────
    marks: dict[str, int] = {}
    for subject in SUBJECT_COLUMNS:
        raw = row.get(subject, "").strip()
        try:
            value = int(raw)
        except ValueError:
            raise ValidationError(
                f"Non‑numeric mark '{raw}'", student_id=student_id, field=subject
            )
        if value < 0 or value > 100:
            raise ValidationError(
                f"Mark {value} out of 0‑100 range",
                student_id=student_id,
                field=subject,
            )
        marks[subject] = value

    return Student(student_id=student_id, name=name, email=email, marks=marks)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSV loaders (async)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@log_action
@timer
async def load_students_csv(filepath: str) -> tuple[list[Student], list[str]]:
    """Read the students CSV and return (valid_students, error_messages).

    File I/O is offloaded to a thread so the event loop stays free.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileLoadError(filepath)

    # Run blocking file read in a thread
    loop = asyncio.get_running_loop()
    rows = await loop.run_in_executor(None, _read_csv_rows, path)

    students: list[Student] = []
    errors: list[str] = []

    for row in rows:
        try:
            student = validate_record(row)
            students.append(student)
        except ValidationError as exc:
            errors.append(exc.message)      # log it, don't crash

    return students, errors


@log_action
@timer
async def load_submissions_csv(
    filepath: str,
    fine_per_day: float,
) -> dict[str, list[dict]]:
    """Read the submissions CSV and compute late days + fines.

    Returns a dict mapping student_id → list of assignment fine info.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileLoadError(filepath)

    loop = asyncio.get_running_loop()
    rows = await loop.run_in_executor(None, _read_csv_rows, path)

    fines: dict[str, list[dict]] = {}

    for row in rows:
        sid = row.get("student_id", "").strip()
        try:
            due = datetime.strptime(row["due_date"].strip(), "%Y-%m-%d")
            submitted = datetime.strptime(row["submitted_date"].strip(), "%Y-%m-%d")
        except (KeyError, ValueError) as exc:
            raise FineCalculationError(sid, f"Bad date format – {exc}")

        late_days = max(0, (submitted - due).days)
        fine_amount = late_days * fine_per_day

        fines.setdefault(sid, []).append(
            {
                "assignment": row.get("assignment", "N/A"),
                "late_days": late_days,
                "fine": fine_amount,
            }
        )

    return fines


def apply_fines(students: list[Student], fines: dict[str, list[dict]]) -> None:
    """Attach fine data from submissions onto each Student object (in‑place)."""
    for student in students:
        details = fines.get(student.student_id, [])
        student.late_details = details
        student.late_fines = sum(d["fine"] for d in details)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Private helper
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Synchronous CSV read – called inside run_in_executor."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)
