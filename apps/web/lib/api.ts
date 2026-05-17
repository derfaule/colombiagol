const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { next: { revalidate: 60 } })
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

export interface Competition {
  id: number
  canonical_name: string
  kind: string
  season_count: number
  first_year: number
  last_year: number
  total_matches: number
}

export interface Season {
  id: number
  year: number
  phase: string | null
  label: string
  competition_id: number
  competition_name: string
  canonical_name: string
  kind: string
  match_count: number
  standing_count: number
}

export interface Standing {
  position: number
  team_id: number
  team_name: string
  played: number
  won: number
  drawn: number
  lost: number
  goals_for: number
  goals_against: number
  goal_diff: number
  points: number
  stage: string | null
  snapshot_date: string
}

export interface MatchSummary {
  id: number
  match_date: string | null
  stage: string | null
  home_score: number | null
  away_score: number | null
  home_team_id: number
  home_team: string
  away_team_id: number
  away_team: string
  goal_count: number
  lineup_count: number
}

export interface Goal {
  minute: number | null
  is_penalty: number
  is_own_goal: number
  player_id: number
  player_name: string
  team_id: number
  team_name: string
}

export interface LineupEntry {
  position_code: string | null
  is_starter: number
  sub_in_minute: number | null
  sub_out_minute: number | null
  player_id: number
  player_name: string
  team_id: number
  team_name: string
}

export interface Match {
  id: number
  match_date: string | null
  stage: string | null
  home_score: number | null
  away_score: number | null
  home_team_id: number
  home_team: string
  away_team_id: number
  away_team: string
  season_id: number
  season_label: string
  season_year: number
  competition_name: string
  kind: string
  goals: Goal[]
  home_lineup: LineupEntry[]
  away_lineup: LineupEntry[]
}

export interface TopScorer {
  player_id: number
  player_name: string
  team_id: number
  team_name: string
  goals: number
  penalties?: number
  own_goals?: number
}

export interface SeasonDetail {
  id: number
  year: number
  phase: string | null
  label: string
  competition_id: number
  competition_name: string
  canonical_name: string
  kind: string
  standings: Standing[]
  matches: MatchSummary[]
  top_scorers: TopScorer[]
}

export interface Team {
  id: number
  name: string
  slug: string
  seasons_active: number
}

export interface TeamDetail {
  id: number
  name: string
  slug: string
  logo_url: string | null
  bio: string | null
  city: string | null
  founded_year: number | null
  seasons: { season_id: number; season_label: string; year: number; competition_name: string; final_position: number | null; matches_played: number }[]
  matches: MatchSummary[]
}

export interface Player {
  id: number
  name: string
  position: string | null
  nationality: string | null
  birth_date: string | null
  height_cm: number | null
  weight_kg: number | null
  photo_url: string | null
  bio: string | null
  total_goals: number
  total_appearances: number
  goals: Goal[]
  appearances: {
    position_code: string | null
    is_starter: number
    team_id: number
    team_name: string
    match_id: number
    match_date: string
    home_team: string
    away_team: string
    home_score: number | null
    away_score: number | null
    season_label: string
    year: number
  }[]
}

export const api = {
  competitions: () => get<Competition[]>('/api/competitions'),
  seasons: () => get<Season[]>('/api/seasons'),
  season: (id: number) => get<SeasonDetail>(`/api/seasons/${id}`),
  match: (id: number) => get<Match>(`/api/matches/${id}`),
  teams: () => get<Team[]>('/api/teams'),
  team: (id: number, seasonId?: number) =>
    get<TeamDetail>(`/api/teams/${id}${seasonId ? `?season_id=${seasonId}` : ''}`),
  player: (id: number) => get<Player>(`/api/players/${id}`),
  searchPlayers: (q: string) => get<{ id: number; name: string; position: string | null; nationality: string | null; birth_date: string | null }[]>(`/api/players/search?q=${encodeURIComponent(q)}`),
  topScorers: (params?: { season_id?: number; competition?: string; limit?: number }) => {
    const qs = new URLSearchParams()
    if (params?.season_id) qs.set('season_id', String(params.season_id))
    if (params?.competition) qs.set('competition', params.competition)
    if (params?.limit) qs.set('limit', String(params.limit))
    return get<TopScorer[]>(`/api/top-scorers${qs.size ? `?${qs}` : ''}`)
  },
}
