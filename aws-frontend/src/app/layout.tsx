import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AWS AI Agent Engineering Platform',
  description: 'Autonomous AI engineering team powered by AWS Bedrock AgentCore and Amazon Nova',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-aws-light via-white to-blue-50">
          {children}
        </div>
      </body>
    </html>
  )
}