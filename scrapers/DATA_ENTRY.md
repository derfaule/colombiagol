# Data Entry Guide — Colombian Football Database

How to get data into `colombia_liga.db`. Pick the method that matches your source.

---

## Methods at a glance

| Method | Source | Coverage | Automation |
|---|---|---|---|
| RSSSF scraper | rsssf.org | Standings + matches 1948–2009 | Fully automated |
| API-Football | api-football.com | Standings + matches 2010–present | Automated, needs API key |
| Wikipedia scraper | es.wikipedia.org | All-time accumulated table | Automated |
| Manual CSV | Books, PDFs, photos | Anything | You type it |
| Book/OCR + AI | Photo a page, AI extracts | Anything | Semi-automated |

All methods ultimately write to `apps/api/colombia_liga.db`. The data flow is:

```
scraper / CSV / API → data/ (JSON/CSV) → import_to_db.py → colombia_liga.db
```

---

## Database quick reference

**Key tables and columns:**

```
competitions  id, name, slug, canonical_name, kind
seasons       id, competition_id, year, phase [Apertura|Clausura|null], label
teams         id, name, slug
matches       id, season_id, home_team_id, away_team_id, match_date, home_score, away_score, stage
standings     id, season_id, team_id, snapshot_date, position, played, won, drawn, lost,
              goals_for, goals_against, points
match_goals   id, match_id, player_id, team_id, minute, is_penalty, is_own_goal
players       id, name, position, nationality, birth_date
```

**Key rules:**
- Team names must match what's already in the `teams` table. Use the canonical short name: `América`, not `CD América de Cali` or `America`.
- Seasons need a `competition_id`. For the top league it's always `"Primera División"` (canonical_name in `competitions`).
- `phase` is either `Apertura`, `Clausura`, or `NULL` (for single-table seasons, most seasons before ~1987).
- `snapshot_date` for end-of-season standings: use `YYYY-12-31`.

**Check existing team names before entering data:**
```bash
sqlite3 apps/api/colombia_liga.db "SELECT id, name FROM teams ORDER BY name;"
```

Or from Python:
```bash
cd scrapers
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
rows = conn.execute('SELECT id, name FROM teams ORDER BY name').fetchall()
for r in rows: print(r[0], r[1])
"
```

---

## Team name matching

The importer does case-insensitive matching and a first-word fuzzy match, but you should always use names that already exist in the DB to avoid creating duplicates.

**Rules:**
- Use the short common name — not the full legal club name.
- Do not include prefixes like "CD", "CF", "AC", "Club", "Deportivo" unless that IS the canonical short name.
- Preserve Spanish accents exactly: `América`, `Atlético`, `Bogotá`.

**Common canonical names:**

| As it appears in books / RSSSF | Canonical name in DB |
|---|---|
| CD América de Cali | `América` |
| Atlético Nacional | `Nacional` |
| Club Millonarios | `Millonarios` |
| Independiente Santa Fe | `Santa Fe` |
| Independiente Medellín | `Deportivo Independiente Medellín` |
| Junior de Barranquilla | `Atlético Junior` |
| Deportivo Cali | `Deportivo Cali` |
| Deportes Tolima | `Deportes Tolima` |
| Deportivo Pereira | `Deportivo Pereira` |
| Cucutá Deportivo | `Cúcuta Deportivo` |

**Search for a name you're unsure about:**
```bash
sqlite3 apps/api/colombia_liga.db \
  "SELECT id, name FROM teams WHERE lower(name) LIKE '%america%';"
```

**Merging duplicate teams after a bad import:**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
correct_id = 5   # the one to keep — find with: SELECT id, name FROM teams
wrong_id   = 42  # the duplicate to remove
conn.execute('UPDATE matches SET home_team_id=? WHERE home_team_id=?', (correct_id, wrong_id))
conn.execute('UPDATE matches SET away_team_id=? WHERE away_team_id=?', (correct_id, wrong_id))
conn.execute('UPDATE standings SET team_id=? WHERE team_id=?', (correct_id, wrong_id))
conn.execute('UPDATE match_goals SET team_id=? WHERE team_id=?', (correct_id, wrong_id))
conn.execute('DELETE FROM teams WHERE id=?', (wrong_id,))
conn.commit()
print('Merged.')
"
```

---

## Method 1: RSSSF scraper (1948–2009)

The primary pipeline for pre-2010 data. Run from the `scrapers/` directory.

**Step 1 — Scrape season pages:**
```bash
cd scrapers

python3 rsssf_scraper.py                       # all seasons 1948-2009
python3 rsssf_scraper.py --year 1990           # single season
python3 rsssf_scraper.py --year 1990 2000      # range
python3 rsssf_scraper.py --matches             # also parse match results (slower)
python3 rsssf_scraper.py --year 1990 --matches # single season with matches
```

Produces: `../data/seasons_1948_2009.json` and `../data/seasons_flat.csv`
With `--matches`: also `../data/matches_flat.csv`

**Step 2 — Import standings into DB:**
```bash
python3 import_to_db.py --rsssf
python3 import_to_db.py --rsssf --db /custom/path/colombia_liga.db
```

**Step 3 — Import match results into DB:**
```bash
python3 import_to_db.py --matches
```

**Step 4 — Cross-check DB vs API-Football (optional):**
```bash
python3 import_to_db.py --crosscheck --years 2010 2023
```
Produces: `../data/crosscheck_report.json` and `crosscheck_report.csv`

**Full pipeline in one command:**
```bash
python3 pipeline.py                    # all steps, skips API-Football if no key
python3 pipeline.py --skip-api         # RSSSF + Wikipedia only (no API key needed)
python3 pipeline.py --years 1990 2000  # only scrape this RSSSF range
```

---

## Method 2: API-Football (2010–present)

Best source for modern data. Free tier gives 100 requests/day — enough for one full season range per day.

**Setup:**
```bash
cd scrapers
echo "API_FOOTBALL_KEY=your_key_here" > .env
```
Get a free key at https://dashboard.api-football.com. Colombia Primera A league ID is `239`.

**Fetch standings:**
```bash
cd scrapers
python3 api_football_client.py --standings 2023
python3 api_football_client.py --standings 2010 2023   # range (uses ~30 requests)
```

**Fetch match results:**
```bash
python3 api_football_client.py --results 2023
```

**Cross-check API data vs DB:**
```bash
python3 api_football_client.py --crosscheck
```

API responses are cached in `../data/.cache/` — re-running the same year doesn't burn quota.

---

## Method 3: Wikipedia scraper (all-time accumulated table)

Scrapes the Spanish Wikipedia accumulated historical table, which DIMAYOR keeps updated (unlike RSSSF, which stops around 2010). Good for verifying all-time totals.

```bash
cd scrapers
python3 wikipedia_scraper.py

# Compare against RSSSF all-time table
python3 wikipedia_scraper.py --compare ../data/alltime_standings.json
```

Produces: `../data/wiki_alltime.json`

---

## Method 4: Manual CSV entry

For data from books, newspapers, PDFs, or any source you enter by hand.

Save your CSV files in `scrapers/data/manual/`. Then import with the helper script below.

### CSV formats

#### matches — `matches_YYYY_[apertura|clausura].csv`

```csv
season_year,phase,match_date,stage,home_team,away_team,home_score,away_score
1975,,1975-03-02,Round 1,Millonarios,América,2,1
1975,,1975-03-02,Round 1,Deportivo Cali,Nacional,0,0
1990,Apertura,1990-02-11,Jornada 1,América,Millonarios,3,1
1990,Clausura,1990-08-04,Jornada 1,Nacional,Deportivo Cali,2,0
```

| Column | Format | Notes |
|---|---|---|
| `season_year` | integer | The calendar year |
| `phase` | `Apertura`, `Clausura`, or blank | Blank for pre-split seasons (before ~1987) |
| `match_date` | `YYYY-MM-DD` | Leave blank if unknown |
| `stage` | text | Round label as in the source: `Round 1`, `Jornada 3`, `Cuartos de final` |
| `home_team` | text | Canonical name |
| `away_team` | text | Canonical name |
| `home_score` | integer | Leave blank if unknown |
| `away_score` | integer | Leave blank if unknown |

#### standings — `standings_YYYY_[apertura|clausura].csv`

```csv
season_year,phase,position,team,played,won,drawn,lost,goals_for,goals_against,points
1975,,1,Deportivo Cali,34,20,10,4,58,24,50
1975,,2,Millonarios,34,18,11,5,52,28,47
1990,Apertura,1,América,18,12,4,2,35,14,28
1990,Clausura,1,Nacional,18,11,5,2,29,12,27
```

| Column | Format | Notes |
|---|---|---|
| `season_year` | integer | |
| `phase` | `Apertura`, `Clausura`, or blank | |
| `position` | integer | Final league position |
| `team` | text | Canonical name |
| `played` | integer | |
| `won` | integer | |
| `drawn` | integer | |
| `lost` | integer | |
| `goals_for` | integer | |
| `goals_against` | integer | |
| `points` | integer | Record as shown in source — pre-1994 seasons used 2pts per win |

#### goals — `goals_YYYY_[apertura|clausura].csv`

```csv
match_date,home_team,away_team,player_name,team,minute,is_penalty,is_own_goal
1975-03-02,Millonarios,América,Carlos Huertas,Millonarios,23,0,0
1975-03-02,Millonarios,América,Pedro Zape,América,67,1,0
1975-03-02,Millonarios,América,Luis Rodríguez,Millonarios,88,0,1
```

| Column | Format | Notes |
|---|---|---|
| `match_date` | `YYYY-MM-DD` | Used to look up the match |
| `home_team` | text | Used to look up the match |
| `away_team` | text | Used to look up the match |
| `player_name` | text | Will create a new player row if not found |
| `team` | text | The team credited with the goal |
| `minute` | integer | Leave blank if unknown |
| `is_penalty` | `0` or `1` | |
| `is_own_goal` | `0` or `1` | For own goals, `team` is still the team credited |

#### players — `players.csv`

```csv
name,position,nationality,birth_date
Carlos Huertas,FW,Colombian,1950-06-15
Pedro Zape,GK,Colombian,
René Higuita,GK,Colombian,1966-08-27
Marcos Canchila,DF,Colombian,1948-03-22
```

| Column | Format | Notes |
|---|---|---|
| `name` | text | Full name, must match name used in goals/lineups |
| `position` | `GK`, `DF`, `MF`, `FW` | |
| `nationality` | text | Full name in English (`Colombian`, `Argentine`) — optional |
| `birth_date` | `YYYY-MM-DD` | Optional |

### Import script

Save this as `scrapers/manual_import.py` and edit the filename and import type at the top:

```python
import csv, sqlite3
from pathlib import Path

DB   = Path("../apps/api/colombia_liga.db")
FILE = Path("data/manual/matches_1975.csv")   # <-- change this
TYPE = "matches"   # "matches", "standings", "goals", or "players"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")


def get_competition_id():
    row = conn.execute(
        "SELECT id FROM competitions WHERE canonical_name='Primera División'"
    ).fetchone()
    if not row:
        raise ValueError("Run --rsssf import first to create the competition row")
    return row["id"]


def get_or_create_season(year, phase):
    comp_id = get_competition_id()
    phase_val = phase.strip() if phase and phase.strip() else None
    row = conn.execute(
        "SELECT id FROM seasons WHERE competition_id=? AND year=? AND phase IS ?",
        (comp_id, int(year), phase_val)
    ).fetchone()
    if row:
        return row["id"]
    label = f"Primera División {year}" + (f" {phase_val}" if phase_val else "")
    cur = conn.execute(
        "INSERT INTO seasons (competition_id, year, phase, label) VALUES (?,?,?,?)",
        (comp_id, int(year), phase_val, label)
    )
    conn.commit()
    return cur.lastrowid


def get_or_create_team(name):
    name = name.strip()
    row = conn.execute("SELECT id FROM teams WHERE lower(name)=lower(?)", (name,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO teams (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def get_or_create_player(name):
    name = name.strip()
    row = conn.execute("SELECT id FROM players WHERE lower(name)=lower(?)", (name,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO players (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


inserted = 0
skipped = 0

with open(FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            if TYPE == "matches":
                season_id = get_or_create_season(row["season_year"], row.get("phase", ""))
                home_id = get_or_create_team(row["home_team"])
                away_id = get_or_create_team(row["away_team"])
                conn.execute(
                    """INSERT OR IGNORE INTO matches
                       (season_id, home_team_id, away_team_id, match_date, home_score, away_score, stage)
                       VALUES (?,?,?,?,?,?,?)""",
                    (season_id, home_id, away_id,
                     row.get("match_date") or None,
                     int(row["home_score"]) if row.get("home_score") else None,
                     int(row["away_score"]) if row.get("away_score") else None,
                     row.get("stage") or None)
                )

            elif TYPE == "standings":
                season_id = get_or_create_season(row["season_year"], row.get("phase", ""))
                team_id = get_or_create_team(row["team"])
                conn.execute(
                    """INSERT OR IGNORE INTO standings
                       (season_id, team_id, snapshot_date, position, played, won, drawn, lost,
                        goals_for, goals_against, points)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (season_id, team_id, f"{row['season_year']}-12-31",
                     int(row["position"]),
                     int(row["played"]) if row.get("played") else None,
                     int(row["won"]) if row.get("won") else None,
                     int(row["drawn"]) if row.get("drawn") else None,
                     int(row["lost"]) if row.get("lost") else None,
                     int(row["goals_for"]) if row.get("goals_for") else None,
                     int(row["goals_against"]) if row.get("goals_against") else None,
                     int(row["points"]) if row.get("points") else None)
                )

            elif TYPE == "players":
                conn.execute(
                    """INSERT OR IGNORE INTO players (name, position, nationality, birth_date)
                       VALUES (?,?,?,?)""",
                    (row["name"].strip(),
                     row.get("position") or None,
                     row.get("nationality") or None,
                     row.get("birth_date") or None)
                )

            conn.commit()
            inserted += 1
        except Exception as e:
            print(f"SKIP: {dict(row)} — {e}")
            skipped += 1

print(f"Done. Inserted: {inserted}  Skipped: {skipped}")
```

Run it:
```bash
cd scrapers
python3 manual_import.py
```

---

## Method 5: Book/photo + AI extraction

Photograph a book page or scan a document, then pass the image to Claude or ChatGPT with the prompt below. The AI returns a CSV you import with Method 4.

### Prompt to use

Copy this entire block and paste it before attaching your image:

---

> You are a sports data extraction assistant. I'm photographing a page from a Colombian football history book or newspaper. Extract all tabular data visible and return it as CSV.
>
> **Rules:**
> - Preserve Spanish accented characters (á é í ó ú ñ). Use UTF-8.
> - Team names: use the short canonical form. "América" not "CD América de Cali". "Nacional" not "Atlético Nacional". "Cali" not "Deportivo Cali" unless it's their actual short name.
> - Dates: YYYY-MM-DD. If only month/year visible, use YYYY-MM-01. If unknown, leave blank.
> - Numbers: integers only, no dots or commas as thousands separators.
> - If a cell is illegible or missing, leave it blank (two consecutive commas in CSV).
> - Output one CSV block per data type. Label each block with a comment: `# matches`, `# standings`, `# goals`, `# players`.
>
> **For standings tables**, use this exact header:
> `season_year,phase,position,team,played,won,drawn,lost,goals_for,goals_against,points`
> `phase` is `Apertura`, `Clausura`, or empty for single-table seasons.
>
> **For match results**, use this exact header:
> `season_year,phase,match_date,stage,home_team,away_team,home_score,away_score`
> `stage` is the round label as printed (e.g. `Fecha 1`, `Round 3`, `Semifinal`).
>
> **For goal scorers / top scorers lists**, use this exact header:
> `season_year,phase,player_name,team,goals,penalties,own_goals`
>
> **For player biographical data**, use this exact header:
> `name,position,nationality,birth_date`
> `position` must be one of: GK, DF, MF, FW.
>
> Return only the CSV blocks. No prose. No markdown fences.

---

**After getting the AI output:**
1. Review the team names — fix any that don't match the canonical names in the DB.
2. Copy each block into a `.csv` file in `scrapers/data/manual/`.
3. Import with the script in Method 4.

**Tip:** If the AI returns points using the old 2-point win system (pre-1994), record them as-is. Add a note in the filename like `standings_1975_2pt.csv` so you remember.

---

## Working with seasons

Before importing, make sure the target season exists:

```bash
sqlite3 apps/api/colombia_liga.db \
  "SELECT id, year, phase, label FROM seasons ORDER BY year DESC LIMIT 30;"
```

Create a missing season manually:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
# Ensure competition exists
conn.execute(\"\"\"INSERT OR IGNORE INTO competitions
  (name, slug, canonical_name, kind)
  VALUES ('Primera División','primera_division','Primera División','league')\"\"\")
comp_id = conn.execute(
  \"SELECT id FROM competitions WHERE canonical_name='Primera División'\"
).fetchone()[0]
# Create season
conn.execute(
  'INSERT OR IGNORE INTO seasons (competition_id, year, phase, label) VALUES (?,?,?,?)',
  (comp_id, 1985, 'Apertura', 'Primera División 1985 Apertura')
)
conn.commit()
print('Done.')
"
```

**Phase reference:**
- `NULL` — Single-table season (most pre-1987 seasons)
- `Apertura` — First half of a split season
- `Clausura` — Second half of a split season
- RSSSF `Liguilla` pages → mapped to `Clausura` in the importer

---

## Troubleshooting

**"DB not found" error**
Pass the path explicitly:
```bash
python3 import_to_db.py --rsssf --db /home/user/colombiagol/apps/api/colombia_liga.db
```

**"Competition not found" in manual import**
The `Primera División` row must exist in `competitions`. Run the RSSSF import once or create it manually (see Working with seasons above).

**RSSSF scraper gets 0 rows for a year**
RSSSF page formatting varies. Check the raw page manually:
`https://www.rsssf.org/tablesc/colNN.html` (NN = last 2 digits of year, e.g. `col90.html` for 1990).
Some pages have inconsistent spacing — the regex in `parse_standing_block()` requires 2+ spaces between columns.

**API-Football returns 0 results**
- Check your key: `echo $API_FOOTBALL_KEY`
- Check the `.env` file exists in `scrapers/`
- Free tier allows 100 requests/day. Cache in `../data/.cache/` avoids re-fetching.
- League ID for Colombia Primera A is `239`.

**IntegrityError on import (UNIQUE constraint failed)**
The row already exists. The importer counts these as "Skipped" — it is safe to ignore. To overwrite, delete the existing rows first:
```sql
DELETE FROM standings WHERE season_id = <season_id>;
```

**Wrong phase assigned to a season**
Check `PHASE_MAP` in `import_to_db.py`:
```python
PHASE_MAP = {
    "Apertura":  "Apertura",
    "Clausura":  "Clausura",
    "Liguilla":  "Clausura",   # playoff/closing stage maps to Clausura
    "Main":      None,          # single-table season → no phase
}
```
If RSSSF uses an unexpected label, add a new mapping here.

**Points look wrong for pre-1994 seasons**
RSSSF reports points under the 2-point win system for historical seasons. The DB stores whatever the source reports. The crosscheck against API-Football (which uses 3-point recalculations) will flag these — they are expected discrepancies, logged in `data/crosscheck_report.csv`.

**Accented characters are broken**
Your CSV editor may have saved in latin-1 instead of UTF-8. In Python, always open files with `encoding="utf-8"`. When using the SQLite CLI, ensure your terminal is UTF-8 (`locale` should show `UTF-8`).
