"""
Migration: add logo_url, photo_url, bio, city, founded_year fields.
Run once against your local DB, then push the updated .db file.

Usage:
    python migrate_add_media.py
    python migrate_add_media.py --db /path/to/colombia_liga.db
"""
from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).parent / "colombia_liga.db"


def migrate(db_path: Path):
    conn = sqlite3.connect(db_path)

    migrations = [
        # Teams
        "ALTER TABLE teams ADD COLUMN logo_url TEXT",
        "ALTER TABLE teams ADD COLUMN bio TEXT",
        "ALTER TABLE teams ADD COLUMN city TEXT",
        "ALTER TABLE teams ADD COLUMN founded_year INTEGER",
        # Players
        "ALTER TABLE players ADD COLUMN photo_url TEXT",
        "ALTER TABLE players ADD COLUMN bio TEXT",
    ]

    for sql in migrations:
        try:
            conn.execute(sql)
            print(f"  ✓ {sql}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print(f"  – already exists: {sql.split('ADD COLUMN')[1].strip()}")
            else:
                raise

    conn.commit()
    conn.close()
    print("\nMigration complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    migrate(Path(args.db))
