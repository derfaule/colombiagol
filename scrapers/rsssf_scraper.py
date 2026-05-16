from __future__ import annotations

"""
RSSSF Colombian Football Scraper (1948–2010)
=============================================
Scrapes season-by-season standings and match tables from rsssf.org.
Outputs structured JSON and CSV for loading into your SQL database.

Usage:
    python rsssf_scraper.py                   # scrape all seasons 1948-2009
    python rsssf_scraper.py --year 1990       # single season
    python rsssf_scraper.py --year 1990 2002  # range
    python rsssf_scraper.py --alltime         # all-time historical table only
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


# ─── Helpers ────────────────────────────────────────────────────────────────

def fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
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
    """
    Parses the RSSSF all-time Colombian league table.
    Format: rank. Team  pts  played  win  draw  loss  gf-ga  diff  editions

    Returns list of dicts with keys:
        rank, team, pts_3pw, played, won, drawn, lost, gf, ga, gd, editions
    """
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.find("pre")
    if not pre:
        print("[WARN] No <pre> block found in all-time page")
        return []

    rows = []
    # Pattern: "1. Millonarios  4663  2858  1278  829  751  4646-3386  1260  70"
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
    """Detect Apertura / Clausura / Finalizacion / single table labels"""
    text_lower = text.lower()
    if "apertura" in text_lower:
        return "Apertura"
    if "clausura" in text_lower or "finalizacion" in text_lower or "finalización" in text_lower:
        return "Clausura"
    if "liguilla" in text_lower:
        return "Liguilla"
    return "Main"


def parse_standing_block(lines: list[str], year: int, tournament: str) -> list[dict]:
    """
    Parse a block of lines like:
       1.America   22  11  6  5  44-24  39
    Returns list of standing dicts.
    """
    rows = []
    # Flexible pattern: pos. Team  GP  W  D  L  GF-GA  Pts
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


def parse_season(html: str, year: int) -> dict:
    """
    Parse a full season page. Returns:
    {
        "year": int,
        "tournaments": {
            "Apertura": [...standings...],
            "Clausura": [...standings...],
        },
        "champions": [str],
        "notes": str
    }
    """
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.find("pre")
    text = pre.get_text() if pre else soup.get_text()

    lines = text.splitlines()
    tournaments: dict[str, list] = {}
    current_tournament = "Main"
    current_block: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if re.match(r"^(Apertura|Clausura|Finalizaci[oó]n|Liguilla|Primera|Second)", stripped, re.I):
            if current_block:
                standings = parse_standing_block(current_block, year, current_tournament)
                if standings:
                    tournaments[current_tournament] = standings
            current_tournament = detect_tournament_name(stripped)
            current_block = []
        elif stripped:
            current_block.append(line)

    # flush last block
    if current_block:
        standings = parse_standing_block(current_block, year, current_tournament)
        if standings:
            tournaments[current_tournament] = standings

    # Try to extract champion
    champions = re.findall(r"[Cc]hampion(?:s)?:?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][\w\s.]+?)(?:\n|\[|\.)", text)
    champions = [c.strip() for c in champions]

    return {
        "year": year,
        "tournaments": tournaments,
        "champions": champions,
    }


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


def scrape_season(year: int) -> dict | None:
    url = season_url(year)
    print(f"  [{year}] {url}")
    html = fetch(url)
    if not html:
        return None
    season = parse_season(html, year)
    total = sum(len(t) for t in season["tournaments"].values())
    print(f"    → {len(season['tournaments'])} tournament(s), {total} standings rows")
    return season


def scrape_seasons(years: list[int]) -> list[dict]:
    results = []
    for year in years:
        season = scrape_season(year)
        if season:
            results.append(season)
        time.sleep(0.8)   # polite delay
    return results


def save_seasons(seasons: list[dict]):
    """Save all seasons as JSON and flat CSV"""
    out_json = OUTPUT_DIR / "seasons_1948_2009.json"
    with open(out_json, "w") as f:
        json.dump(seasons, f, indent=2, ensure_ascii=False)
    print(f"\nSaved → {out_json}")

    # Flat CSV: one row per team per tournament per year
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


# ─── SQL generation ──────────────────────────────────────────────────────────

def generate_sql_schema():
    schema = """-- ============================================================
-- Colombian Football Historical Database Schema
-- Source: RSSSF (pre-2010) + API-Football (2010+)
-- ============================================================

CREATE TABLE IF NOT EXISTS col_alltime_standings (
    id          SERIAL PRIMARY KEY,
    rank        INTEGER,
    team        VARCHAR(100),
    pts_3pw     INTEGER,    -- points under 3-pts-per-win system
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
    tournament  VARCHAR(50),   -- 'Apertura', 'Clausura', 'Main'
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
    source      VARCHAR(50),   -- 'RSSSF' | 'API-Football' | 'manual'
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

-- Cross-check view: flag mismatches between sources
CREATE OR REPLACE VIEW col_standing_discrepancies AS
SELECT
    a.year, a.tournament, a.team,
    a.points   AS pts_rsssf,
    b.points   AS pts_api,
    a.position AS pos_rsssf,
    b.position AS pos_api,
    ABS(a.points - b.points) AS pts_diff
FROM col_season_standings a
JOIN col_season_standings b
    ON  a.year       = b.year
    AND a.tournament = b.tournament
    AND a.team       = b.team
    AND a.source     = 'RSSSF'
    AND b.source     = 'API-Football'
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
    parser.add_argument("--year", nargs="+", type=int, help="Year(s) to scrape")
    parser.add_argument("--alltime", action="store_true", help="Scrape all-time table only")
    parser.add_argument("--schema", action="store_true", help="Generate SQL schema file")
    args = parser.parse_args()

    if args.schema:
        generate_sql_schema()
        return

    if args.alltime:
        scrape_alltime()
        return

    if args.year:
        if len(args.year) == 2:
            years = list(range(args.year[0], args.year[1] + 1))
        else:
            years = args.year
    else:
        years = list(range(1948, 2010))

    print(f"Scraping {len(years)} season(s)...")
    seasons = scrape_seasons(years)
    save_seasons(seasons)
    generate_sql_schema()
    print("\nDone.")


if __name__ == "__main__":
    main()
