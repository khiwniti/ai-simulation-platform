import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { WorkbookManager, useWorkbookManager } from '@/components/workbook/WorkbookManager';
import { useWorkbookStore } from '@/stores/workbookStore';

// Mock the store
jest.mock('@/stores/workbookStore');
const mockUseWorkbookStore = useWorkbookStore as jest.MockedFunction<typeof useWorkbookStore>;

const mockStoreState = {
  workbooks: [],
  selectedWorkbook: null,
  selectedNotebook: null,
  loading: false,
  error: null,
  setWorkbooks: jest.fn(),
  addWorkbook: jest.fn(),
  updateWorkbook: jest.fn(),
  deleteWorkbook: jest.fn(),
  selectWorkbook: jest.fn(),
  selectNotebook: jest.fn(),
  addNotebook: jest.fn(),
  updateNotebook: jest.fn(),
  deleteNotebook: jest.fn(),
  setLoading: jest.fn(),
  setError: jest.fn()
};

describe('WorkbookManager', () => {
  beforeEach(() => {
    mockUseWorkbookStore.mockReturnValue(mockStoreState);
    jest.clearAllMocks();
  });

  it('renders loading state when loading and no workbooks', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      loading: true
    });

    render(<WorkbookManager />);
    
    expect(screen.getByText('Loading workbooks...')).toBeInTheDocument();
  });

  it('renders error state when there is an error', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      error: 'Failed to load workbooks'
    });

    render(<WorkbookManager />);
    
    expect(screen.getByText('Error:')).toBeInTheDocument();
    expect(screen.getByText('Failed to load workbooks')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('renders nothing when not loading and no error', () => {
    const { container } = render(<WorkbookManager />);
    
    expect(container.firstChild).toBeNull();
  });

  it('loads mock workbooks on mount when workbooks array is empty', async () => {
    render(<WorkbookManager />);
    
    await waitFor(() => {
      expect(mockStoreState.setLoading).toHaveBeenCalledWith(true);
    });
  });

  it('does not load workbooks if workbooks already exist', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      workbooks: [{ id: 'wb_1', name: 'Existing Workbook' } as any]
    });

    render(<WorkbookManager />);
    
    // Should not call setLoading since workbooks already exist
    expect(mockStoreState.setLoading).not.toHaveBeenCalled();
  });
});

describe('useWorkbookManager', () => {
  beforeEach(() => {
    mockUseWorkbookStore.mockReturnValue(mockStoreState);
    jest.clearAllMocks();
  });

  it('returns store state and methods', () => {
    const TestComponent = () => {
      const manager = useWorkbookManager();
      return (
        <div>
          <span data-testid="workbooks-count">{manager.workbooks.length}</span>
          <span data-testid="loading">{manager.loading.toString()}</span>
        </div>
      );
    };

    render(<TestComponent />);
    
    expect(screen.getByTestId('workbooks-count')).toHaveTextContent('0');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
  });
});