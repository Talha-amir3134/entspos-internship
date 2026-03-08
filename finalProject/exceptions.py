"""
exceptions.py  –  Custom exception hierarchy
─────────────────────────────────────────────
Every error the app can raise lives here.
Keeping them in one file makes it easy to import and catch them anywhere.

Hierarchy:
    StudentRecordError          (base for ALL our custom errors)
    ├── ValidationError         (a single field is invalid)
    ├── FileLoadError           (CSV can't be read / found)
    └── FineCalculationError    (something wrong while computing fines)
"""


class StudentRecordError(Exception):
    """Base exception for the Student Record System."""

    def __init__(self, message: str = "An error occurred in the student record system"):
        self.message = message
        super().__init__(self.message)


class ValidationError(StudentRecordError):
    """Raised when a student record fails validation.

    Attributes:
        student_id : the ID of the problematic record (if known)
        field      : which column triggered the error
    """

    def __init__(self, message: str, student_id: str = "UNKNOWN", field: str = ""):
        self.student_id = student_id
        self.field = field
        full_message = f"[Validation] Student {student_id} – {field}: {message}"
        super().__init__(full_message)


class FileLoadError(StudentRecordError):
    """Raised when a CSV file cannot be loaded."""

    def __init__(self, filepath: str, reason: str = "file not found"):
        self.filepath = filepath
        full_message = f"[FileLoad] Could not load '{filepath}': {reason}"
        super().__init__(full_message)


class FineCalculationError(StudentRecordError):
    """Raised when late‑fine calculation fails (e.g. bad dates)."""

    def __init__(self, student_id: str, reason: str):
        self.student_id = student_id
        full_message = f"[Fine] Student {student_id}: {reason}"
        super().__init__(full_message)
