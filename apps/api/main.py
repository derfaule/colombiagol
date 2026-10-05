from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import queries

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "logos").mkdir(exist_ok=True)
(STATIC_DIR / "players").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.conn = queries.get_conn()
    yield
    app.state.conn.close()


app = FastAPI(title='Colombia Liga API', version='1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET'],
    allow_headers=['*'],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def conn():
    return app.state.conn


# ── Competitions & seasons ────────────────────────────────────────────────

@app.get('/api/competitions')
def get_competitions():
    return queries.list_competitions(conn())


@app.get('/api/seasons')
def get_seasons():
    return queries.list_seasons(conn())


@app.get('/api/seasons/{season_id}')
def get_season(season_id: int):
    season = queries.get_season(conn(), season_id)
    if not season:
        raise HTTPException(404, 'Season not found')
    return {
        **season,
        'standings': queries.get_season_standings(conn(), season_id),
        'matches':   queries.get_season_matches(conn(), season_id),
        'top_scorers': queries.get_season_top_scorers(conn(), season_id),
    }


@app.get('/api/seasons/{season_id}/standings')
def get_standings(season_id: int):
    season = queries.get_season(conn(), season_id)
    if not season:
        raise HTTPException(404, 'Season not found')
    return queries.get_season_standings(conn(), season_id)


@app.get('/api/seasons/{season_id}/matches')
def get_season_matches(season_id: int):
    season = queries.get_season(conn(), season_id)
    if not season:
        raise HTTPException(404, 'Season not found')
    return queries.get_season_matches(conn(), season_id)


@app.get('/api/seasons/{season_id}/top-scorers')
def get_top_scorers_for_season(season_id: int):
    season = queries.get_season(conn(), season_id)
    if not season:
        raise HTTPException(404, 'Season not found')
    return queries.get_season_top_scorers(conn(), season_id)


# ── Matches ───────────────────────────────────────────────────────────────

@app.get('/api/matches/{match_id}')
def get_match(match_id: int):
    match = queries.get_match(conn(), match_id)
    if not match:
        raise HTTPException(404, 'Match not found')
    goals   = queries.get_match_goals(conn(), match_id)
    lineups = queries.get_match_lineups(conn(), match_id)

    home_id = match['home_team_id']
    away_id = match['away_team_id']
    return {
        **match,
        'goals': goals,
        'home_lineup': [l for l in lineups if l['team_id'] == home_id],
        'away_lineup': [l for l in lineups if l['team_id'] == away_id],
    }


# ── Teams ─────────────────────────────────────────────────────────────────

@app.get('/api/teams')
def get_teams():
    return queries.list_teams(conn())


@app.get('/api/teams/{team_id}')
def get_team(team_id: int, season_id: Optional[int] = Query(None)):
    team = queries.get_team(conn(), team_id)
    if not team:
        raise HTTPException(404, 'Team not found')
    return {
        **team,
        'seasons':  queries.get_team_seasons(conn(), team_id),
        'matches':  queries.get_team_matches(conn(), team_id, season_id),
    }


# ── Players ───────────────────────────────────────────────────────────────

@app.get('/api/players/search')
def search_players(q: str = Query(..., min_length=2)):
    return queries.search_players(conn(), q)


@app.get('/api/players/{player_id}')
def get_player(player_id: int):
    player = queries.get_player(conn(), player_id)
    if not player:
        raise HTTPException(404, 'Player not found')
    goals       = queries.get_player_goals(conn(), player_id)
    appearances = queries.get_player_appearances(conn(), player_id)
    return {
        **player,
        'total_goals':       len(goals),
        'total_appearances': len(appearances),
        'goals':             goals,
        'appearances':       appearances,
    }


# ── Top scorers (global / filtered) ──────────────────────────────────────

@app.get('/api/top-scorers')
def get_top_scorers(
    season_id:    Optional[int] = Query(None),
    competition:  Optional[str] = Query(None),
    limit:        int           = Query(20, ge=1, le=100),
):
    return queries.top_scorers(conn(), season_id, competition, limit)
