import type { Meta, StoryObj } from '@storybook/react'
import { Badge } from '@workspace/ui/components/badge'

const meta: Meta<typeof Badge> = {
  title: 'UI/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'outline', 'ghost', 'link'],
    },
  },
}

export default meta
type Story = StoryObj<typeof Badge>

export const Default: Story = {
  args: { children: 'Liga BetPlay', variant: 'default' },
}

export const Secondary: Story = {
  args: { children: 'Apertura', variant: 'secondary' },
}

export const Destructive: Story = {
  args: { children: 'Suspended', variant: 'destructive' },
}

export const Outline: Story = {
  args: { children: 'Clausura', variant: 'outline' },
}

export const Ghost: Story = {
  args: { children: 'Cup', variant: 'ghost' },
}

export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default">Default</Badge>
      <Badge variant="secondary">Secondary</Badge>
      <Badge variant="destructive">Destructive</Badge>
      <Badge variant="outline">Outline</Badge>
      <Badge variant="ghost">Ghost</Badge>
      <Badge variant="link">Link</Badge>
    </div>
  ),
}

export const FootballContext: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default">Liga BetPlay</Badge>
      <Badge variant="secondary">Apertura</Badge>
      <Badge variant="outline">Clausura</Badge>
      <Badge variant="destructive">Relegation</Badge>
      <Badge variant="ghost">Friendly</Badge>
    </div>
  ),
}
