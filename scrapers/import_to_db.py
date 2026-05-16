"""
Import scraped data into colombia_liga.db (existing normalized schema).

Run order:
    1. python rsssf_scraper.py            # produces data/seasons_1948_2009.json
    2. python import_to_db.py --rsssf     # loads pre-2010 standings into DB
    3. python import_to_db.py --crosscheck # compares DB standings vs API-Football

Usage:
    python import_to_db.py --rsssf   [--db PATH]   # import RSSSF 1948-2009
    python import_to_db.py --crosscheck [--years 2015 2023] [--db PATH]
    python import_to_db.py --rsssf --crosscheck     # both
"""

from __future__ import annotations
import argparse
import json
import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DB = Path(__file__).parent.parent / "apps" / "api" / "colombia_liga.db"

# The RSSSF/historical data all belongs to this competition
HISTORICAL_COMPETITION = {
    "name":           "Primera División",
    "slug":           "primera_division",
    "canonical_name": "Primera División",
    "kind":           "league",
}

# Phase normalisation: RSSSF "Main" means a single-table season → no phase
PHASE_MAP = {
    "Apertura":  "Apertura",
    "Clausura":  "Clausura",
    "Liguilla":  "Clausura",   # liguilla is the playoff/closing stage
    "Main":      None,
}


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def upsert_competition(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT id FROM competitions WHERE canonical_name = ?",
        (HISTORICAL_COMPETITION["canonical_name"],),
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO competitions (name, slug, canonical_name, kind) VALUES (?,?,?,?)",
        (
            HISTORICAL_COMPETITION["name"],
            HISTORICAL_COMPETITION["slug"],
            HISTORICAL_COMPETITION["canonical_name"],
            HISTORICAL_COMPETITION["kind"],
        ),
    )
    return cur.lastrowid


def upsert_season(conn: sqlite3.Connection, competition_id: int, year: int, phase: str | None) -> int:
    label_parts = ["Primera División", str(year)]
    if phase:
        label_parts.append(phase)
    label = " ".join(label_parts)

    row = conn.execute(
        "SELECT id FROM seasons WHERE competition_id=? AND year=? AND phase IS ?",
        (competition_id, year, phase),
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO seasons (competition_id, year, phase, label) VALUES (?,?,?,?)",
        (competition_id, year, phase, label),
    )
    return cur.lastrowid


def upsert_team(conn: sqlite3.Connection, name: str) -> int:
    row = conn.execute("SELECT id FROM teams WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]

    # Try case-insensitive match before inserting
    row = conn.execute(
        "SELECT id, name FROM teams WHERE lower(name) = lower(?)", (name,)
    ).fetchone()
    if row:
        return row["id"]

    cur = conn.execute("INSERT INTO teams (name) VALUES (?)", (name,))
    return cur.lastrowid


def insert_standing(
    conn: sqlite3.Connection,
    season_id: int,
    team_id: int,
    snapshot_date: str,
    row: dict,
) -> bool:
    try:
        conn.execute(
            """
            INSERT INTO standings
                (season_id, team_id, snapshot_date, position,
                 played, won, drawn, lost, goals_for, goals_against, points)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                season_id,
                team_id,
                snapshot_date,
                row["position"],
                row.get("played"),
                row.get("won"),
                row.get("drawn"),
                row.get("lost"),
                row.get("gf"),
                row.get("ga"),
                row.get("points"),
            ),
        )
        return True
    except sqlite3.IntegrityError:
        return False  # already exists


# ── RSSSF import ─────────────────────────────────────────────────────────────

def import_rsssf(conn: sqlite3.Connection):
    src = DATA_DIR / "seasons_1948_2009.json"
    if not src.exists():
        print(f"[ERROR] {src} not found. Run rsssf_scraper.py first.")
        return

    with open(src) as f:
        seasons = json.load(f)

    competition_id = upsert_competition(conn)
    print(f"Competition id={competition_id}")

    total_inserted = total_skipped = 0

    for season_data in seasons:
        year = season_data["year"]
        tournaments = season_data.get("tournaments", {})

        if not tournaments:
            continue

        for tournament_name, standings in tournaments.items():
            if not standings:
                continue

            phase = PHASE_MAP.get(tournament_name, None)
            season_id = upsert_season(conn, competition_id, year, phase)

            # Use end-of-year as synthetic snapshot date for historical data
            snapshot_date = f"{year}-12-31"

            for standing_row in standings:
                team_name = standing_row.get("team", "").strip()
                if not team_name:
                    continue

                team_id = upsert_team(conn, team_name)
                inserted = insert_standing(conn, season_id, team_id, snapshot_date, standing_row)
                if inserted:
                    total_inserted += 1
                else:
                    total_skipped += 1

        conn.commit()
        print(f"  {year}: {sum(len(s) for s in tournaments.values())} rows")

    print(f"\nDone. Inserted: {total_inserted}  Skipped (already exists): {total_skipped}")


# ── Cross-check: DB vs API-Football ──────────────────────────────────────────

def crosscheck(conn: sqlite3.Connection, start_year: int, end_year: int):
    try:
        from api_football_client import fetch_standings_range
    except ImportError:
        print("[ERROR] api_football_client.py must be in the same directory")
        return

    print(f"Fetching API-Football standings {start_year}–{end_year}...")
    api_rows = fetch_standings_range(start_year, end_year)

    if not api_rows:
        print("[WARN] No API data returned — check your API_FOOTBALL_KEY")
        return

    discrepancies = []
    matched = 0

    for api in api_rows:
        year       = api["year"]
        tournament = api["tournament"]
        team_name  = api["team"]
        phase      = PHASE_MAP.get(tournament, None)

        # Find team in DB (case-insensitive)
        team_row = conn.execute(
            "SELECT id FROM teams WHERE lower(name) = lower(?)", (team_name,)
        ).fetchone()

        if not team_row:
            discrepancies.append({
                "status":     "MISSING_IN_DB",
                "year":       year,
                "tournament": tournament,
                "team":       team_name,
                "api_pts":    api["points"],
                "db_pts":     None,
                "api_pos":    api["position"],
                "db_pos":     None,
            })
            continue

        team_id = team_row["id"]

        # Find season
        season_row = conn.execute(
            "SELECT id FROM seasons WHERE year=? AND phase IS ?",
            (year, phase),
        ).fetchone()

        if not season_row:
            discrepancies.append({
                "status":     "MISSING_SEASON_IN_DB",
                "year":       year,
                "tournament": tournament,
                "team":       team_name,
                "api_pts":    api["points"],
                "db_pts":     None,
            })
            continue

        season_id = season_row["id"]

        # Find standing (use latest snapshot for that season)
        standing = conn.execute(
            """
            SELECT position, points FROM standings
            WHERE season_id=? AND team_id=?
            ORDER BY snapshot_date DESC LIMIT 1
            """,
            (season_id, team_id),
        ).fetchone()

        if not standing:
            discrepancies.append({
                "status":     "MISSING_IN_DB",
                "year":       year,
                "tournament": tournament,
                "team":       team_name,
                "api_pts":    api["points"],
                "db_pts":     None,
                "api_pos":    api["position"],
                "db_pos":     None,
            })
            continue

        db_pos, db_pts = standing["position"], standing["points"]
        status = "MATCH"
        if db_pts != api["points"]:
            status = "PTS_MISMATCH"
        elif db_pos != api["position"]:
            status = "POS_MISMATCH"

        if status == "MATCH":
            matched += 1
        else:
            discrepancies.append({
                "status":     status,
                "year":       year,
                "tournament": tournament,
                "team":       team_name,
                "api_pts":    api["points"],
                "db_pts":     db_pts,
                "api_pos":    api["position"],
                "db_pos":     db_pos,
                "pts_diff":   abs((api["points"] or 0) - (db_pts or 0)),
            })

    print(f"\nResults: {matched} matches, {len(discrepancies)} discrepancies")

    if not discrepancies:
        print("✓ DB matches API-Football perfectly for this range!")
        return

    # Save report
    out_json = DATA_DIR / "crosscheck_report.json"
    out_csv  = DATA_DIR / "crosscheck_report.csv"

    import csv
    with open(out_json, "w") as f:
        json.dump(discrepancies, f, indent=2, ensure_ascii=False)

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=discrepancies[0].keys())
        w.writeheader()
        w.writerows(discrepancies)

    from collections import Counter
    counts = Counter(d["status"] for d in discrepancies)
    for status, n in counts.most_common():
        print(f"  {status}: {n}")

    print(f"\nReports saved:")
    print(f"  {out_json}")
    print(f"  {out_csv}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rsssf",       action="store_true", help="Import RSSSF 1948-2009 data")
    parser.add_argument("--crosscheck",  action="store_true", help="Cross-check DB vs API-Football")
    parser.add_argument("--years",       nargs=2, type=int, default=[2010, 2024], metavar="YEAR",
                        help="Year range for cross-check (default: 2010 2024)")
    parser.add_argument("--db",          default=str(DEFAULT_DB), help="Path to colombia_liga.db")
    args = parser.parse_args()

    if not args.rsssf and not args.crosscheck:
        parser.print_help()
        return

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[ERROR] DB not found at {db_path}")
        print("       Pass --db path/to/colombia_liga.db")
        return

    print(f"DB: {db_path}")
    conn = get_conn(db_path)

    if args.rsssf:
        print("\n── Importing RSSSF 1948-2009 ──")
        import_rsssf(conn)

    if args.crosscheck:
        print("\n── Cross-checking vs API-Football ──")
        crosscheck(conn, args.years[0], args.years[1])

    conn.close()


if __name__ == "__main__":
    main()
