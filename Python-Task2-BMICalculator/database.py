"""SQLite persistence for BMI records."""

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseManager:
    """Manage the BMI SQLite database and parameterized data access."""

    def __init__(self, database_path: str | Path = "bmi_database.db") -> None:
        self.database_path = Path(database_path)
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Open the database connection and configure row access."""
        if self.connection is None:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row

    def initialize(self) -> None:
        """Create the database schema and add sample data to a new database."""
        self.connect()
        assert self.connection is not None
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS BMIRecords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_bmi_records_user_date "
            "ON BMIRecords(username, date)"
        )
        self.connection.commit()
        self.seed_sample_data()

    def seed_sample_data(self) -> None:
        """Insert a small demonstration history only when the table is empty."""
        assert self.connection is not None
        record_count = self.connection.execute("SELECT COUNT(*) FROM BMIRecords").fetchone()[0]
        if record_count:
            return
        sample_records = [
            ("Sample User", 68.0, 1.72, 22.99, "Normal Weight", "2026-07-20 08:30:00"),
            ("Sample User", 69.0, 1.72, 23.32, "Normal Weight", "2026-07-22 08:30:00"),
            ("Sample User", 70.0, 1.72, 23.66, "Normal Weight", "2026-07-24 08:30:00"),
        ]
        self.connection.executemany(
            """
            INSERT INTO BMIRecords (username, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            sample_records,
        )
        self.connection.commit()

    def save_record(
        self,
        username: str,
        weight: float,
        height: float,
        bmi: float,
        category: str,
        date: str,
    ) -> int:
        """Save a calculated BMI record and return its new ID."""
        self.connect()
        assert self.connection is not None
        cursor = self.connection.execute(
            """
            INSERT INTO BMIRecords (username, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, weight, height, bmi, category, date),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_records(self, username: str | None = None) -> list[dict[str, Any]]:
        """Return records newest first, optionally filtered by user name."""
        self.connect()
        assert self.connection is not None
        if username:
            rows = self.connection.execute(
                """
                SELECT date, weight, height, bmi, category, username
                FROM BMIRecords
                WHERE username = ? COLLATE NOCASE
                ORDER BY date DESC, id DESC
                """,
                (username,),
            ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT date, weight, height, bmi, category, username
                FROM BMIRecords
                ORDER BY date DESC, id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close the SQLite connection if one is open."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
