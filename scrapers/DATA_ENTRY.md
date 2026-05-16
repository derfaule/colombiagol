# Data Entry Guide — Colombia Liga DB

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

---

## Database quick reference

The DB lives at `apps/api/colombia_liga.db`. All imports go through that file.

**Key rules:**
- Team names must match what's already in the `teams` table. Use the canonical short name: `América`, not `CD América de Cali` or `America`.
- Seasons need a `competition_id`. For the top league it's always `"Primera División"` (canonical_name in `competitions`).
- `phase` is either `Apertura`, `Clausura`, or `NULL` (for single-table seasons pre-1990s).
- `snapshot_date` for historical/end-of-season standings: use `YYYY-12-31`.

**Check existing team names before entering data:**
```bash
cd scrapers
python3 -c "
import sqlite3, sys
conn = sqlite3.connect('../apps/api/colombia_liga.db')
rows = conn.execute('SELECT id, name FROM teams ORDER BY name').fetchall()
for r in rows: print(r[0], r[1])
"
```

---

## Method 1: RSSSF scraper (1948–2009)

The primary pipeline for pre-2010 data.

**Step 1 — Scrape standings only:**
```bash
cd scrapers
python3 rsssf_scraper.py                    # all seasons 1948-2009
python3 rsssf_scraper.py --year 1990        # single season
python3 rsssf_scraper.py --year 1990 2000   # range
```
Produces: `../data/seasons_1948_2009.json` and `../data/seasons_flat.csv`

**Step 2 — Scrape standings + match results:**
```bash
python3 rsssf_scraper.py --matches          # all seasons with match results
python3 rsssf_scraper.py --year 1990 --matches
```
Produces: also `../data/matches_flat.csv`

**Step 3 — Import standings into DB:**
```bash
python3 import_to_db.py --rsssf
python3 import_to_db.py --rsssf --db /custom/path/colombia_liga.db
```

**Step 4 — Import match results into DB:**
```bash
python3 import_to_db.py --matches
```

**Step 5 — Cross-check against API-Football (optional):**
```bash
python3 import_to_db.py --crosscheck --years 2010 2023
```
Produces: `../data/crosscheck_report.json` and `crosscheck_report.csv`

**Full pipeline in one command:**
```bash
python3 pipeline.py                    # all steps, skips API if no key
python3 pipeline.py --skip-api         # RSSSF + Wikipedia only
python3 pipeline.py --years 1990 2000  # only scrape this RSSSF range
```

---

## Method 2: API-Football (2010–present)

Requires a free account at https://dashboard.api-football.com (100 req/day on free tier).

**Setup:**
```bash
cd scrapers
echo "API_FOOTBALL_KEY=your_key_here" > .env
```

**Fetch standings:**
```bash
python3 api_football_client.py --standings 2023
python3 api_football_client.py --standings 2010 2023   # range
```

**Fetch match results:**
```bash
python3 api_football_client.py --results 2023
```

**Cross-check API data vs DB:**
```bash
python3 api_football_client.py --crosscheck
```

API responses are cached in `../data/.cache/` so re-running doesn't burn quota.

---

## Method 3: Wikipedia scraper (all-time table)

Scrapes the Spanish Wikipedia accumulated historical table. Good for verifying all-time totals.

```bash
cd scrapers
python3 wikipedia_scraper.py

# Compare against RSSSF all-time table
python3 wikipedia_scraper.py --compare ../data/alltime_standings.json
```
Produces: `../data/wiki_alltime.json`

---

## Method 4: Manual CSV entry

For data from books, PDFs, scanned tables, or any source you type by hand. Create a CSV, then import it with a small Python script.

### CSV formats

#### Matches
Filename: `matches_YYYY_[apertura|clausura].csv`

```
season_year,phase,match_date,stage,home_team,away_team,home_score,away_score
1975,,1975-03-02,Round 1,Millonarios,América,2,1
1975,,1975-03-02,Round 1,Cali,Nacional,0,0
1990,Apertura,1990-02-11,Jornada 1,América,Millonarios,3,1
1990,Clausura,1990-08-04,Jornada 1,Nacional,Cali,2,0
```

- `phase`: leave empty for pre-Apertura/Clausura seasons (before ~1987). Use `Apertura` or `Clausura` otherwise.
- `stage`: the round label as it appears in the source (e.g. `Round 1`, `Jornada 3`, `Cuartos de final`).
- `match_date`: always `YYYY-MM-DD`. If unknown, leave blank.
- `home_score` / `away_score`: integer. Leave blank if the result is unknown.

#### Standings (end-of-season table)
Filename: `standings_YYYY_[apertura|clausura].csv`

```
season_year,phase,position,team,played,won,drawn,lost,goals_for,goals_against,points
1975,,1,Deportivo Cali,34,20,10,4,58,24,50
1975,,2,Millonarios,34,18,11,5,52,28,47
1990,Apertura,1,América,18,12,4,2,35,14,28
1990,Clausura,1,Nacional,18,11,5,2,29,12,27
```

#### Goals (match-by-match)
Filename: `goals_matchID_or_date.csv`

```
match_date,home_team,away_team,player_name,team,minute,is_penalty,is_own_goal
1975-03-02,Millonarios,América,Carlos Huertas,Millonarios,23,0,0
1975-03-02,Millonarios,América,Pedro Zape,América,67,1,0
1975-03-02,Millonarios,América,Luis Rodríguez,Millonarios,88,0,1
```

- `is_penalty`: 1 if penalty, 0 if not.
- `is_own_goal`: 1 if own goal, 0 if not.
- `minute`: integer. Leave blank if unknown.

#### Players
Filename: `players.csv`

```
name,position,nationality,birth_date
Carlos Huertas,FW,Colombian,1950-06-15
Pedro Zape,GK,Colombian,
Marcos Canchila,DF,Colombian,1948-03-22
```

- `position`: use `GK`, `DF`, `MF`, or `FW`.
- `birth_date`: `YYYY-MM-DD` or leave blank.
- `nationality`: full name in English (`Colombian`, `Argentine`, `Brazilian`).

### Importing a manual CSV

Save the CSV to `scrapers/data/manual/`, then run this script (edit the filename and type):

```bash
cd scrapers
python3 - <<'EOF'
import csv, sqlite3
from pathlib import Path

DB = Path("../apps/api/colombia_liga.db")
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")

# ── helpers ──────────────────────────────────────────────────────
def get_team_id(name):
    row = conn.execute("SELECT id FROM teams WHERE lower(name)=lower(?)", (name,)).fetchone()
    if row: return row["id"]
    cur = conn.execute("INSERT INTO teams (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid

def get_season_id(year, phase):
    comp = conn.execute(
        "SELECT id FROM competitions WHERE canonical_name='Primera División'"
    ).fetchone()
    if not comp: raise ValueError("Competition not found — run --rsssf import first")
    row = conn.execute(
        "SELECT id FROM seasons WHERE competition_id=? AND year=? AND phase IS ?",
        (comp["id"], int(year), phase if phase else None)
    ).fetchone()
    if row: return row["id"]
    label = f"Primera División {year}" + (f" {phase}" if phase else "")
    cur = conn.execute(
        "INSERT INTO seasons (competition_id, year, phase, label) VALUES (?,?,?,?)",
        (comp["id"], int(year), phase if phase else None, label)
    )
    conn.commit()
    return cur.lastrowid

# ── import matches ────────────────────────────────────────────────
with open("data/manual/matches_1975.csv") as f:
    for row in csv.DictReader(f):
        season_id = get_season_id(row["season_year"], row["phase"] or None)
        home_id   = get_team_id(row["home_team"])
        away_id   = get_team_id(row["away_team"])
        conn.execute(
            """INSERT OR IGNORE INTO matches
               (season_id, home_team_id, away_team_id, match_date, home_score, away_score, stage)
               VALUES (?,?,?,?,?,?,?)""",
            (season_id, home_id, away_id,
             row["match_date"] or None,
             int(row["home_score"]) if row["home_score"] else None,
             int(row["away_score"]) if row["away_score"] else None,
             row["stage"] or None)
        )
        conn.commit()
print("Done.")
EOF
```

---

## Method 5: Book/photo + AI extraction

When you have a book or printed table, photograph the page and pass it to Claude or ChatGPT with the prompt below. It will return a CSV you can then import using Method 4.

### AI extraction prompt

Copy this entire prompt and attach your photo:

---

> You are a sports data extraction assistant. I am photographing a page from a Colombian football history book. Extract all tabular data you can see and return it as CSV.
>
> **Rules:**
> - Use UTF-8. Preserve Spanish accented characters (á é í ó ú ñ Ü).
> - Team names: use the short canonical form. "América" not "CD América de Cali". "Nacional" not "Atlético Nacional". "Cali" not "Deportivo Cali" unless it's their actual short name.
> - Dates: YYYY-MM-DD format. If only month/year visible, use YYYY-MM-01.
> - Numbers: integers only, no dots or commas.
> - If a cell is illegible or missing, leave it blank (two consecutive commas).
> - Output one CSV block per data type found (matches, standings, goals, players).
>
> **For standings tables**, use this header:
> `season_year,phase,position,team,played,won,drawn,lost,goals_for,goals_against,points`
> phase is Apertura, Clausura, or empty if single-table season.
>
> **For match results**, use this header:
> `season_year,phase,match_date,stage,home_team,away_team,home_score,away_score`
>
> **For goal scorers / top scorers**, use this header:
> `season_year,phase,player_name,team,goals,penalties,own_goals`
>
> **For player bio data**, use this header:
> `name,position,nationality,birth_date`
> position is GK, DF, MF, or FW.
>
> Return only the CSV blocks, no prose. Label each block with a comment line like `# matches` or `# standings`.

---

After you get the output:
1. Copy each CSV block into a `.csv` file in `scrapers/data/manual/`.
2. Double-check team names against the DB (see the query at the top of this guide).
3. Import using the script in Method 4.

---

## Team name matching

The DB uses short canonical names. When entering data, always check whether a variant already exists:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
# Find all teams with 'america' in the name
rows = conn.execute(\"SELECT id, name FROM teams WHERE lower(name) LIKE '%america%'\").fetchall()
for r in rows: print(r)
"
```

**Common canonical names:**

| In books/RSSSF | Canonical in DB |
|---|---|
| CD América de Cali | América |
| Atlético Nacional | Nacional |
| Deportivo Cali | Deportivo Cali |
| Club Millonarios | Millonarios |
| Independiente Santa Fe | Santa Fe |
| Independiente Medellín | Deportivo Independiente Medellín |
| Deportes Tolima | Deportes Tolima |
| Junior de Barranquilla | Atlético Junior |
| Deportivo Pereira | Deportivo Pereira |

If a team name from your source doesn't match anything in the DB, the importer will create a new team row. After importing, check for duplicates:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
rows = conn.execute('SELECT name FROM teams ORDER BY name').fetchall()
for r in rows: print(r[0])
" | sort -f
```

If you see `América` and `America` as separate rows, fix it:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
# Find the correct id (the one with more data)
correct_id = 1   # replace with real id
wrong_id   = 42  # replace with real id
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

## Troubleshooting

**"DB not found" error**
```
[ERROR] DB not found at .../colombia_liga.db
```
Pass the path explicitly: `python3 import_to_db.py --rsssf --db /home/user/colombiagol/apps/api/colombia_liga.db`

**"Competition not found" in manual import**
The `Primera División` row must exist in `competitions` before you can create seasons. Run `--rsssf` import at least once, or insert it:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('../apps/api/colombia_liga.db')
conn.execute(\"INSERT OR IGNORE INTO competitions (name, slug, canonical_name, kind) VALUES ('Primera División','primera_division','Primera División','league')\")
conn.commit()
"
```

**RSSSF scraper gets no rows for a season**
RSSSF page format varies by year. Check the raw page: `https://www.rsssf.org/tablesc/col90.html` (replace 90 with 2-digit year). Some pages have different column spacing. The regex in `parse_standing_block()` requires at least 2 spaces between columns.

**API-Football returns 0 results**
- Confirm your key is set: `echo $API_FOOTBALL_KEY`
- Free tier allows 100 requests/day. The cache in `../data/.cache/` avoids repeated calls.
- League ID for Colombia Primera A is `239`.

**IntegrityError on import**
Usually a duplicate — the row already exists. The importer catches these and counts them as "Skipped". If you want to overwrite, delete the existing rows first:
```sql
DELETE FROM standings WHERE season_id = <id>;
```

**Wrong phase assigned**
Check `PHASE_MAP` in `import_to_db.py`. RSSSF uses "Liguilla" for some closing playoffs — these map to `Clausura`. If a season has both "Clausura" and "Liguilla" blocks, they will be merged into one season. Verify in the DB after import.
