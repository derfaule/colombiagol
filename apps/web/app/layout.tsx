import { Geist_Mono, Figtree, Raleway } from "next/font/google"
import Link from "next/link"

import "@workspace/ui/globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@workspace/ui/lib/utils"

const ralewayHeading = Raleway({ subsets: ['latin'], variable: '--font-heading' })
const figtree = Figtree({ subsets: ['latin'], variable: '--font-sans' })
const fontMono = Geist_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata = { title: 'Colombia Liga', description: 'Historical Colombian football data' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn('antialiased', fontMono.variable, 'font-sans', figtree.variable, ralewayHeading.variable)}
    >
      <body>
        <ThemeProvider>
          <header className="border-b">
            <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
              <Link href="/" className="font-heading text-lg font-bold tracking-tight">
                Colombia Liga
              </Link>
              <nav className="flex items-center gap-4 text-sm">
                <Link href="/" className="text-muted-foreground hover:text-foreground transition-colors">
                  Seasons
                </Link>
                <Link href="/teams" className="text-muted-foreground hover:text-foreground transition-colors">
                  Teams
                </Link>
              </nav>
            </div>
          </header>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
