from __future__ import annotations

"""
RSSSF Colombian Football Scraper (1948–2010)
=============================================
Scrapes season-by-season standings and match results from rsssf.org.
Outputs structured JSON and CSV for loading into your SQL database.

Usage:
    python rsssf_scraper.py                   # scrape all seasons 1948-2009
    python rsssf_scraper.py --year 1990       # single season
    python rsssf_scraper.py --year 1990 2002  # range
    python rsssf_scraper.py --alltime         # all-time historical table only
    python rsssf_scraper.py --matches         # scrape match results too
"""

import requests
import re
import json
import csv
import time
import argparse
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://www.rsssf.org/tablesc"
ALLTIME_URL = "https://www.rsssf.org/tablesc/colalltime.html"
OUTPUT_DIR = Path("../data")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (research/data archival)"}

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


# ─── Helpers ────────────────────────────────────────────────────────────────

def fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        # RSSSF pages are latin-1 encoded
        resp.encoding = resp.apparent_encoding or "latin-1"
        return resp.text
    except Exception as e:
        print(f"  [WARN] Could not fetch {url}: {e}")
        return None


def season_url(year: int) -> str:
    """RSSSF uses 2-digit year suffix: col90.html, col02.html, col99.html"""
    suffix = str(year)[-2:].zfill(2)
    return f"{BASE_URL}/col{suffix}.html"


# ─── All-time table ──────────────────────────────────────────────────────────

def parse_alltime_table(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.find("pre")
    if not pre:
        print("[WARN] No <pre> block found in all-time page")
        return []

    rows = []
    pattern = re.compile(
        r"(\d+)\.\s+(.+?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)-(\d+)\s+([-\d]+)\s+(\d+)"
    )
    for line in pre.get_text().splitlines():
        m = pattern.match(line.strip())
        if m:
            rows.append({
                "rank":     int(m.group(1)),
                "team":     m.group(2).strip(),
                "pts_3pw":  int(m.group(3)),
                "played":   int(m.group(4)),
                "won":      int(m.group(5)),
                "drawn":    int(m.group(6)),
                "lost":     int(m.group(7)),
                "gf":       int(m.group(8)),
                "ga":       int(m.group(9)),
                "gd":       int(m.group(10)),
                "editions": int(m.group(11)),
            })
    return rows


# ─── Season standings ────────────────────────────────────────────────────────

def detect_tournament_name(text: str) -> str:
    text_lower = text.lower()
    if "apertura" in text_lower:
        return "Apertura"
    if "clausura" in text_lower or "finalizacion" in text_lower or "finalización" in text_lower:
        return "Clausura"
    if "liguilla" in text_lower:
        return "Liguilla"
    return "Main"


def parse_standing_block(lines: list[str], year: int, tournament: str) -> list[dict]:
    rows = []
    pattern = re.compile(
        r"(\d+)[.)]\s*(.+?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)-\s*(\d+)\s+(\d+)"
    )
    for line in lines:
        m = pattern.match(line.strip())
        if m:
            gf, ga = int(m.group(7)), int(m.group(8))
            rows.append({
                "year":       year,
                "tournament": tournament,
                "position":   int(m.group(1)),
                "team":       m.group(2).strip().rstrip("-"),
                "played":     int(m.group(3)),
                "won":        int(m.group(4)),
                "drawn":      int(m.group(5)),
                "lost":       int(m.group(6)),
                "gf":         gf,
                "ga":         ga,
                "gd":         gf - ga,
                "points":     int(m.group(9)),
            })
    return rows


# ─── Match results ────────────────────────────────────────────────────────────

def parse_date(month_str: str, day_str: str, year: int) -> str | None:
    month = MONTH_MAP.get(month_str.lower().strip()[:3])
    if not month:
        return None
    try:
        return f"{year}-{month:02d}-{int(day_str):02d}"
    except ValueError:
        return None


def parse_matches_from_text(text: str, year: int, tournament: str) -> list[dict]:
    """
    Parse match lines from RSSSF season page text.
    Handles formats like:
        Round 1
        [Feb 6]
        América     2-1 Cúcuta
        Cali        awd Equidad  [awarded 3-0, originally 2-3]
    """
    matches = []
    current_round = None
    current_date = None

    # Match line: "HomeTeam   score-score  AwayTeam"
    match_re = re.compile(
        r"^(.+?)\s{2,}(\d+)\s*-\s*(\d+)\s+(.+?)(?:\s+\[.*\])?\s*$"
    )
    # Awarded match: "HomeTeam   awd  AwayTeam  [awarded X-Y ...]"
    awarded_re = re.compile(
        r"^(.+?)\s{2,}awd\s+(.+?)\s*\[awarded\s+(\d+)-(\d+)",
        re.IGNORECASE,
    )
    # Round header: "Round 1", "Matchday 5", "Jornada 3", "Quarter-finals", etc.
    round_re = re.compile(
        r"^(Round|Matchday|Jornada|Date|Week|Quarter|Semi|Final)\b",
        re.IGNORECASE,
    )
    # Date line: [Feb 6], [Mar 14], [15 Feb], [6.2], etc.
    date_re = re.compile(
        r"\[(\w+)\s+(\d{1,2})\]|\[(\d{1,2})\s+(\w+)\]|\[(\d{1,2})\.(\d{1,2})\]"
    )

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Round header
        if round_re.match(line):
            current_round = line.rstrip(":")
            continue

        # Date line
        dm = date_re.search(line)
        if dm:
            if dm.group(1) and dm.group(2):       # [Feb 6]
                current_date = parse_date(dm.group(1), dm.group(2), year)
            elif dm.group(3) and dm.group(4):     # [6 Feb]
                current_date = parse_date(dm.group(4), dm.group(3), year)
            elif dm.group(5) and dm.group(6):     # [6.2]
                try:
                    current_date = f"{year}-{int(dm.group(6)):02d}-{int(dm.group(5)):02d}"
                except ValueError:
                    pass
            continue

        # Awarded match
        am = awarded_re.match(line)
        if am:
            matches.append({
                "year":        year,
                "tournament":  tournament,
                "stage":       current_round,
                "match_date":  current_date,
                "home_team":   am.group(1).strip(),
                "away_team":   am.group(2).strip(),
                "home_score":  int(am.group(3)),
                "away_score":  int(am.group(4)),
                "awarded":     True,
            })
            continue

        # Normal match
        mm = match_re.match(line)
        if mm and current_round:
            home = mm.group(1).strip()
            away = mm.group(4).strip()
            # Skip lines that look like standings (team names with lots of numbers)
            if re.search(r"\d{2,}\s+\d+\s+\d+\s+\d+", line):
                continue
            matches.append({
                "year":        year,
                "tournament":  tournament,
                "stage":       current_round,
                "match_date":  current_date,
                "home_team":   home,
                "away_team":   away,
                "home_score":  int(mm.group(2)),
                "away_score":  int(mm.group(3)),
                "awarded":     False,
            })

    return matches


def parse_season(html: str, year: int, parse_match_results: bool = False) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.find("pre")
    text = pre.get_text() if pre else soup.get_text()

    lines = text.splitlines()
    tournaments: dict[str, list] = {}
    all_matches: dict[str, list] = {}
    current_tournament = "Main"
    current_block: list[str] = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^(Apertura|Clausura|Finalizaci[oó]n|Liguilla|Primera|Second)", stripped, re.I):
            if current_block:
                standings = parse_standing_block(current_block, year, current_tournament)
                if standings:
                    tournaments[current_tournament] = standings
                if parse_match_results:
                    block_text = "\n".join(current_block)
                    matches = parse_matches_from_text(block_text, year, current_tournament)
                    if matches:
                        all_matches[current_tournament] = matches
            current_tournament = detect_tournament_name(stripped)
            current_block = []
        elif stripped:
            current_block.append(line)

    if current_block:
        standings = parse_standing_block(current_block, year, current_tournament)
        if standings:
            tournaments[current_tournament] = standings
        if parse_match_results:
            block_text = "\n".join(current_block)
            matches = parse_matches_from_text(block_text, year, current_tournament)
            if matches:
                all_matches[current_tournament] = matches

    champions = re.findall(r"[Cc]hampion(?:s)?:?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][\w\s.]+?)(?:\n|\[|\.)", text)
    champions = [c.strip() for c in champions]

    result = {
        "year":        year,
        "tournaments": tournaments,
        "champions":   champions,
    }
    if parse_match_results:
        result["matches"] = all_matches
    return result


# ─── Main scraper ─────────────────────────────────────────────────────────────

def scrape_alltime():
    print("→ Scraping all-time historical table...")
    html = fetch(ALLTIME_URL)
    if not html:
        print("[ERROR] Could not fetch all-time table")
        return

    rows = parse_alltime_table(html)
    print(f"  Found {len(rows)} clubs in all-time table")

    out_json = OUTPUT_DIR / "alltime_standings.json"
    out_csv  = OUTPUT_DIR / "alltime_standings.csv"

    with open(out_json, "w") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    if rows:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)

    print(f"  Saved → {out_json}")
    print(f"  Saved → {out_csv}")
    return rows


def scrape_season(year: int, parse_matches: bool = False) -> dict | None:
    url = season_url(year)
    print(f"  [{year}] {url}")
    html = fetch(url)
    if not html:
        return None
    season = parse_season(html, year, parse_match_results=parse_matches)
    total_standings = sum(len(t) for t in season["tournaments"].values())
    total_matches   = sum(len(m) for m in season.get("matches", {}).values())
    print(f"    → {len(season['tournaments'])} tournament(s), {total_standings} standings, {total_matches} matches")
    return season


def scrape_seasons(years: list[int], parse_matches: bool = False) -> list[dict]:
    results = []
    for year in years:
        season = scrape_season(year, parse_matches=parse_matches)
        if season:
            results.append(season)
        time.sleep(0.8)
    return results


def save_seasons(seasons: list[dict]):
    out_json = OUTPUT_DIR / "seasons_1948_2009.json"
    with open(out_json, "w") as f:
        json.dump(seasons, f, indent=2, ensure_ascii=False)
    print(f"\nSaved → {out_json}")

    out_csv = OUTPUT_DIR / "seasons_flat.csv"
    flat_rows = []
    for season in seasons:
        for tournament, standings in season["tournaments"].items():
            for row in standings:
                flat_rows.append(row)

    if flat_rows:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=flat_rows[0].keys())
            w.writeheader()
            w.writerows(flat_rows)
        print(f"Saved → {out_csv}  ({len(flat_rows)} rows)")

    # Save flat matches CSV if present
    all_match_rows = []
    for season in seasons:
        for tournament_matches in season.get("matches", {}).values():
            all_match_rows.extend(tournament_matches)

    if all_match_rows:
        out_matches = OUTPUT_DIR / "matches_flat.csv"
        with open(out_matches, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=all_match_rows[0].keys())
            w.writeheader()
            w.writerows(all_match_rows)
        print(f"Saved → {out_matches}  ({len(all_match_rows)} matches)")


def generate_sql_schema():
    schema = """-- ============================================================
-- Colombian Football Historical Database Schema
-- Source: RSSSF (pre-2010) + API-Football (2010+)
-- ============================================================

CREATE TABLE IF NOT EXISTS col_alltime_standings (
    id          SERIAL PRIMARY KEY,
    rank        INTEGER,
    team        VARCHAR(100),
    pts_3pw     INTEGER,
    played      INTEGER,
    won         INTEGER,
    drawn       INTEGER,
    lost        INTEGER,
    gf          INTEGER,
    ga          INTEGER,
    gd          INTEGER,
    editions    INTEGER,
    source      VARCHAR(50) DEFAULT 'RSSSF',
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS col_season_standings (
    id          SERIAL PRIMARY KEY,
    year        INTEGER NOT NULL,
    tournament  VARCHAR(50),
    position    INTEGER,
    team        VARCHAR(100),
    played      INTEGER,
    won         INTEGER,
    drawn       INTEGER,
    lost        INTEGER,
    gf          INTEGER,
    ga          INTEGER,
    gd          INTEGER,
    points      INTEGER,
    source      VARCHAR(50),
    verified    BOOLEAN DEFAULT FALSE,
    updated_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(year, tournament, team)
);

CREATE TABLE IF NOT EXISTS col_champions (
    id          SERIAL PRIMARY KEY,
    year        INTEGER,
    tournament  VARCHAR(50),
    champion    VARCHAR(100),
    runner_up   VARCHAR(100),
    source      VARCHAR(50),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE VIEW col_standing_discrepancies AS
SELECT
    a.year, a.tournament, a.team,
    a.points AS pts_rsssf, b.points AS pts_api,
    a.position AS pos_rsssf, b.position AS pos_api,
    ABS(a.points - b.points) AS pts_diff
FROM col_season_standings a
JOIN col_season_standings b
    ON a.year = b.year AND a.tournament = b.tournament AND a.team = b.team
    AND a.source = 'RSSSF' AND b.source = 'API-Football'
WHERE a.points != b.points OR a.position != b.position
ORDER BY a.year DESC, pts_diff DESC;
"""
    out = OUTPUT_DIR / "schema.sql"
    with open(out, "w") as f:
        f.write(schema)
    print(f"SQL schema → {out}")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape RSSSF Colombian football data")
    parser.add_argument("--year",    nargs="+", type=int, help="Year(s) to scrape")
    parser.add_argument("--alltime", action="store_true", help="Scrape all-time table only")
    parser.add_argument("--schema",  action="store_true", help="Generate SQL schema file")
    parser.add_argument("--matches", action="store_true", help="Also parse match results")
    args = parser.parse_args()

    if args.schema:
        generate_sql_schema()
        return

    if args.alltime:
        scrape_alltime()
        return

    if args.year:
        years = list(range(args.year[0], args.year[1] + 1)) if len(args.year) == 2 else args.year
    else:
        years = list(range(1948, 2010))

    print(f"Scraping {len(years)} season(s){'  + match results' if args.matches else ''}...")
    seasons = scrape_seasons(years, parse_matches=args.matches)
    save_seasons(seasons)
    generate_sql_schema()
    print("\nDone.")


if __name__ == "__main__":
    main()
