# colombiagol

Historical database of Colombian top-flight football (1948–present). Standings, match results, scorers, and player data for the Primera División / Categoría Primera A.

---

## What's in the database

| Data type | Coverage | Source |
|---|---|---|
| Season standings | 1948–2009 | RSSSF |
| Season standings | 2010–present | API-Football |
| Match results | 1948–2009 (partial) | RSSSF |
| Match results | 2010–present | API-Football |
| All-time accumulated table | 1948–present | Wikipedia ES |
| Goal scorers | Varies by season | API-Football / manual |
| Player data | Partial | API-Football / manual |

Data for match-level detail (scorers, lineups) before 2010 is sparse — that era mostly has standings only.

---

## Architecture

```
┌─────────────────┐     HTTPS      ┌─────────────────┐
│   apps/web      │ ──────────────▶│   apps/api      │
│   Next.js       │                │   FastAPI        │
│   Vercel        │                │   Render         │
└─────────────────┘                └────────┬────────┘
                                            │ reads
                                   ┌────────▼────────┐
                                   │ colombia_liga.db │
                                   │ SQLite (on disk) │
                                   └─────────────────┘
                                            ▲
                                            │ import_to_db.py
                                   ┌────────┴────────┐
                                   │  scrapers/      │
                                   │  runs locally   │
                                   └─────────────────┘
```

- **Frontend** (`apps/web/`) — Next.js app deployed to Vercel. Fetches data from the API at build time and/or at runtime.
- **API** (`apps/api/`) — FastAPI app deployed to Render. Reads from a SQLite file bundled with the service. Exposes JSON endpoints at `/api/*`.
- **Scrapers** (`scrapers/`) — Python scripts that pull data from RSSSF, API-Football, and Wikipedia, then write to `colombia_liga.db`. Run locally, then push the updated DB file.

**Why SQLite on Render?** The dataset is read-heavy and append-only. SQLite eliminates a managed database dependency and deploys with zero extra config. Render persists the file between deploys as long as you commit it to the repo (or mount a disk).

---

## API endpoints

Base URL (production): configured in `apps/web/` environment variables.

| Method | Path | Description |
|---|---|---|
| GET | `/api/competitions` | List all competitions |
| GET | `/api/seasons` | List all seasons |
| GET | `/api/seasons/{id}` | Season detail with standings, matches, top scorers |
| GET | `/api/seasons/{id}/standings` | Standings table for a season |
| GET | `/api/seasons/{id}/matches` | Match list for a season |
| GET | `/api/seasons/{id}/top-scorers` | Top scorers for a season |
| GET | `/api/matches/{id}` | Match detail with goals and lineups |
| GET | `/api/teams` | List all teams |
| GET | `/api/teams/{id}` | Team detail with season history and matches |
| GET | `/api/players/search?q=` | Search players by name |
| GET | `/api/players/{id}` | Player detail with goals and appearances |
| GET | `/api/top-scorers` | Global top scorers, filterable by season/competition |

---

## Local development

### Prerequisites

- Node.js 18+
- pnpm
- Python 3.10+

### Setup

```bash
git clone <repo>
cd colombiagol

# Install JS dependencies
pnpm install

# Install Python scraper dependencies
cd scrapers
pip install -r requirements.txt
cd ..
```

### Run the API locally

```bash
cd apps/api
uvicorn main:app --reload --port 8000
```

API is now at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

The API reads `apps/api/colombia_liga.db`. If the file doesn't exist yet, run the RSSSF import first (see Data pipeline below).

### Run the web frontend locally

```bash
pnpm dev
```

The web app runs at `http://localhost:3000`. Set the API base URL in `apps/web/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run both together

```bash
pnpm dev   # starts both apps via Turborepo
```

---

## Data pipeline

This is how you add or update data. See `scrapers/DATA_ENTRY.md` for the full guide with CSV formats, examples, and troubleshooting.

### Data sources

| Source | Script | What it provides |
|---|---|---|
| RSSSF | `rsssf_scraper.py` | Standings + matches 1948–2009 |
| API-Football | `api_football_client.py` | Standings + matches 2010–present |
| Wikipedia ES | `wikipedia_scraper.py` | All-time accumulated table |
| Manual CSV | `manual_import.py` | Anything from books, PDFs, photos |
| Book + AI | Prompt in DATA_ENTRY.md | Bulk entry from scanned pages |

### Quick start: initial DB population

```bash
cd scrapers

# 1. Scrape RSSSF (1948-2009 standings)
python3 rsssf_scraper.py

# 2. Import standings into DB
python3 import_to_db.py --rsssf

# 3. Scrape and import match results (optional, slower)
python3 rsssf_scraper.py --matches
python3 import_to_db.py --matches

# 4. Fetch modern data from API-Football (needs key)
echo "API_FOOTBALL_KEY=your_key_here" > .env
python3 api_football_client.py --standings 2010 2024

# 5. Cross-check DB vs API-Football
python3 import_to_db.py --crosscheck --years 2010 2024
```

Or run everything at once:
```bash
python3 pipeline.py           # full run (RSSSF + Wikipedia + API-Football)
python3 pipeline.py --skip-api  # RSSSF + Wikipedia only (no API key needed)
```

### Enrichment workflow

After adding data to the DB locally:

1. Make sure the data looks right:
   ```bash
   sqlite3 apps/api/colombia_liga.db "SELECT COUNT(*) FROM matches;"
   sqlite3 apps/api/colombia_liga.db "SELECT year, phase, label FROM seasons ORDER BY year DESC LIMIT 10;"
   ```

2. Commit the updated DB file:
   ```bash
   git add apps/api/colombia_liga.db
   git commit -m "Add 1975 season matches"
   git push
   ```

3. Render auto-redeploys the API. Vercel auto-redeploys the frontend. No manual steps needed.

**Note:** `colombia_liga.db` is committed to the repo. This works well for a dataset that's a few hundred MB or less. If it grows large, switch to Render's persistent disk and deploy the DB separately.

---

## Deployment

### API — Render

The API is deployed to Render using `apps/api/railway.toml` for build configuration.

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on-failure"
```

**Setup on Render:**
1. Create a new Web Service and connect your GitHub repo.
2. Set root directory to `apps/api`.
3. Render picks up `railway.toml` automatically.
4. No environment variables required for the API itself (it reads the DB from disk).

**To update the DB on Render:** Push to main. Render redeploys and picks up the updated `colombia_liga.db` from the repo.

### Frontend — Vercel

**Setup on Vercel:**
1. Import the repo and set the root directory to `apps/web`.
2. Framework preset: Next.js.
3. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com
   ```
4. Deploy. Vercel auto-deploys on every push to main.

---

## Project structure

```
colombiagol/
├── apps/
│   ├── api/
│   │   ├── main.py              # FastAPI app + route definitions
│   │   ├── queries.py           # All SQL queries (no ORM)
│   │   ├── colombia_liga.db     # SQLite database (committed to repo)
│   │   ├── requirements.txt
│   │   └── railway.toml         # Render deploy config
│   └── web/
│       ├── app/                 # Next.js app router
│       ├── components/
│       └── ...
├── scrapers/
│   ├── rsssf_scraper.py         # Scrapes rsssf.org (1948-2009)
│   ├── api_football_client.py   # Fetches from api-football.com (2010+)
│   ├── wikipedia_scraper.py     # Scrapes Wikipedia ES all-time table
│   ├── import_to_db.py          # Loads scraped data into the DB
│   ├── pipeline.py              # Runs all scrapers in sequence
│   ├── requirements.txt
│   ├── DATA_ENTRY.md            # Full data entry guide
│   └── data/                   # Intermediate JSON/CSV files (gitignored)
├── packages/                   # Shared UI components (shadcn)
├── turbo.json
└── package.json
```

---

## DB schema

```sql
competitions  (id, name, slug, canonical_name, kind)
seasons       (id, competition_id, year, phase, label)
teams         (id, name, slug)
matches       (id, season_id, home_team_id, away_team_id, match_date,
               home_score, away_score, stage)
standings     (id, season_id, team_id, snapshot_date, position, played,
               won, drawn, lost, goals_for, goals_against, points)
match_goals   (id, match_id, player_id, team_id, minute, is_penalty, is_own_goal)
match_lineups (id, match_id, player_id, team_id, position_code, is_starter,
               sub_in_minute, sub_out_minute)
players       (id, name, position, nationality, birth_date, height_cm, weight_kg)
```

`phase` is `Apertura`, `Clausura`, or `NULL` (single-table seasons, mostly pre-1987).
`snapshot_date` for end-of-season standings is set to `YYYY-12-31`.
