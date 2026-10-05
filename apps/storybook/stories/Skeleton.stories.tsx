import type { Meta, StoryObj } from '@storybook/react'
import { Skeleton } from '@workspace/ui/components/skeleton'

const meta: Meta<typeof Skeleton> = {
  title: 'UI/Skeleton',
  component: Skeleton,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Skeleton>

export const Default: Story = {
  render: () => <Skeleton className="h-4 w-48" />,
}

export const SeasonCard: Story = {
  render: () => (
    <div className="w-64 space-y-3 rounded-lg border p-4">
      <Skeleton className="h-4 w-36" />
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-3 w-20" />
    </div>
  ),
}

export const StandingsTable: Story = {
  render: () => (
    <div className="w-full space-y-2">
      <Skeleton className="h-8 w-full" />
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-6 w-full" />
      ))}
    </div>
  ),
}

export const MatchRow: Story = {
  render: () => (
    <div className="flex items-center gap-3 w-80">
      <Skeleton className="h-3 w-20" />
      <Skeleton className="h-5 w-6 rounded-full" />
      <Skeleton className="h-3 flex-1" />
      <Skeleton className="h-4 w-10" />
    </div>
  ),
}
