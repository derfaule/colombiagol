import Link from 'next/link'
import { notFound } from 'next/navigation'
import { api, MatchSummary } from '@/lib/api'
import { Badge } from '@workspace/ui/components/badge'
import { Card, CardContent } from '@workspace/ui/components/card'
import { Separator } from '@workspace/ui/components/separator'

export default async function TeamPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const team = await api.team(Number(id)).catch(() => null)
  if (!team) notFound()

  // Group matches by season
  const bySeason = team.matches.reduce<Record<string, MatchSummary[]>>(
    (acc, m) => {
      const key = (m as any).season_label ?? 'Unknown'
      acc[key] = acc[key] ?? []
      acc[key].push(m)
      return acc
    },
    {},
  )

  const teamId = Number(id)

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <div className="mb-4">
        <Link href="/" className="text-muted-foreground hover:text-foreground text-sm transition-colors">
          ← Home
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="font-heading text-3xl font-bold">{team.name}</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          {team.seasons_active} season{team.seasons_active !== 1 ? 's' : ''} in database
        </p>
      </div>

      {/* Season summary cards */}
      {team.seasons.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-4 text-lg font-semibold">Seasons</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {team.seasons.map((s) => (
              <Link key={s.season_id} href={`/seasons/${s.season_id}`}>
                <Card className="hover:bg-accent/50 cursor-pointer transition-colors">
                  <CardContent className="flex items-center justify-between py-4">
                    <div>
                      <p className="font-medium">{s.season_label}</p>
                      <p className="text-muted-foreground text-sm">{s.competition_name}</p>
                    </div>
                    <div className="text-right text-sm">
                      {s.final_position && (
                        <p className="font-bold">#{s.final_position}</p>
                      )}
                      <p className="text-muted-foreground">{s.matches_played} matches</p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Matches */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">All Matches ({team.matches.length})</h2>
        <div className="space-y-8">
          {Object.entries(bySeason).map(([seasonLabel, matches]) => (
            <div key={seasonLabel}>
              <p className="text-muted-foreground mb-2 text-xs font-medium uppercase tracking-wider">
                {seasonLabel}
              </p>
              <div className="space-y-1.5">
                {matches.map((m) => {
                  const mAny = m as any
                  const isHome = m.home_team_id === teamId
                  const opponent = isHome ? m.away_team : m.home_team
                  const opponentId = isHome ? m.away_team_id : m.home_team_id
                  const hasResult = m.home_score !== null && m.away_score !== null

                  let result = '—'
                  let resultClass = 'text-muted-foreground'
                  if (hasResult) {
                    const scored = isHome ? m.home_score! : m.away_score!
                    const conceded = isHome ? m.away_score! : m.home_score!
                    if (scored > conceded) { result = 'W'; resultClass = 'text-green-600 dark:text-green-400' }
                    else if (scored < conceded) { result = 'L'; resultClass = 'text-red-600 dark:text-red-400' }
                    else { result = 'D'; resultClass = 'text-yellow-600 dark:text-yellow-400' }
                  }

                  const card = (
                    <Card className={m.goal_count > 0 || m.lineup_count > 0 ? 'hover:bg-accent/50 cursor-pointer transition-colors' : ''}>
                      <CardContent className="flex items-center gap-3 py-3 text-sm">
                        <span className="text-muted-foreground w-24 shrink-0 font-mono text-xs">
                          {m.match_date ?? '—'}
                        </span>
                        <Badge variant="outline" className={`w-6 shrink-0 justify-center font-bold ${resultClass}`}>
                          {result}
                        </Badge>
                        <span className="text-muted-foreground w-10 shrink-0 text-xs">
                          {isHome ? 'vs' : '@'}
                        </span>
                        <Link
                          href={`/teams/${opponentId}`}
                          className="min-w-0 flex-1 truncate font-medium hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {opponent}
                        </Link>
                        {hasResult && (
                          <span className="font-mono font-bold">
                            {isHome ? `${m.home_score}–${m.away_score}` : `${m.away_score}–${m.home_score}`}
                          </span>
                        )}
                      </CardContent>
                    </Card>
                  )

                  return m.goal_count > 0 || m.lineup_count > 0
                    ? <Link key={m.id} href={`/matches/${m.id}`}>{card}</Link>
                    : <div key={m.id}>{card}</div>
                })}
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
