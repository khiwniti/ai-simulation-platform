import { renderHook, act } from '@testing-library/react';
import { useWorkbookStore } from '@/stores/workbookStore';
import { Workbook, Notebook } from '@ai-jupyter/shared';

// Mock workbook data
const mockWorkbook: Workbook = {
  id: 'wb_1',
  name: 'Test Workbook',
  description: 'Test description',
  notebooks: [],
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01')
};

const mockNotebook: Notebook = {
  id: 'nb_1',
  title: 'Test Notebook',
  description: 'Test notebook description',
  workbookId: 'wb_1',
  cells: [],
  metadata: {},
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01'),
  version: 1
};

describe('workbookStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useWorkbookStore.setState({
      workbooks: [],
      selectedWorkbook: null,
      selectedNotebook: null,
      loading: false,
      error: null
    });
  });

  describe('workbook management', () => {
    it('should add a workbook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addWorkbook(mockWorkbook);
      });

      expect(result.current.workbooks).toHaveLength(1);
      expect(result.current.workbooks[0]).toEqual(mockWorkbook);
    });

    it('should update a workbook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addWorkbook(mockWorkbook);
        result.current.updateWorkbook('wb_1', { name: 'Updated Name' });
      });

      expect(result.current.workbooks[0].name).toBe('Updated Name');
    });

    it('should delete a workbook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addWorkbook(mockWorkbook);
        result.current.deleteWorkbook('wb_1');
      });

      expect(result.current.workbooks).toHaveLength(0);
    });

    it('should select a workbook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.selectWorkbook(mockWorkbook);
      });

      expect(result.current.selectedWorkbook).toEqual(mockWorkbook);
    });

    it('should clear notebook selection when selecting a different workbook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.selectNotebook(mockNotebook);
        result.current.selectWorkbook(mockWorkbook);
      });

      expect(result.current.selectedWorkbook).toEqual(mockWorkbook);
      expect(result.current.selectedNotebook).toBeNull();
    });
  });

  describe('notebook management', () => {
    beforeEach(() => {
      const { result } = renderHook(() => useWorkbookStore());
      act(() => {
        result.current.addWorkbook(mockWorkbook);
      });
    });

    it('should add a notebook to a workbook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addNotebook('wb_1', mockNotebook);
      });

      expect(result.current.workbooks[0].notebooks).toHaveLength(1);
      expect(result.current.workbooks[0].notebooks[0]).toEqual(mockNotebook);
    });

    it('should update a notebook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addNotebook('wb_1', mockNotebook);
        result.current.updateNotebook('nb_1', { title: 'Updated Title' });
      });

      expect(result.current.workbooks[0].notebooks[0].title).toBe('Updated Title');
    });

    it('should delete a notebook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addNotebook('wb_1', mockNotebook);
        result.current.deleteNotebook('nb_1');
      });

      expect(result.current.workbooks[0].notebooks).toHaveLength(0);
    });

    it('should select a notebook', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.selectNotebook(mockNotebook);
      });

      expect(result.current.selectedNotebook).toEqual(mockNotebook);
    });

    it('should clear selected notebook when deleting it', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.addNotebook('wb_1', mockNotebook);
        result.current.selectNotebook(mockNotebook);
        result.current.deleteNotebook('nb_1');
      });

      expect(result.current.selectedNotebook).toBeNull();
    });
  });

  describe('loading and error states', () => {
    it('should set loading state', () => {
      const { result } = renderHook(() => useWorkbookStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.loading).toBe(true);
    });

    it('should set error state', () => {
      const { result } = renderHook(() => useWorkbookStore());
      const errorMessage = 'Test error';

      act(() => {
        result.current.setError(errorMessage);
      });

      expect(result.current.error).toBe(errorMessage);
    });
  });
});