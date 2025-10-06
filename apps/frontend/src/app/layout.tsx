import './globals.css';
import type { Metadata } from 'next'
import { AuthProvider } from '../contexts/AuthContext';

export const metadata: Metadata = {
  title: 'EnsimuSpace - Your Engineering Universe',
  description: 'Transform your engineering workflow with GPU-accelerated physics, AI-assisted modeling, and real-time collaboration in EnsimuSpace.',
  keywords: 'simulation, engineering, AI, physics, GPU, collaboration, modeling, EnsimuSpace, EnsimuLab, EnsimuNotebook',
  authors: [{ name: 'EnsimuSpace Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="antialiased bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 min-h-screen">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}