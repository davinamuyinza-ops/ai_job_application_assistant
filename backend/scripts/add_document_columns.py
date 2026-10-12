"""One-off migration: add document columns to the existing `applications` table.

Base.metadata.create_all only creates missing tables, it never adds columns to
a table that already exists, so this must be run once against the database
(before deploying backend code that reads these columns). Safe to re-run.

    cd backend
    .venv/Scripts/python.exe scripts/add_document_columns.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import engine  # noqa: E402

STATEMENT = """
ALTER TABLE applications
    ADD COLUMN IF NOT EXISTS tailored_resume JSONB,
    ADD COLUMN IF NOT EXISTS cover_letter TEXT,
    ADD COLUMN IF NOT EXISTS job_description TEXT
"""

if __name__ == "__main__":
    with engine.begin() as connection:
        connection.execute(text(STATEMENT))

    print("applications table now has tailored_resume, cover_letter, job_description")
