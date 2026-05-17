"""
All SQL queries for the API layer. Returns plain dicts — no ORM.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'colombia_liga.db'


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


# ── Competitions & seasons ────────────────────────────────────────────────

def list_competitions(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute('''
        SELECT
            c.id,
            c.canonical_name,
            c.kind,
            COUNT(DISTINCT s.id)          AS season_count,
            MIN(s.year)                   AS first_year,
            MAX(s.year)                   AS last_year,
            SUM((SELECT COUNT(*) FROM matches WHERE season_id = s.id)) AS total_matches
        FROM competitions c
        JOIN seasons s ON s.competition_id = c.id
        GROUP BY c.canonical_name, c.kind
        ORDER BY c.kind, c.canonical_name
    ''').fetchall()
    return [dict(r) for r in rows]


def list_seasons(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute('''
        SELECT
            s.id,
            s.year,
            s.phase,
            s.label,
            c.id          AS competition_id,
            c.name        AS competition_name,
            c.canonical_name,
            c.kind,
            COUNT(DISTINCT m.id)  AS match_count,
            COUNT(DISTINCT st.id) AS standing_count
        FROM seasons s
        JOIN competitions c ON c.id = s.competition_id
        LEFT JOIN matches m ON m.season_id = s.id
        LEFT JOIN standings st ON st.season_id = s.id
        GROUP BY s.id
        ORDER BY s.year DESC, c.kind, c.canonical_name
    ''').fetchall()
    return [dict(r) for r in rows]


def get_season(conn: sqlite3.Connection, season_id: int) -> dict | None:
    row = conn.execute('''
        SELECT
            s.id, s.year, s.phase, s.label,
            c.id AS competition_id, c.name AS competition_name,
            c.canonical_name, c.kind
        FROM seasons s JOIN competitions c ON c.id = s.competition_id
        WHERE s.id = ?
    ''', (season_id,)).fetchone()
    return dict(row) if row else None


def get_season_standings(conn: sqlite3.Connection, season_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            st.position, t.id AS team_id, t.name AS team_name,
            st.played, st.won, st.drawn, st.lost,
            st.goals_for, st.goals_against, st.goal_diff, st.points,
            st.stage, st.snapshot_date
        FROM standings st
        JOIN teams t ON t.id = st.team_id
        WHERE st.season_id = ?
        ORDER BY st.snapshot_date DESC, st.position
    ''', (season_id,)).fetchall()
    return [dict(r) for r in rows]


def get_season_matches(conn: sqlite3.Connection, season_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            m.id, m.match_date, m.stage, m.home_score, m.away_score,
            ht.id AS home_team_id, ht.name AS home_team,
            at.id AS away_team_id, at.name AS away_team,
            (SELECT COUNT(*) FROM match_goals WHERE match_id = m.id) AS goal_count,
            (SELECT COUNT(*) FROM match_lineups WHERE match_id = m.id) AS lineup_count
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        WHERE m.season_id = ?
        ORDER BY m.match_date, m.stage, m.id
    ''', (season_id,)).fetchall()
    return [dict(r) for r in rows]


def get_season_top_scorers(conn: sqlite3.Connection, season_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            p.id AS player_id, p.name AS player_name,
            t.id AS team_id, t.name AS team_name,
            COUNT(*) AS goals,
            SUM(CASE WHEN g.is_penalty  = 1 THEN 1 ELSE 0 END) AS penalties,
            SUM(CASE WHEN g.is_own_goal = 1 THEN 1 ELSE 0 END) AS own_goals
        FROM match_goals g
        JOIN matches m ON m.id = g.match_id
        JOIN players p ON p.id = g.player_id
        JOIN teams   t ON t.id = g.team_id
        WHERE m.season_id = ? AND g.is_own_goal = 0
        GROUP BY g.player_id, g.team_id
        ORDER BY goals DESC
        LIMIT 30
    ''', (season_id,)).fetchall()
    return [dict(r) for r in rows]


# ── Match detail ──────────────────────────────────────────────────────────

def get_match(conn: sqlite3.Connection, match_id: int) -> dict | None:
    row = conn.execute('''
        SELECT
            m.id, m.match_date, m.stage, m.home_score, m.away_score,
            ht.id AS home_team_id, ht.name AS home_team,
            at.id AS away_team_id, at.name AS away_team,
            s.id AS season_id, s.label AS season_label,
            s.year AS season_year,
            c.canonical_name AS competition_name, c.kind
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        JOIN seasons s ON s.id = m.season_id
        JOIN competitions c ON c.id = s.competition_id
        WHERE m.id = ?
    ''', (match_id,)).fetchone()
    return dict(row) if row else None


def get_match_goals(conn: sqlite3.Connection, match_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            g.minute, g.is_penalty, g.is_own_goal,
            p.id AS player_id, p.name AS player_name,
            t.id AS team_id, t.name AS team_name
        FROM match_goals g
        JOIN players p ON p.id = g.player_id
        JOIN teams   t ON t.id = g.team_id
        WHERE g.match_id = ?
        ORDER BY g.minute
    ''', (match_id,)).fetchall()
    return [dict(r) for r in rows]


def get_match_lineups(conn: sqlite3.Connection, match_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            l.position_code, l.is_starter, l.sub_in_minute, l.sub_out_minute,
            p.id AS player_id, p.name AS player_name,
            t.id AS team_id, t.name AS team_name
        FROM match_lineups l
        JOIN players p ON p.id = l.player_id
        JOIN teams   t ON t.id = l.team_id
        WHERE l.match_id = ?
        ORDER BY t.name, l.is_starter DESC, l.position_code
    ''', (match_id,)).fetchall()
    return [dict(r) for r in rows]


# ── Teams ─────────────────────────────────────────────────────────────────

def list_teams(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute('''
        SELECT
            t.id, t.name, t.slug,
            COUNT(DISTINCT ml.season_id) AS seasons_active
        FROM teams t
        LEFT JOIN (
            SELECT home_team_id AS tid, season_id FROM matches
            UNION
            SELECT away_team_id, season_id FROM matches
        ) ml ON ml.tid = t.id
        GROUP BY t.id
        ORDER BY t.name
    ''').fetchall()
    return [dict(r) for r in rows]


def get_team(conn: sqlite3.Connection, team_id: int) -> dict | None:
    row = conn.execute(
        'SELECT id, name, slug, logo_url, bio, city, founded_year FROM teams WHERE id = ?',
        (team_id,),
    ).fetchone()
    return dict(row) if row else None


def get_team_seasons(conn: sqlite3.Connection, team_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT DISTINCT
            s.id AS season_id, s.label AS season_label, s.year,
            c.canonical_name AS competition_name,
            (SELECT position FROM standings WHERE season_id=s.id AND team_id=? ORDER BY snapshot_date DESC LIMIT 1) AS final_position,
            (SELECT COUNT(*) FROM matches WHERE season_id=s.id AND (home_team_id=? OR away_team_id=?)) AS matches_played
        FROM seasons s
        JOIN competitions c ON c.id = s.competition_id
        JOIN matches m ON m.season_id = s.id
        WHERE m.home_team_id = ? OR m.away_team_id = ?
        ORDER BY s.year DESC
    ''', (team_id, team_id, team_id, team_id, team_id)).fetchall()
    return [dict(r) for r in rows]


def get_team_matches(conn: sqlite3.Connection, team_id: int, season_id: int | None = None) -> list[dict]:
    sql = '''
        SELECT
            m.id, m.match_date, m.stage, m.home_score, m.away_score,
            ht.id AS home_team_id, ht.name AS home_team,
            at.id AS away_team_id, at.name AS away_team,
            s.label AS season_label, s.year,
            (SELECT COUNT(*) FROM match_goals WHERE match_id = m.id) AS goal_count,
            (SELECT COUNT(*) FROM match_lineups WHERE match_id = m.id) AS lineup_count
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        JOIN seasons s ON s.id = m.season_id
        WHERE (m.home_team_id = ? OR m.away_team_id = ?)
    '''
    params: list = [team_id, team_id]
    if season_id is not None:
        sql += ' AND m.season_id = ?'
        params.append(season_id)
    sql += ' ORDER BY m.match_date, m.id'
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


# ── Players ───────────────────────────────────────────────────────────────

def get_player(conn: sqlite3.Connection, player_id: int) -> dict | None:
    row = conn.execute(
        'SELECT id, name, position, nationality, birth_date, height_cm, weight_kg, photo_url, bio FROM players WHERE id = ?',
        (player_id,),
    ).fetchone()
    return dict(row) if row else None


def get_player_goals(conn: sqlite3.Connection, player_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            g.minute, g.is_penalty, g.is_own_goal,
            t.id AS team_id, t.name AS team_name,
            m.id AS match_id, m.match_date,
            ht.name AS home_team, at.name AS away_team,
            m.home_score, m.away_score,
            s.label AS season_label
        FROM match_goals g
        JOIN matches m  ON m.id = g.match_id
        JOIN teams   t  ON t.id = g.team_id
        JOIN teams   ht ON ht.id = m.home_team_id
        JOIN teams   at ON at.id = m.away_team_id
        JOIN seasons s  ON s.id = m.season_id
        WHERE g.player_id = ?
        ORDER BY m.match_date, g.minute
    ''', (player_id,)).fetchall()
    return [dict(r) for r in rows]


def get_player_appearances(conn: sqlite3.Connection, player_id: int) -> list[dict]:
    rows = conn.execute('''
        SELECT
            l.position_code, l.is_starter,
            t.id AS team_id, t.name AS team_name,
            m.id AS match_id, m.match_date,
            ht.name AS home_team, at.name AS away_team,
            m.home_score, m.away_score,
            s.label AS season_label, s.year
        FROM match_lineups l
        JOIN matches m  ON m.id = l.match_id
        JOIN teams   t  ON t.id = l.team_id
        JOIN teams   ht ON ht.id = m.home_team_id
        JOIN teams   at ON at.id = m.away_team_id
        JOIN seasons s  ON s.id = m.season_id
        WHERE l.player_id = ?
        ORDER BY m.match_date
    ''', (player_id,)).fetchall()
    return [dict(r) for r in rows]


def search_players(conn: sqlite3.Connection, q: str, limit: int = 20) -> list[dict]:
    rows = conn.execute('''
        SELECT id, name, position, nationality, birth_date
        FROM players
        WHERE lower(name) LIKE lower(?)
        ORDER BY name
        LIMIT ?
    ''', (f'%{q}%', limit)).fetchall()
    return [dict(r) for r in rows]


# ── Global top scorers ────────────────────────────────────────────────────

def top_scorers(
    conn: sqlite3.Connection,
    season_id: int | None = None,
    competition_canonical: str | None = None,
    limit: int = 20,
) -> list[dict]:
    params: list = []
    filters = ['g.is_own_goal = 0']
    if season_id is not None:
        filters.append('m.season_id = ?')
        params.append(season_id)
    if competition_canonical:
        filters.append('c.canonical_name = ?')
        params.append(competition_canonical)
    where = 'WHERE ' + ' AND '.join(filters)
    params.append(limit)

    rows = conn.execute(f'''
        SELECT
            p.id AS player_id, p.name AS player_name,
            t.id AS team_id, t.name AS team_name,
            COUNT(*) AS goals
        FROM match_goals g
        JOIN matches      m ON m.id = g.match_id
        JOIN seasons      s ON s.id = m.season_id
        JOIN competitions c ON c.id = s.competition_id
        JOIN players      p ON p.id = g.player_id
        JOIN teams        t ON t.id = g.team_id
        {where}
        GROUP BY g.player_id, g.team_id
        ORDER BY goals DESC
        LIMIT ?
    ''', params).fetchall()
    return [dict(r) for r in rows]
