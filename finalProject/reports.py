"""
reports.py  –  Timestamped report generation
─────────────────────────────────────────────
Generates a clean text report saved into the `reports/` directory.
The filename includes a timestamp so you never overwrite a previous report.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from decorators import log_action, timer
from models import Student


@log_action
@timer
async def generate_report(
    students: list[Student],
    errors: list[str],
    passing_mark: int,
    report_dir: str = "reports",
) -> str:
    """Build a full report string and write it to a timestamped file.

    Returns the path of the generated report.
    """

    # ── Build the report text ─────────────────────────────────
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    separator = "=" * 90

    lines: list[str] = [
        separator,
        f"  STUDENT RECORD REPORT  –  Generated: {now.strftime('%B %d, %Y at %H:%M:%S')}",
        separator,
        "",
    ]

    # Section 1: All valid students
    lines.append(f"{'─' * 90}")
    lines.append("  ALL VALID STUDENTS")
    lines.append(f"{'─' * 90}")
    for s in students:
        lines.append(f"  {s.summary_line()}")
    lines.append("")

    # Section 2: Failed students
    failed = [s for s in students if not s.has_passed(passing_mark)]
    lines.append(f"{'─' * 90}")
    lines.append(f"  FAILED STUDENTS  (passing mark: {passing_mark})")
    lines.append(f"{'─' * 90}")
    if failed:
        for s in failed:
            lines.append(f"  ⚠ {s.summary_line()}")
    else:
        lines.append("  None – everyone passed! 🎉")
    lines.append("")

    # Section 3: Late fines
    fined = [s for s in students if s.late_fines > 0]
    lines.append(f"{'─' * 90}")
    lines.append("  LATE SUBMISSION FINES")
    lines.append(f"{'─' * 90}")
    if fined:
        for s in fined:
            lines.append(f"  {s.student_id} | {s.name:<20} | Total Fine: ${s.late_fines:.2f}")
            for d in s.late_details:
                if d["late_days"] > 0:
                    lines.append(
                        f"      └─ {d['assignment']}: {d['late_days']} day(s) late → ${d['fine']:.2f}"
                    )
    else:
        lines.append("  No late submissions!")
    lines.append("")

    # Section 4: Validation errors
    lines.append(f"{'─' * 90}")
    lines.append(f"  VALIDATION ERRORS  ({len(errors)} record(s) skipped)")
    lines.append(f"{'─' * 90}")
    if errors:
        for err in errors:
            lines.append(f"  ✖ {err}")
    else:
        lines.append("  All records were valid.")
    lines.append("")

    # Section 5: Summary stats
    lines.append(f"{'─' * 90}")
    lines.append("  SUMMARY")
    lines.append(f"{'─' * 90}")
    total = len(students)
    passed = total - len(failed)
    lines.append(f"  Total valid records : {total}")
    lines.append(f"  Passed              : {passed}")
    lines.append(f"  Failed              : {len(failed)}")
    lines.append(f"  Skipped (errors)    : {len(errors)}")
    if students:
        avg = sum(s.average for s in students) / total
        lines.append(f"  Class average       : {avg:.2f}")
    total_fines = sum(s.late_fines for s in students)
    lines.append(f"  Total fines charged : ${total_fines:.2f}")
    lines.append(separator)

    report_text = "\n".join(lines)

    # ── Write to file (offload to thread) ─────────────────────
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"report_{timestamp}.txt"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _write_file, filename, report_text)

    return str(filename)


def _write_file(path: Path, content: str) -> None:
    """Synchronous file write – called inside run_in_executor."""
    path.write_text(content, encoding="utf-8")
