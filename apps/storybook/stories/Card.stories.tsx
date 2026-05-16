import type { Meta, StoryObj } from '@storybook/react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardAction,
} from '@workspace/ui/components/card'
import { Badge } from '@workspace/ui/components/badge'
import { Button } from '@workspace/ui/components/button'

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['default', 'sm'] },
  },
}

export default meta
type Story = StoryObj<typeof Card>

export const Default: Story = {
  render: () => (
    <Card className="w-72">
      <CardHeader>
        <CardTitle>Liga BetPlay 2023</CardTitle>
        <CardDescription>Clausura · 20 teams</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">380 matches played</p>
      </CardContent>
    </Card>
  ),
}

export const WithAction: Story = {
  render: () => (
    <Card className="w-72">
      <CardHeader>
        <CardTitle>Atlético Nacional</CardTitle>
        <CardAction>
          <Badge variant="secondary">1st</Badge>
        </CardAction>
        <CardDescription>Liga BetPlay 2023 Apertura</CardDescription>
      </CardHeader>
      <CardContent>
        <p>38 played · 24W 8D 6L</p>
      </CardContent>
      <CardFooter>
        <Button size="sm" variant="outline">View squad</Button>
      </CardFooter>
    </Card>
  ),
}

export const Small: Story = {
  render: () => (
    <Card size="sm" className="w-64">
      <CardHeader>
        <CardTitle>Millonarios FC</CardTitle>
        <CardDescription>2022 Clausura</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Champion</p>
      </CardContent>
    </Card>
  ),
}

export const MatchCard: Story = {
  render: () => (
    <Card className="w-80">
      <CardContent className="flex items-center justify-between py-4">
        <span className="font-medium">Millonarios</span>
        <span className="font-mono font-bold text-sm">2 – 1</span>
        <span className="font-medium">América</span>
      </CardContent>
    </Card>
  ),
}

export const SeasonGrid: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-3 w-[500px]">
      {['2023 Apertura', '2023 Clausura', '2022 Apertura', '2022 Clausura'].map(label => (
        <Card key={label} size="sm">
          <CardHeader>
            <CardTitle>{label}</CardTitle>
            <CardDescription>Liga BetPlay</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">180 matches</p>
          </CardContent>
        </Card>
      ))}
    </div>
  ),
}
