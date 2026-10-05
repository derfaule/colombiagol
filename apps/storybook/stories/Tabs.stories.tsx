import type { Meta, StoryObj } from '@storybook/react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@workspace/ui/components/tabs'
import {
  Table, TableHeader, TableBody,
  TableHead, TableRow, TableCell,
} from '@workspace/ui/components/table'

const meta: Meta<typeof Tabs> = {
  title: 'UI/Tabs',
  component: Tabs,
  tags: ['autodocs'],
  argTypes: {
    orientation: { control: 'select', options: ['horizontal', 'vertical'] },
  },
}

export default meta
type Story = StoryObj<typeof Tabs>

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="standings">
      <TabsList>
        <TabsTrigger value="standings">Standings</TabsTrigger>
        <TabsTrigger value="matches">Matches</TabsTrigger>
        <TabsTrigger value="scorers">Top Scorers</TabsTrigger>
      </TabsList>
      <TabsContent value="standings">
        <p className="text-muted-foreground mt-2">Standings table goes here</p>
      </TabsContent>
      <TabsContent value="matches">
        <p className="text-muted-foreground mt-2">Match results go here</p>
      </TabsContent>
      <TabsContent value="scorers">
        <p className="text-muted-foreground mt-2">Top scorers go here</p>
      </TabsContent>
    </Tabs>
  ),
}

export const LineVariant: Story = {
  render: () => (
    <Tabs defaultValue="apertura">
      <TabsList variant="line">
        <TabsTrigger value="apertura">Apertura</TabsTrigger>
        <TabsTrigger value="clausura">Clausura</TabsTrigger>
      </TabsList>
      <TabsContent value="apertura">
        <p className="text-muted-foreground mt-4">Apertura standings</p>
      </TabsContent>
      <TabsContent value="clausura">
        <p className="text-muted-foreground mt-4">Clausura standings</p>
      </TabsContent>
    </Tabs>
  ),
}

export const SeasonDetail: Story = {
  render: () => (
    <div className="w-[600px]">
      <Tabs defaultValue="standings">
        <TabsList>
          <TabsTrigger value="standings">Standings</TabsTrigger>
          <TabsTrigger value="matches">Matches</TabsTrigger>
          <TabsTrigger value="scorers">Top Scorers</TabsTrigger>
        </TabsList>
        <TabsContent value="standings">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>Team</TableHead>
                <TableHead className="text-right">Pts</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {['Atlético Nacional', 'Millonarios FC', 'Deportivo Cali'].map((team, i) => (
                <TableRow key={team}>
                  <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                  <TableCell className="font-medium">{team}</TableCell>
                  <TableCell className="text-right font-bold">{80 - i * 8}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TabsContent>
        <TabsContent value="matches">
          <p className="text-muted-foreground p-4">Match results</p>
        </TabsContent>
        <TabsContent value="scorers">
          <p className="text-muted-foreground p-4">Top scorers</p>
        </TabsContent>
      </Tabs>
    </div>
  ),
}

export const Vertical: Story = {
  render: () => (
    <Tabs defaultValue="league" orientation="vertical" className="w-[400px]">
      <TabsList>
        <TabsTrigger value="league">League</TabsTrigger>
        <TabsTrigger value="cup">Cup</TabsTrigger>
        <TabsTrigger value="friendly">Friendly</TabsTrigger>
      </TabsList>
      <TabsContent value="league">League matches</TabsContent>
      <TabsContent value="cup">Cup matches</TabsContent>
      <TabsContent value="friendly">Friendly matches</TabsContent>
    </Tabs>
  ),
}
