export const dynamic = 'force-dynamic'

import Link from 'next/link'
import { notFound } from 'next/navigation'
import { api } from '@/lib/api'
import { Badge } from '@workspace/ui/components/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@workspace/ui/components/table'

export default async function PlayerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const player = await api.player(Number(id)).catch(() => null)
  if (!player) notFound()

  // Group goals by season
  const goalsBySeason = player.goals.reduce<Record<string, typeof player.goals>>(
    (acc, g) => {
      const key = (g as any).season_label ?? 'Unknown'
      acc[key] = acc[key] ?? []
      acc[key].push(g)
      return acc
    },
    {},
  )

  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-4">
        <Link href="/" className="text-muted-foreground hover:text-foreground text-sm transition-colors">
          ← Home
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="font-heading text-3xl font-bold">{player.name}</h1>
        <div className="mt-2 flex flex-wrap gap-2">
          {player.position && <Badge variant="secondary">{player.position}</Badge>}
          {player.nationality && <Badge variant="outline">{player.nationality}</Badge>}
          {player.birth_date && (
            <span className="text-muted-foreground text-sm">{player.birth_date}</span>
          )}
        </div>
      </div>

      {/* Stats summary */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Appearances', value: player.total_appearances },
          { label: 'Goals', value: player.total_goals },
          ...(player.height_cm ? [{ label: 'Height', value: `${player.height_cm} cm` }] : []),
          ...(player.weight_kg ? [{ label: 'Weight', value: `${player.weight_kg} kg` }] : []),
        ].map(({ label, value }) => (
          <Card key={label}>
            <CardHeader className="pb-1 pt-4">
              <CardTitle className="text-muted-foreground text-xs font-medium uppercase tracking-wider">
                {label}
              </CardTitle>
            </CardHeader>
            <CardContent className="pb-4 pt-0">
              <p className="font-heading text-2xl font-bold">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Goals */}
      {player.total_goals > 0 && (
        <section className="mb-8">
          <h2 className="mb-4 text-lg font-semibold">Goals ({player.total_goals})</h2>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Match</TableHead>
                  <TableHead>Season</TableHead>
                  <TableHead className="text-center">Min</TableHead>
                  <TableHead className="text-center">Type</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {player.goals.map((g, i) => {
                  const gAny = g as any
                  return (
                    <TableRow key={i}>
                      <TableCell className="text-sm">
                        <Link href={`/matches/${gAny.match_id}`} className="hover:underline">
                          {gAny.home_team} {gAny.home_score}–{gAny.away_score} {gAny.away_team}
                        </Link>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">{gAny.season_label}</TableCell>
                      <TableCell className="text-center font-mono text-sm">
                        {g.minute ?? '—'}
                      </TableCell>
                      <TableCell className="text-center">
                        {g.is_penalty ? (
                          <Badge variant="outline" className="text-xs">Penalty</Badge>
                        ) : g.is_own_goal ? (
                          <Badge variant="destructive" className="text-xs">OG</Badge>
                        ) : (
                          <span className="text-muted-foreground text-xs">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        </section>
      )}

      {/* Appearances */}
      {player.total_appearances > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold">Appearances ({player.total_appearances})</h2>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Match</TableHead>
                  <TableHead>Club</TableHead>
                  <TableHead>Season</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {player.appearances.map((a, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-muted-foreground font-mono text-xs">{a.match_date}</TableCell>
                    <TableCell className="text-sm">
                      <Link href={`/matches/${a.match_id}`} className="hover:underline">
                        {a.home_team} {a.home_score ?? '?'}–{a.away_score ?? '?'} {a.away_team}
                      </Link>
                    </TableCell>
                    <TableCell className="text-sm">{a.team_name}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">{a.season_label}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </section>
      )}
    </main>
  )
}
