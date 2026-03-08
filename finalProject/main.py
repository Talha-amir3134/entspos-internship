"""
main.py  –  Entry point for the Student Record Management System
────────────────────────────────────────────────────────────────
Run:
    python main.py

What happens:
    1. Loads config from .env
    2. Reads students.csv  AND  submissions.csv  concurrently (asyncio.gather)
    3. Validates every record – bad rows are logged, not crashed on
    4. Flags students who failed (any subject < passing mark)
    5. Calculates late‑submission fines
    6. Prints a colourful summary to the terminal
    7. Saves a timestamped text report into  reports/
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# python‑dotenv reads .env into os.environ
from dotenv import load_dotenv

from decorators import log_action, timer
from exceptions import StudentRecordError
from loader import apply_fines, load_students_csv, load_submissions_csv
from models import Student
from reports import generate_report


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Config loader
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def load_config() -> dict:
    """Read settings from .env and return them as a handy dict."""
    # Look for .env next to this script
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    return {
        "students_csv": os.getenv("STUDENTS_CSV", "data/students.csv"),
        "submissions_csv": os.getenv("SUBMISSIONS_CSV", "data/submissions.csv"),
        "passing_mark": int(os.getenv("PASSING_MARK", "50")),
        "fine_per_day": float(os.getenv("FINE_PER_DAY", "5.00")),
        "report_dir": os.getenv("REPORT_DIR", "reports"),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Terminal display helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_header():
    print()
    print("=" * 90)
    print("  STUDENT RECORD MANAGEMENT SYSTEM")
    print("=" * 90)
    print()


def print_students(title: str, students: list[Student]):
    print(f"\n{'─' * 90}")
    print(f"  {title}")
    print(f"{'─' * 90}")
    for s in students:
        print(f"  {s.summary_line()}")


def print_fines(students: list[Student]):
    fined = [s for s in students if s.late_fines > 0]
    print(f"\n{'─' * 90}")
    print("  LATE SUBMISSION FINES")
    print(f"{'─' * 90}")
    if not fined:
        print("  No late submissions!")
        return
    for s in fined:
        print(f"  {s.student_id} | {s.name:<20} | Total Fine: ${s.late_fines:.2f}")
        for d in s.late_details:
            if d["late_days"] > 0:
                print(
                    f"      └─ {d['assignment']}: "
                    f"{d['late_days']} day(s) late → ${d['fine']:.2f}"
                )


def print_errors(errors: list[str]):
    print(f"\n{'─' * 90}")
    print(f"  VALIDATION ERRORS  ({len(errors)} record(s) skipped)")
    print(f"{'─' * 90}")
    for err in errors:
        print(f"  ✖ {err}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Main async workflow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@log_action
@timer
async def run():
    """Orchestrates the full pipeline."""

    # 1. Load configuration from .env
    config = load_config()
    print(f"  Config loaded → passing mark: {config['passing_mark']}, "
          f"fine/day: ${config['fine_per_day']:.2f}")

    # 2. Load both CSV files concurrently
    students_task = load_students_csv(config["students_csv"])
    submissions_task = load_submissions_csv(
        config["submissions_csv"], config["fine_per_day"]
    )
    (students, errors), fines = await asyncio.gather(
        students_task, submissions_task
    )

    print(f"\n  Loaded {len(students)} valid student(s), "
          f"{len(errors)} skipped, "
          f"{sum(len(v) for v in fines.values())} submission record(s).")

    # 3. Attach fines to students
    apply_fines(students, fines)

    # 4. Display everything in the terminal
    print_header()
    print_students("ALL VALID STUDENTS", students)

    failed = [s for s in students if not s.has_passed(config["passing_mark"])]
    print_students(
        f"FAILED STUDENTS  (passing mark: {config['passing_mark']})", failed
    )

    print_fines(students)

    if errors:
        print_errors(errors)

    # 5. Generate timestamped report file
    report_path = await generate_report(
        students, errors, config["passing_mark"], config["report_dir"]
    )

    print(f"\n{'=' * 90}")
    print(f"  Report saved → {report_path}")
    print(f"{'=' * 90}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Script entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except StudentRecordError as exc:
        print(f"\n  FATAL: {exc.message}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n  Interrupted by user.")
        sys.exit(0)
