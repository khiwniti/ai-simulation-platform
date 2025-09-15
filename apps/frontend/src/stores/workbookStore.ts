import { create } from 'zustand';
import { Workbook, Notebook } from '@ai-jupyter/shared';

interface WorkbookState {
  workbooks: Workbook[];
  selectedWorkbook: Workbook | null;
  selectedNotebook: Notebook | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  setWorkbooks: (workbooks: Workbook[]) => void;
  addWorkbook: (workbook: Workbook) => void;
  updateWorkbook: (id: string, updates: Partial<Workbook>) => void;
  deleteWorkbook: (id: string) => void;
  selectWorkbook: (workbook: Workbook | null) => void;
  selectNotebook: (notebook: Notebook | null) => void;
  addNotebook: (workbookId: string, notebook: Notebook) => void;
  updateNotebook: (id: string, updates: Partial<Notebook>) => void;
  deleteNotebook: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useWorkbookStore = create<WorkbookState>((set, get) => ({
  workbooks: [],
  selectedWorkbook: null,
  selectedNotebook: null,
  loading: false,
  error: null,

  setWorkbooks: (workbooks) => set({ workbooks }),
  
  addWorkbook: (workbook) => set((state) => ({
    workbooks: [...state.workbooks, workbook]
  })),
  
  updateWorkbook: (id, updates) => set((state) => ({
    workbooks: state.workbooks.map(wb => 
      wb.id === id ? { ...wb, ...updates } : wb
    ),
    selectedWorkbook: state.selectedWorkbook?.id === id 
      ? { ...state.selectedWorkbook, ...updates }
      : state.selectedWorkbook
  })),
  
  deleteWorkbook: (id) => set((state) => ({
    workbooks: state.workbooks.filter(wb => wb.id !== id),
    selectedWorkbook: state.selectedWorkbook?.id === id ? null : state.selectedWorkbook,
    selectedNotebook: state.selectedNotebook?.workbookId === id ? null : state.selectedNotebook
  })),
  
  selectWorkbook: (workbook) => set({ 
    selectedWorkbook: workbook,
    selectedNotebook: null // Clear notebook selection when changing workbook
  }),
  
  selectNotebook: (notebook) => set({ selectedNotebook: notebook }),
  
  addNotebook: (workbookId, notebook) => set((state) => ({
    workbooks: state.workbooks.map(wb =>
      wb.id === workbookId
        ? { ...wb, notebooks: [...wb.notebooks, notebook] }
        : wb
    )
  })),
  
  updateNotebook: (id, updates) => set((state) => ({
    workbooks: state.workbooks.map(wb => ({
      ...wb,
      notebooks: wb.notebooks.map(nb =>
        nb.id === id ? { ...nb, ...updates } : nb
      )
    })),
    selectedNotebook: state.selectedNotebook?.id === id
      ? { ...state.selectedNotebook, ...updates }
      : state.selectedNotebook
  })),
  
  deleteNotebook: (id) => set((state) => ({
    workbooks: state.workbooks.map(wb => ({
      ...wb,
      notebooks: wb.notebooks.filter(nb => nb.id !== id)
    })),
    selectedNotebook: state.selectedNotebook?.id === id ? null : state.selectedNotebook
  })),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error })
}));