import { z } from 'zod';

export const CellTypeSchema = z.enum(['code', 'markdown', 'physics', 'visualization']);

export const CellOutputSchema = z.object({
  outputType: z.enum(['text', 'html', 'image', 'visualization']),
  data: z.any(),
  metadata: z.record(z.any()).optional(),
});

export const CellSchema = z.object({
  id: z.string(),
  notebookId: z.string(),
  cellType: CellTypeSchema,
  content: z.string(),
  outputs: z.array(CellOutputSchema),
  executionCount: z.number(),
  metadata: z.record(z.any()),
  position: z.number(),
});

export const NotebookSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  workbookId: z.string(),
  cells: z.array(CellSchema),
  metadata: z.record(z.any()),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number(),
});

export const WorkbookSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  notebooks: z.array(NotebookSchema),
  createdAt: z.date(),
  updatedAt: z.date(),
});