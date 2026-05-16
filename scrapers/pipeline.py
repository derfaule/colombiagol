"""
Colombian Football Data Pipeline — Master Runner
=================================================
Orchestrates all three scrapers and produces a unified, cross-validated dataset.

Steps:
    1. Scrape RSSSF all-time table (free, 1948–2009)
    2. Scrape RSSSF season-by-season pages (1948–2009)
    3. Scrape Wikipedia all-time table (free, 1948–present)
    4. Fetch API-Football standings (2010–present, requires key)
    5. Cross-check all sources, generate discrepancy report
    6. Output unified JSON/CSV ready for SQL import

Usage:
    pip install requests beautifulsoup4 python-dotenv
    python pipeline.py                    # full run (steps 1-5, skips API if no key)
    python pipeline.py --skip-api         # steps 1-3 only (no API key needed)
    python pipeline.py --years 1990 2000  # only scrape specific range from RSSSF
"""

import subprocess
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("../data")
OUTPUT_DIR.mkdir(exist_ok=True)


def run(cmd: list[str], cwd: Path = Path(".")) -> bool:
    print(f"\n{'─'*60}")
    print(f"  $ {' '.join(cmd)}")
    print(f"{'─'*60}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode == 0


def merge_alltime_sources():
    """
    Merge RSSSF all-time + Wikipedia all-time into a single unified table.
    Wikipedia is treated as the authoritative source for post-2009 data.
    RSSSF is authoritative for pre-2010 season-level data.
    """
    rsssf_path = OUTPUT_DIR / "alltime_standings.json"
    wiki_path  = OUTPUT_DIR / "wiki_alltime.json"

    if not rsssf_path.exists() or not wiki_path.exists():
        print("[WARN] Cannot merge — missing one or more source files")
        return

    with open(rsssf_path) as f:
        rsssf = {r["team"].lower(): r for r in json.load(f)}
    with open(wiki_path) as f:
        wiki = {r["team"].lower(): r for r in json.load(f) if r.get("team")}

    merged = []
    all_teams = set(rsssf.keys()) | set(wiki.keys())

    for team_lower in all_teams:
        r = rsssf.get(team_lower, {})
        w = wiki.get(team_lower, {})

        # Try to find best team name
        team_name = w.get("team") or r.get("team") or team_lower.title()

        merged.append({
            "team":               team_name,
            "rank_rsssf":         r.get("rank"),
            "rank_wiki":          w.get("rank"),
            "editions_rsssf":     r.get("editions"),
            "editions_wiki":      w.get("editions"),
            "pts_3pw_rsssf":      r.get("pts_3pw"),     # up to 2009
            "pts_3pw_wiki":       w.get("pts_3pw"),     # up to present
            "played_rsssf":       r.get("played"),
            "played_wiki":        w.get("played"),
            "won_wiki":           w.get("won"),
            "drawn_wiki":         w.get("drawn"),
            "lost_wiki":          w.get("lost"),
            "gf_wiki":            w.get("gf"),
            "ga_wiki":            w.get("ga"),
            "gd_wiki":            w.get("gd"),
            "has_rsssf":          bool(r),
            "has_wiki":           bool(w),
        })

    # Sort by Wikipedia rank (most current)
    merged.sort(key=lambda x: (x["rank_wiki"] or 999))

    out = OUTPUT_DIR / "alltime_unified.json"
    with open(out, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    out_csv = OUTPUT_DIR / "alltime_unified.csv"
    if merged:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=merged[0].keys())
            w.writeheader()
            w.writerows(merged)

    print(f"\n✓ Unified all-time table: {len(merged)} clubs")
    print(f"  → {out}")
    print(f"  → {out_csv}")
    return merged


def generate_summary_report():
    """Print a summary of all data collected"""
    files = {
        "RSSSF All-time":       OUTPUT_DIR / "alltime_standings.json",
        "RSSSF Seasons":        OUTPUT_DIR / "seasons_flat.csv",
        "Wikipedia All-time":   OUTPUT_DIR / "wiki_alltime.json",
        "API Standings":        OUTPUT_DIR / "api_standings.json",
        "Unified All-time":     OUTPUT_DIR / "alltime_unified.json",
        "Discrepancy Report":   OUTPUT_DIR / "discrepancy_report.json",
    }

    print(f"\n{'='*60}")
    print("  PIPELINE SUMMARY")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    for label, path in files.items():
        if path.exists():
            if path.suffix == ".json":
                with open(path) as f:
                    data = json.load(f)
                count = len(data)
            else:
                with open(path) as f:
                    count = sum(1 for _ in f) - 1  # minus header
            print(f"  ✓  {label:<25} {count:>5} records  →  {path.name}")
        else:
            print(f"  ✗  {label:<25} (not generated)")

    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-api", action="store_true", help="Skip API-Football step")
    parser.add_argument("--years", nargs=2, type=int, metavar="YEAR",
                        help="RSSSF year range (e.g. --years 1990 2000)")
    args = parser.parse_args()

    scrapers_dir = Path(".")  # run from scrapers/ directory
    year_args = ["--year"] + [str(y) for y in args.years] if args.years else []

    steps = [
        ("RSSSF All-time Table",    [sys.executable, "rsssf_scraper.py", "--alltime"]),
        ("RSSSF Season Pages",      [sys.executable, "rsssf_scraper.py"] + year_args),
        ("Wikipedia All-time",      [sys.executable, "wikipedia_scraper.py",
                                     "--compare", str(OUTPUT_DIR / "alltime_standings.json")]),
    ]

    if not args.skip_api:
        steps += [
            ("API-Football Standings (2010–2024)", [
                sys.executable, "api_football_client.py",
                "--standings", "2010", "2024",
            ]),
        ]

    for label, cmd in steps:
        print(f"\n{'█'*60}")
        print(f"  STEP: {label}")
        print(f"{'█'*60}")
        ok = run(cmd, cwd=scrapers_dir)
        if not ok:
            print(f"[WARN] Step '{label}' had errors — continuing...")

    print(f"\n{'█'*60}")
    print("  STEP: Merging all-time sources")
    print(f"{'█'*60}")
    merge_alltime_sources()

    generate_summary_report()

    print("Data pipeline complete.")
    print("Next steps:")
    print("  1. Import CSVs into your SQL database using schema.sql")
    print("  2. Run: psql -d yourdb -f ../data/schema.sql")
    print("  3. Use COPY or \\copy to load the CSVs")
    print("  4. Open the dashboard: colombia_football_dashboard.html")


if __name__ == "__main__":
    main()
