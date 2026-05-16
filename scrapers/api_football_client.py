"""
API-Football Client — Colombian Primera A (2010–present)
=========================================================
Fetches season standings, match results, and team stats from api-football.com.
Cross-checks against your existing SQL database.

Setup:
    1. Sign up at https://dashboard.api-football.com (free tier: 100 req/day)
    2. Set your key: export API_FOOTBALL_KEY="your_key_here"
       OR create a .env file with: API_FOOTBALL_KEY=your_key_here

Usage:
    python api_football_client.py --standings 2023
    python api_football_client.py --standings 2010 2023  (range)
    python api_football_client.py --results 2023
    python api_football_client.py --crosscheck            (compare vs your DB)
"""

import os
import json
import time
import csv
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("Run: pip install requests")
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env is optional


# ─── Config ──────────────────────────────────────────────────────────────────

API_KEY    = os.getenv("API_FOOTBALL_KEY", "YOUR_KEY_HERE")
BASE_URL   = "https://v3.football.api-sports.io"
LEAGUE_ID  = 239        # Colombia - Primera A
OUTPUT_DIR = Path("../data")
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR  = OUTPUT_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key":  API_KEY,
}


# ─── HTTP + caching ──────────────────────────────────────────────────────────

def cache_path(endpoint: str, params: dict) -> Path:
    key = endpoint.replace("/", "_") + "_" + "_".join(f"{k}{v}" for k, v in sorted(params.items()))
    return CACHE_DIR / f"{key}.json"


def api_get(endpoint: str, params: dict = {}, use_cache=True) -> dict | None:
    cp = cache_path(endpoint, params)
    if use_cache and cp.exists():
        with open(cp) as f:
            return json.load(f)

    if API_KEY == "YOUR_KEY_HERE":
        print("[ERROR] Set API_FOOTBALL_KEY env var or replace placeholder in config")
        return None

    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Respect rate limit headers
        remaining = int(resp.headers.get("x-ratelimit-requests-remaining", 999))
        if remaining < 5:
            print(f"  [WARN] Only {remaining} API requests remaining today")

        with open(cp, "w") as f:
            json.dump(data, f)
        return data
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return None


# ─── Standings ───────────────────────────────────────────────────────────────

def normalize_tournament(round_name: str | None) -> str:
    if not round_name:
        return "Main"
    r = round_name.lower()
    if "apertura" in r:
        return "Apertura"
    if "clausura" in r or "finaliz" in r or "closing" in r:
        return "Clausura"
    return "Main"


def fetch_standings(year: int) -> list[dict]:
    """
    Returns list of standing rows for a given season year.
    API returns Apertura + Clausura as separate groups.
    """
    data = api_get("standings", {"league": LEAGUE_ID, "season": year})
    if not data or not data.get("response"):
        print(f"  [{year}] No standings data")
        return []

    rows = []
    for league_block in data["response"]:
        for group in league_block.get("league", {}).get("standings", []):
            tournament = normalize_tournament(
                group[0].get("group") if group else None
            )
            for entry in group:
                team   = entry.get("team", {})
                all_s  = entry.get("all", {})
                goals  = all_s.get("goals", {})
                rows.append({
                    "year":        year,
                    "tournament":  tournament,
                    "position":    entry.get("rank"),
                    "team":        team.get("name"),
                    "team_id":     team.get("id"),
                    "played":      all_s.get("played"),
                    "won":         all_s.get("win"),
                    "drawn":       all_s.get("draw"),
                    "lost":        all_s.get("lose"),
                    "gf":          goals.get("for"),
                    "ga":          goals.get("against"),
                    "gd":          entry.get("goalsDiff"),
                    "points":      entry.get("points"),
                    "form":        entry.get("form"),
                    "source":      "API-Football",
                })
    print(f"  [{year}] {len(rows)} standing rows")
    return rows


def fetch_standings_range(start: int, end: int) -> list[dict]:
    all_rows = []
    for year in range(start, end + 1):
        rows = fetch_standings(year)
        all_rows.extend(rows)
        time.sleep(0.5)
    return all_rows


# ─── Match results ────────────────────────────────────────────────────────────

def fetch_results(year: int) -> list[dict]:
    """Fetch all completed match results for a season"""
    data = api_get("fixtures", {
        "league":  LEAGUE_ID,
        "season":  year,
        "status":  "FT",    # Full Time only
    })
    if not data or not data.get("response"):
        return []

    matches = []
    for fix in data["response"]:
        fixture  = fix.get("fixture", {})
        teams    = fix.get("teams", {})
        score    = fix.get("score", {}).get("fulltime", {})
        league   = fix.get("league", {})
        matches.append({
            "fixture_id":  fixture.get("id"),
            "year":        year,
            "tournament":  normalize_tournament(league.get("round")),
            "date":        fixture.get("date", "")[:10],
            "round":       league.get("round"),
            "home_team":   teams.get("home", {}).get("name"),
            "home_id":     teams.get("home", {}).get("id"),
            "away_team":   teams.get("away", {}).get("name"),
            "away_id":     teams.get("away", {}).get("id"),
            "home_goals":  score.get("home"),
            "away_goals":  score.get("away"),
            "venue":       fixture.get("venue", {}).get("name"),
            "source":      "API-Football",
        })
    print(f"  [{year}] {len(matches)} matches")
    return matches


# ─── Cross-check engine ───────────────────────────────────────────────────────

def crosscheck_with_db(api_standings: list[dict], db_path: str = "../data/colombia.db"):
    """
    Compare API standings against your existing SQLite database.
    Flags:
        MATCH          - same points & position
        PTS_MISMATCH   - different points
        POS_MISMATCH   - different position (same pts possible)
        MISSING_IN_DB  - team found in API but not in your DB
        MISSING_IN_API - team in your DB but not in API
    """
    if not Path(db_path).exists():
        print(f"[WARN] DB not found at {db_path}. Skipping cross-check.")
        print("       Update db_path to point to your SQL database.")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    discrepancies = []
    for api_row in api_standings:
        cursor.execute("""
            SELECT position, points, won, drawn, lost, gf, ga
            FROM col_season_standings
            WHERE year = ? AND team = ? AND tournament = ?
        """, (api_row["year"], api_row["team"], api_row["tournament"]))
        db_row = cursor.fetchone()

        if not db_row:
            discrepancies.append({
                "status":      "MISSING_IN_DB",
                "year":        api_row["year"],
                "tournament":  api_row["tournament"],
                "team":        api_row["team"],
                "api_pts":     api_row["points"],
                "db_pts":      None,
                "api_pos":     api_row["position"],
                "db_pos":      None,
            })
            continue

        db_pos, db_pts = db_row[0], db_row[1]
        status = "MATCH"
        if db_pts != api_row["points"]:
            status = "PTS_MISMATCH"
        elif db_pos != api_row["position"]:
            status = "POS_MISMATCH"

        if status != "MATCH":
            discrepancies.append({
                "status":     status,
                "year":       api_row["year"],
                "tournament": api_row["tournament"],
                "team":       api_row["team"],
                "api_pts":    api_row["points"],
                "db_pts":     db_pts,
                "api_pos":    api_row["position"],
                "db_pos":     db_pos,
                "pts_diff":   abs((api_row["points"] or 0) - (db_pts or 0)),
            })

    conn.close()
    return discrepancies


# ─── Save helpers ─────────────────────────────────────────────────────────────

def save_to_json(data: list, filename: str):
    out = OUTPUT_DIR / filename
    with open(out, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved → {out}")


def save_to_csv(data: list, filename: str):
    if not data:
        return
    out = OUTPUT_DIR / filename
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=data[0].keys())
        w.writeheader()
        w.writerows(data)
    print(f"Saved → {out}  ({len(data)} rows)")


def save_discrepancy_report(discrepancies: list):
    if not discrepancies:
        print("\n✓ No discrepancies found — your database matches API-Football perfectly!")
        return

    out = OUTPUT_DIR / "discrepancy_report.json"
    with open(out, "w") as f:
        json.dump(discrepancies, f, indent=2)

    out_csv = OUTPUT_DIR / "discrepancy_report.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=discrepancies[0].keys())
        w.writeheader()
        w.writerows(discrepancies)

    print(f"\n⚠  {len(discrepancies)} discrepancies found")
    print(f"   JSON report → {out}")
    print(f"   CSV  report → {out_csv}")

    # Summary by type
    from collections import Counter
    counts = Counter(d["status"] for d in discrepancies)
    for status, n in counts.most_common():
        print(f"   {status}: {n}")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--standings", nargs="+", type=int, metavar="YEAR",
                        help="Fetch standings for year or year range")
    parser.add_argument("--results", nargs="+", type=int, metavar="YEAR",
                        help="Fetch match results for year or year range")
    parser.add_argument("--crosscheck", action="store_true",
                        help="Compare API data against your local DB")
    parser.add_argument("--db", default="../data/colombia.db",
                        help="Path to your SQLite DB (default: ../data/colombia.db)")
    args = parser.parse_args()

    if args.standings:
        if len(args.standings) == 2:
            rows = fetch_standings_range(args.standings[0], args.standings[1])
        else:
            rows = fetch_standings(args.standings[0])
        save_to_json(rows, "api_standings.json")
        save_to_csv(rows, "api_standings.csv")

        if args.crosscheck:
            disc = crosscheck_with_db(rows, args.db)
            save_discrepancy_report(disc)

    elif args.results:
        all_matches = []
        for year in (range(args.results[0], args.results[1] + 1)
                     if len(args.results) == 2 else args.results):
            all_matches.extend(fetch_results(year))
            time.sleep(0.5)
        save_to_json(all_matches, "api_results.json")
        save_to_csv(all_matches, "api_results.csv")

    elif args.crosscheck:
        # Load previously cached standings and cross-check
        cached = OUTPUT_DIR / "api_standings.json"
        if not cached.exists():
            print("[ERROR] Run --standings first to fetch data, then --crosscheck")
            return
        with open(cached) as f:
            rows = json.load(f)
        disc = crosscheck_with_db(rows, args.db)
        save_discrepancy_report(disc)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
