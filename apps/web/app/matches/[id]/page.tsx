export const dynamic = 'force-dynamic'

import Link from 'next/link'
import { notFound } from 'next/navigation'
import { api, LineupEntry } from '@/lib/api'
import { Badge } from '@workspace/ui/components/badge'
import { Separator } from '@workspace/ui/components/separator'

const POSITION_LABEL: Record<string, string> = {
  A: 'GK', D: 'DEF', V: 'MID', M: 'MID', C: 'FWD', P: 'FWD',
}

export default async function MatchPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const match = await api.match(Number(id)).catch(() => null)
  if (!match) notFound()

  const homeGoals = match.goals.filter((g) => g.team_id === match.home_team_id)
  const awayGoals = match.goals.filter((g) => g.team_id === match.away_team_id)

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <div className="mb-4">
        <Link
          href={`/seasons/${match.season_id}`}
          className="text-muted-foreground hover:text-foreground text-sm transition-colors"
        >
          ← {match.season_label}
        </Link>
      </div>

      {/* Score banner */}
      <div className="bg-card mb-8 rounded-xl border p-8">
        <div className="mb-4 flex items-center justify-center gap-2">
          <Badge variant="secondary">{match.competition_name}</Badge>
          {match.stage && <span className="text-muted-foreground text-sm">{match.stage}</span>}
        </div>

        <div className="grid grid-cols-3 items-center gap-4">
          <div className="text-right">
            <Link href={`/teams/${match.home_team_id}`} className="hover:underline">
              <h2 className="font-heading text-2xl font-bold">{match.home_team}</h2>
            </Link>
            <div className="text-muted-foreground mt-1 space-y-0.5 text-sm">
              {homeGoals.map((g, i) => (
                <p key={i}>
                  {g.player_name.split(' ').slice(-2).join(' ')}
                  {g.minute ? ` ${g.minute}'` : ''}
                  {g.is_penalty ? ' (P)' : ''}
                  {g.is_own_goal ? ' (OG)' : ''}
                </p>
              ))}
            </div>
          </div>

          <div className="text-center">
            {match.home_score !== null ? (
              <div className="font-mono text-5xl font-bold tracking-tight">
                {match.home_score} – {match.away_score}
              </div>
            ) : (
              <div className="text-muted-foreground text-2xl">vs</div>
            )}
            <p className="text-muted-foreground mt-2 text-xs">{match.match_date}</p>
          </div>

          <div className="text-left">
            <Link href={`/teams/${match.away_team_id}`} className="hover:underline">
              <h2 className="font-heading text-2xl font-bold">{match.away_team}</h2>
            </Link>
            <div className="text-muted-foreground mt-1 space-y-0.5 text-sm">
              {awayGoals.map((g, i) => (
                <p key={i}>
                  {g.player_name.split(' ').slice(-2).join(' ')}
                  {g.minute ? ` ${g.minute}'` : ''}
                  {g.is_penalty ? ' (P)' : ''}
                  {g.is_own_goal ? ' (OG)' : ''}
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Goal timeline */}
      {match.goals.length > 0 && (
        <section className="mb-8">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider">Goals</h3>
          <div className="space-y-1.5">
            {match.goals
              .slice()
              .sort((a, b) => (a.minute ?? 999) - (b.minute ?? 999))
              .map((g, i) => {
                const isHome = g.team_id === match.home_team_id
                return (
                  <div
                    key={i}
                    className={`flex items-center gap-3 text-sm ${isHome ? '' : 'flex-row-reverse'}`}
                  >
                    <span className="text-muted-foreground w-8 shrink-0 font-mono text-xs">
                      {g.minute ?? '?'}'
                    </span>
                    <span className="flex items-center gap-1.5">
                      ⚽
                      <Link href={`/players/${g.player_id}`} className="hover:underline">
                        {g.player_name}
                      </Link>
                      {g.is_penalty ? <Badge variant="outline" className="text-xs">P</Badge> : null}
                      {g.is_own_goal ? <Badge variant="destructive" className="text-xs">OG</Badge> : null}
                    </span>
                  </div>
                )
              })}
          </div>
        </section>
      )}

      {/* Lineups */}
      {(match.home_lineup.length > 0 || match.away_lineup.length > 0) && (
        <section>
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider">Lineups</h3>
          <div className="grid grid-cols-2 gap-8">
            <LineupColumn entries={match.home_lineup} teamName={match.home_team} />
            <LineupColumn entries={match.away_lineup} teamName={match.away_team} align="right" />
          </div>
        </section>
      )}
    </main>
  )
}

function LineupColumn({
  entries,
  teamName,
  align = 'left',
}: {
  entries: LineupEntry[]
  teamName: string
  align?: 'left' | 'right'
}) {
  const starters = entries.filter((e) => e.is_starter)
  const subs = entries.filter((e) => !e.is_starter)
  const textAlign = align === 'right' ? 'text-right' : 'text-left'

  return (
    <div className={textAlign}>
      <p className="mb-3 font-semibold">{teamName}</p>
      <div className="space-y-1">
        {starters.map((p) => (
          <div key={p.player_id} className={`flex items-center gap-2 text-sm ${align === 'right' ? 'flex-row-reverse' : ''}`}>
            <span className="text-muted-foreground w-8 font-mono text-xs">
              {p.position_code ? POSITION_LABEL[p.position_code] ?? p.position_code : '—'}
            </span>
            <Link href={`/players/${p.player_id}`} className="hover:underline">
              {p.player_name}
            </Link>
          </div>
        ))}
      </div>
      {subs.length > 0 && (
        <>
          <Separator className="my-3" />
          <p className="text-muted-foreground mb-2 text-xs uppercase tracking-wider">Substitutes</p>
          <div className="space-y-1">
            {subs.map((p) => (
              <div key={p.player_id} className={`flex items-center gap-2 text-sm ${align === 'right' ? 'flex-row-reverse' : ''}`}>
                <span className="text-muted-foreground w-8 font-mono text-xs">
                  {p.position_code ? POSITION_LABEL[p.position_code] ?? p.position_code : '—'}
                </span>
                <Link href={`/players/${p.player_id}`} className="text-muted-foreground hover:underline">
                  {p.player_name}
                </Link>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
