export const dynamic = 'force-dynamic'

import Link from 'next/link'
import { api } from '@/lib/api'
import { Badge } from '@workspace/ui/components/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card'

export default async function HomePage() {
  const [seasons, competitions] = await Promise.all([api.seasons(), api.competitions()])

  const grouped = seasons.reduce<Record<string, typeof seasons>>(
    (acc, s) => {
      const key = s.canonical_name
      acc[key] = acc[key] ?? []
      acc[key].push(s)
      return acc
    },
    {},
  )

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <div className="mb-10">
        <h1 className="font-heading text-4xl font-bold tracking-tight">Colombia Liga</h1>
        <p className="text-muted-foreground mt-2 text-sm">
          Historical data from the Colombian football leagues · {competitions.reduce((n, c) => n + c.total_matches, 0).toLocaleString()} matches
        </p>
      </div>

      <div className="space-y-10">
        {Object.entries(grouped).map(([competition, compSeasons]) => (
          <section key={competition}>
            <div className="mb-4 flex items-center gap-3">
              <h2 className="font-heading text-xl font-semibold">{competition}</h2>
              <Badge variant="secondary">{compSeasons[0]?.kind}</Badge>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {compSeasons.map((s) => (
                <Link key={s.id} href={`/seasons/${s.id}`}>
                  <Card className="hover:bg-accent/50 cursor-pointer transition-colors">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">{s.label}</CardTitle>
                    </CardHeader>
                    <CardContent className="text-muted-foreground flex gap-4 text-xs">
                      <span>{s.match_count} matches</span>
                      {s.standing_count > 0 && <span>{s.standing_count} standings</span>}
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  )
}
