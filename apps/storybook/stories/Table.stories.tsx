import type { Meta, StoryObj } from '@storybook/react'
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
} from '@workspace/ui/components/table'
import { Badge } from '@workspace/ui/components/badge'

const meta: Meta<typeof Table> = {
  title: 'UI/Table',
  component: Table,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Table>

const standings = [
  { pos: 1,  team: 'Atlético Nacional',     p: 38, w: 24, d: 8,  l: 6,  gf: 72, ga: 32, pts: 80 },
  { pos: 2,  team: 'Millonarios FC',        p: 38, w: 21, d: 9,  l: 8,  gf: 61, ga: 38, pts: 72 },
  { pos: 3,  team: 'Deportivo Cali',        p: 38, w: 19, d: 11, l: 8,  gf: 58, ga: 41, pts: 68 },
  { pos: 4,  team: 'Independiente Medellín',p: 38, w: 18, d: 10, l: 10, gf: 54, ga: 44, pts: 64 },
  { pos: 5,  team: 'Atlético Junior',       p: 38, w: 17, d: 12, l: 9,  gf: 52, ga: 42, pts: 63 },
]

export const Standings: Story = {
  render: () => (
    <Table>
      <TableCaption>Liga BetPlay 2023 Apertura — Final Standings</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-8">#</TableHead>
          <TableHead>Team</TableHead>
          <TableHead className="text-right">P</TableHead>
          <TableHead className="text-right">W</TableHead>
          <TableHead className="text-right">D</TableHead>
          <TableHead className="text-right">L</TableHead>
          <TableHead className="text-right">GF</TableHead>
          <TableHead className="text-right">GA</TableHead>
          <TableHead className="text-right">Pts</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {standings.map(row => (
          <TableRow key={row.pos}>
            <TableCell className="font-mono text-muted-foreground">{row.pos}</TableCell>
            <TableCell className="font-medium">{row.team}</TableCell>
            <TableCell className="text-right">{row.p}</TableCell>
            <TableCell className="text-right">{row.w}</TableCell>
            <TableCell className="text-right">{row.d}</TableCell>
            <TableCell className="text-right">{row.l}</TableCell>
            <TableCell className="text-right">{row.gf}</TableCell>
            <TableCell className="text-right">{row.ga}</TableCell>
            <TableCell className="text-right font-bold">{row.pts}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
}

export const TopScorers: Story = {
  render: () => (
    <Table>
      <TableCaption>Top Scorers — 2023 Apertura</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>#</TableHead>
          <TableHead>Player</TableHead>
          <TableHead>Team</TableHead>
          <TableHead className="text-right">Goals</TableHead>
          <TableHead className="text-right">Pens</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[
          { rank: 1, player: 'Jefferson Duque', team: 'Nacional', goals: 18, pens: 3 },
          { rank: 2, player: 'Dayro Moreno',    team: 'Once Caldas', goals: 15, pens: 2 },
          { rank: 3, player: 'Leonardo Castro', team: 'Millonarios', goals: 13, pens: 1 },
        ].map(row => (
          <TableRow key={row.rank}>
            <TableCell className="text-muted-foreground">{row.rank}</TableCell>
            <TableCell className="font-medium">{row.player}</TableCell>
            <TableCell>
              <Badge variant="outline">{row.team}</Badge>
            </TableCell>
            <TableCell className="text-right font-bold">{row.goals}</TableCell>
            <TableCell className="text-right text-muted-foreground">{row.pens}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
}
