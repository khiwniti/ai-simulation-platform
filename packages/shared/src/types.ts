export interface Notebook {
  id: string;
  title: string;
  description: string;
  workbookId: string;
  cells: Cell[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export interface Cell {
  id: string;
  notebookId: string;
  cellType: CellType;
  content: string;
  outputs: CellOutput[];
  executionCount: number;
  metadata: Record<string, any>;
  position: number;
}

export enum CellType {
  CODE = 'code',
  MARKDOWN = 'markdown',
  PHYSICS = 'physics',
  VISUALIZATION = 'visualization',
}

export interface CellOutput {
  outputType: 'text' | 'html' | 'image' | 'visualization';
  data: any;
  metadata?: Record<string, any>;
}

export interface Workbook {
  id: string;
  name: string;
  description: string;
  notebooks: Notebook[];
  createdAt: Date;
  updatedAt: Date;
}

// Re-export chat types
export * from './chat-types';