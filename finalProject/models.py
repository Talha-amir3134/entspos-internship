"""
models.py  –  Data models (OOP)
────────────────────────────────
Uses a `dataclass` so Python auto‑generates __init__, __repr__, etc.
Business logic (average, pass/fail, fines) lives as methods on the class.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Student:
    """Represents one student record loaded from CSV."""

    student_id: str
    name: str
    email: str
    marks: dict[str, int]                     # {"math": 85, "science": 90, …}
    late_fines: float = 0.0                    # total monetary fine
    late_details: list[dict] = field(default_factory=list)  # per‑assignment info

    # ── Computed helpers ──────────────────────────────────────────

    @property
    def average(self) -> float:
        """Return the average mark across all subjects."""
        if not self.marks:
            return 0.0
        return sum(self.marks.values()) / len(self.marks)

    def has_passed(self, passing_mark: int = 50) -> bool:
        """A student passes only if EVERY subject >= passing_mark."""
        return all(mark >= passing_mark for mark in self.marks.values())

    @property
    def status(self) -> str:
        """Human‑readable pass / fail label."""
        return "PASS" if self.has_passed() else "FAIL"

    # ── Display ───────────────────────────────────────────────────

    def summary_line(self) -> str:
        """One‑line summary used in terminal output and reports."""
        marks_str = ", ".join(f"{subj}: {m}" for subj, m in self.marks.items())
        return (
            f"{self.student_id} | {self.name:<20} | Avg: {self.average:5.1f} "
            f"| {self.status:<4} | Fine: ${self.late_fines:6.2f} | {marks_str}"
        )
