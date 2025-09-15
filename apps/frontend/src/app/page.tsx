'use client';

import { Layout } from '@/components/layout/Layout';
import { WorkbookManager } from '@/components/workbook/WorkbookManager';
import { NotebookManager } from '@/components/notebook/NotebookManager';

export default function Home() {
  return (
    <main>
      <WorkbookManager />
      <NotebookManager />
      <Layout />
    </main>
  );
}