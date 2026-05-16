"""
Wikipedia All-Time Colombian Football Table Scraper
===================================================
Scrapes the Spanish Wikipedia historical standings table, which is updated
regularly by DIMAYOR and covers 1948 to present (unlike RSSSF which stops ~2010).

This is your best free source for post-2010 all-time accumulated stats.

Usage:
    python wikipedia_scraper.py
    python wikipedia_scraper.py --compare ../data/alltime_standings.json
"""

import requests
import json
import csv
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

WIKI_URL = (
    "https://es.wikipedia.org/wiki/"
    "Anexo:Tabla_hist%C3%B3rica_de_la_Categor%C3%ADa_Primera_A"
)
OUTPUT_DIR = Path("../data")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (research/data-archival)"}


def fetch_wiki_table() -> list[dict]:
    resp = requests.get(WIKI_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find the main wikitable (first sortable table)
    table = soup.find("table", class_="wikitable")
    if not table:
        print("[ERROR] Could not find wikitable on page")
        return []

    headers_row = table.find("tr")
    header_cells = [th.get_text(strip=True) for th in headers_row.find_all(["th", "td"])]
    print(f"  Columns found: {header_cells}")

    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cells) < 8:
            continue

        def safe_int(val):
            try:
                return int(val.replace(".", "").replace(",", ""))
            except:
                return None

        def safe_float(val):
            try:
                return float(val.replace(",", "."))
            except:
                return None

        row = {
            "rank":          safe_int(cells[0]) if cells[0].isdigit() else None,
            "team":          cells[1] if len(cells) > 1 else None,
            "editions":      safe_int(cells[2]) if len(cells) > 2 else None,
            "played":        safe_int(cells[3]) if len(cells) > 3 else None,
            "won":           safe_int(cells[4]) if len(cells) > 4 else None,
            "drawn":         safe_int(cells[5]) if len(cells) > 5 else None,
            "lost":          safe_int(cells[6]) if len(cells) > 6 else None,
            "gf":            safe_int(cells[7]) if len(cells) > 7 else None,
            "ga":            safe_int(cells[8]) if len(cells) > 8 else None,
            "gd":            safe_int(cells[9]) if len(cells) > 9 else None,
            "pts_historical": safe_float(cells[10]) if len(cells) > 10 else None,
            "pts_3pw":       safe_int(cells[11]) if len(cells) > 11 else None,
            "source":        "Wikipedia",
        }
        if row["team"]:
            rows.append(row)

    return rows


def compare_with_rsssf(wiki_rows: list[dict], rsssf_path: str) -> list[dict]:
    """Compare Wikipedia all-time table against RSSSF all-time table"""
    with open(rsssf_path) as f:
        rsssf_rows = json.load(f)

    rsssf_by_team = {r["team"].lower(): r for r in rsssf_rows}
    wiki_by_team  = {r["team"].lower(): r for r in wiki_rows if r["team"]}

    discrepancies = []
    for team_key, wiki in wiki_by_team.items():
        # fuzzy match: try exact, then partial
        rsssf = rsssf_by_team.get(team_key)
        if not rsssf:
            # try partial match
            matches = [v for k, v in rsssf_by_team.items() if team_key[:6] in k or k[:6] in team_key]
            rsssf = matches[0] if matches else None

        if not rsssf:
            discrepancies.append({
                "team":    wiki["team"],
                "status":  "ONLY_IN_WIKIPEDIA",
                "wiki_pts": wiki.get("pts_3pw"),
                "rsssf_pts": None,
            })
            continue

        wiki_pts  = wiki.get("pts_3pw") or 0
        rsssf_pts = rsssf.get("pts_3pw") or 0
        diff      = abs(wiki_pts - rsssf_pts)

        # RSSSF stops at 2009, so Wikipedia will always have more points
        # Flag only suspiciously large gaps relative to editions difference
        wiki_eds  = wiki.get("editions") or 0
        rsssf_eds = rsssf.get("editions") or 0
        extra_eds = wiki_eds - rsssf_eds  # seasons after RSSSF cutoff
        expected_extra_pts = extra_eds * 50  # rough max pts per season

        if diff > expected_extra_pts + 100:
            discrepancies.append({
                "team":       wiki["team"],
                "status":     "SUSPICIOUS_GAP",
                "wiki_pts":   wiki_pts,
                "rsssf_pts":  rsssf_pts,
                "diff":       diff,
                "expected_extra": expected_extra_pts,
            })

    return discrepancies


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", metavar="RSSSF_JSON",
                        help="Path to alltime_standings.json from RSSSF scraper")
    args = parser.parse_args()

    print("→ Fetching Wikipedia all-time table...")
    rows = fetch_wiki_table()
    print(f"  Found {len(rows)} clubs")

    out_json = OUTPUT_DIR / "wiki_alltime.json"
    out_csv  = OUTPUT_DIR / "wiki_alltime.csv"

    with open(out_json, "w") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"  Saved → {out_json}")

    if rows:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print(f"  Saved → {out_csv}")

    if args.compare:
        print(f"\n→ Comparing against RSSSF data ({args.compare})...")
        disc = compare_with_rsssf(rows, args.compare)
        if disc:
            print(f"  ⚠  {len(disc)} discrepancies:")
            for d in disc:
                print(f"    {d['team']}: {d['status']} "
                      f"(wiki={d.get('wiki_pts')}, rsssf={d.get('rsssf_pts')})")
        else:
            print("  ✓ No suspicious discrepancies found")


if __name__ == "__main__":
    main()
