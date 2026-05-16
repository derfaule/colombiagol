export const dynamic = 'force-dynamic'

import Link from 'next/link'
import { notFound } from 'next/navigation'
import { api, MatchSummary } from '@/lib/api'
import { Badge } from '@workspace/ui/components/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@workspace/ui/components/tabs'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@workspace/ui/components/table'

export default async function SeasonPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const season = await api.season(Number(id)).catch(() => null)
  if (!season) notFound()

  // Group matches by stage
  const byStage = season.matches.reduce<Record<string, MatchSummary[]>>((acc, m) => {
    const stage = m.stage ?? 'Sin fecha'
    acc[stage] = acc[stage] ?? []
    acc[stage].push(m)
    return acc
  }, {})

  // Latest standings snapshot
  const latestDate = season.standings.reduce<string>(
    (max, s) => (s.snapshot_date > max ? s.snapshot_date : max),
    '',
  )
  const standings = season.standings.filter((s) => s.snapshot_date === latestDate)

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <div className="mb-2">
        <Link href="/" className="text-muted-foreground hover:text-foreground text-sm transition-colors">
          ← All seasons
        </Link>
      </div>
      <div className="mb-8 flex items-center gap-3">
        <h1 className="font-heading text-3xl font-bold">{season.label}</h1>
        <Badge variant="secondary">{season.kind}</Badge>
      </div>

      <Tabs defaultValue="matches">
        <TabsList className="mb-6">
          <TabsTrigger value="matches">Matches ({season.matches.length})</TabsTrigger>
          {standings.length > 0 && (
            <TabsTrigger value="standings">Standings</TabsTrigger>
          )}
          {season.top_scorers.length > 0 && (
            <TabsTrigger value="scorers">Top Scorers</TabsTrigger>
          )}
        </TabsList>

        {/* Matches tab */}
        <TabsContent value="matches">
          <div className="space-y-8">
            {Object.entries(byStage).map(([stage, matches]) => (
              <section key={stage}>
                <h3 className="text-muted-foreground mb-3 text-sm font-medium uppercase tracking-wider">
                  {stage}
                </h3>
                <div className="grid gap-2">
                  {matches.map((m) => (
                    <MatchCard key={m.id} match={m} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </TabsContent>

        {/* Standings tab */}
        {standings.length > 0 && (
          <TabsContent value="standings">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10">#</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead className="text-center">P</TableHead>
                    <TableHead className="text-center">W</TableHead>
                    <TableHead className="text-center">D</TableHead>
                    <TableHead className="text-center">L</TableHead>
                    <TableHead className="text-center">GF</TableHead>
                    <TableHead className="text-center">GA</TableHead>
                    <TableHead className="text-center">GD</TableHead>
                    <TableHead className="text-center font-bold">Pts</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {standings.map((s) => (
                    <TableRow key={s.team_id}>
                      <TableCell className="text-muted-foreground font-mono text-xs">{s.position}</TableCell>
                      <TableCell>
                        <Link href={`/teams/${s.team_id}`} className="hover:underline">
                          {s.team_name}
                        </Link>
                      </TableCell>
                      <TableCell className="text-center text-sm">{s.played}</TableCell>
                      <TableCell className="text-center text-sm">{s.won}</TableCell>
                      <TableCell className="text-center text-sm">{s.drawn}</TableCell>
                      <TableCell className="text-center text-sm">{s.lost}</TableCell>
                      <TableCell className="text-center text-sm">{s.goals_for}</TableCell>
                      <TableCell className="text-center text-sm">{s.goals_against}</TableCell>
                      <TableCell className="text-center text-sm">{s.goal_diff > 0 ? `+${s.goal_diff}` : s.goal_diff}</TableCell>
                      <TableCell className="text-center font-bold">{s.points}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
        )}

        {/* Top scorers tab */}
        {season.top_scorers.length > 0 && (
          <TabsContent value="scorers">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10">#</TableHead>
                    <TableHead>Player</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead className="text-center">Goals</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {season.top_scorers.map((s, i) => (
                    <TableRow key={`${s.player_id}-${s.team_id}`}>
                      <TableCell className="text-muted-foreground font-mono text-xs">{i + 1}</TableCell>
                      <TableCell>
                        <Link href={`/players/${s.player_id}`} className="hover:underline">
                          {s.player_name}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/teams/${s.team_id}`} className="text-muted-foreground hover:underline text-sm">
                          {s.team_name}
                        </Link>
                      </TableCell>
                      <TableCell className="text-center font-bold">{s.goals}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
        )}
      </Tabs>
    </main>
  )
}

function MatchCard({ match }: { match: MatchSummary }) {
  const hasResult = match.home_score !== null && match.away_score !== null
  const hasDetail = match.goal_count > 0 || match.lineup_count > 0

  const card = (
    <Card className={hasDetail ? 'hover:bg-accent/50 cursor-pointer transition-colors' : ''}>
      <CardContent className="flex items-center gap-4 py-3">
        <span className="text-muted-foreground w-28 shrink-0 text-xs">
          {match.match_date ?? '—'}
        </span>
        <span className="min-w-0 flex-1 truncate text-right text-sm font-medium">
          {match.home_team}
        </span>
        <div className="flex shrink-0 items-center gap-1.5">
          {hasResult ? (
            <>
              <span className="bg-muted w-6 rounded text-center font-mono text-sm font-bold">
                {match.home_score}
              </span>
              <span className="text-muted-foreground text-xs">–</span>
              <span className="bg-muted w-6 rounded text-center font-mono text-sm font-bold">
                {match.away_score}
              </span>
            </>
          ) : (
            <span className="text-muted-foreground text-xs">vs</span>
          )}
        </div>
        <span className="min-w-0 flex-1 truncate text-sm font-medium">{match.away_team}</span>
      </CardContent>
    </Card>
  )

  return hasDetail ? <Link href={`/matches/${match.id}`}>{card}</Link> : card
}
