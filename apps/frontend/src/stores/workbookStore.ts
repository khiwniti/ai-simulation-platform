'use client';

import { create } from 'zustand';

interface WorkbookState {
  workbooks: any[];
  currentWorkbook: any | null;
  isLoading: boolean;
}

interface WorkbookActions {
  setWorkbooks: (workbooks: any[]) => void;
  setCurrentWorkbook: (workbook: any | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useWorkbookStore = create<WorkbookState & WorkbookActions>((set) => ({
  workbooks: [],
  currentWorkbook: null,
  isLoading: false,
  setWorkbooks: (workbooks) => set({ workbooks }),
  setCurrentWorkbook: (workbook) => set({ currentWorkbook: workbook }),
  setLoading: (loading) => set({ isLoading: loading }),
}));