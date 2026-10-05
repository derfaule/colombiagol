import type { Meta, StoryObj } from '@storybook/react'
import { Separator } from '@workspace/ui/components/separator'

const meta: Meta<typeof Separator> = {
  title: 'UI/Separator',
  component: Separator,
  tags: ['autodocs'],
  argTypes: {
    orientation: { control: 'select', options: ['horizontal', 'vertical'] },
  },
}

export default meta
type Story = StoryObj<typeof Separator>

export const Horizontal: Story = {
  render: () => (
    <div className="w-64">
      <p className="text-sm">Atlético Nacional</p>
      <Separator className="my-3" />
      <p className="text-sm text-muted-foreground">18 titles</p>
    </div>
  ),
}

export const Vertical: Story = {
  render: () => (
    <div className="flex h-8 items-center gap-3">
      <span className="text-sm">Apertura</span>
      <Separator orientation="vertical" />
      <span className="text-sm">Clausura</span>
      <Separator orientation="vertical" />
      <span className="text-sm">Finals</span>
    </div>
  ),
}
