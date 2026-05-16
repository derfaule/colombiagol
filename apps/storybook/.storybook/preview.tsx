import type { Preview } from '@storybook/react'
import '@workspace/ui/globals.css'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: 'oklch(1 0 0)' },
        { name: 'dark',  value: 'oklch(0.147 0.004 49.25)' },
      ],
    },
  },
  decorators: [
    (Story, context) => {
      const isDark = context.globals.backgrounds?.value === 'oklch(0.147 0.004 49.25)'
      return (
        <div className={isDark ? 'dark' : ''} style={{ padding: '2rem' }}>
          <Story />
        </div>
      )
    },
  ],
}

export default preview
