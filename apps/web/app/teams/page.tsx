import Link from 'next/link'
import { api } from '@/lib/api'
import { Card, CardContent } from '@workspace/ui/components/card'

export default async function TeamsPage() {
  const teams = await api.teams()
  const active = teams.filter((t) => t.seasons_active > 0)

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="font-heading mb-8 text-3xl font-bold">Teams</h1>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {active.map((t) => (
          <Link key={t.id} href={`/teams/${t.id}`}>
            <Card className="hover:bg-accent/50 cursor-pointer transition-colors">
              <CardContent className="flex items-center justify-between py-3">
                <span className="font-medium">{t.name}</span>
                <span className="text-muted-foreground text-xs">{t.seasons_active} season{t.seasons_active !== 1 ? 's' : ''}</span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  )
}
