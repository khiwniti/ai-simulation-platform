import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { useWorkbookStore } from '@/stores/workbookStore';
import { Workbook } from '@ai-jupyter/shared';

// Mock the store
jest.mock('@/stores/workbookStore');
const mockUseWorkbookStore = useWorkbookStore as jest.MockedFunction<typeof useWorkbookStore>;

const mockWorkbook: Workbook = {
  id: 'wb_1',
  name: 'Test Workbook',
  description: 'Test description',
  notebooks: [
    {
      id: 'nb_1',
      title: 'Test Notebook',
      description: 'Test notebook',
      workbookId: 'wb_1',
      cells: [],
      metadata: {},
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-01'),
      version: 1
    }
  ],
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01')
};

const mockStoreState = {
  workbooks: [mockWorkbook],
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

describe('Sidebar', () => {
  beforeEach(() => {
    mockUseWorkbookStore.mockReturnValue(mockStoreState);
    jest.clearAllMocks();
  });

  it('renders workbooks title and create button', () => {
    render(<Sidebar />);
    
    expect(screen.getByText('Workbooks')).toBeInTheDocument();
    expect(screen.getByTitle('Create new workbook')).toBeInTheDocument();
  });

  it('displays workbooks from store', () => {
    render(<Sidebar />);
    
    expect(screen.getByText('Test Workbook')).toBeInTheDocument();
  });

  it('shows empty state when no workbooks exist', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      workbooks: []
    });

    render(<Sidebar />);
    
    expect(screen.getByText('No workbooks yet. Create your first workbook to get started.')).toBeInTheDocument();
  });

  it('opens new workbook form when create button is clicked', () => {
    render(<Sidebar />);
    
    const createButton = screen.getByTitle('Create new workbook');
    fireEvent.click(createButton);
    
    expect(screen.getByPlaceholderText('Workbook name')).toBeInTheDocument();
    expect(screen.getByText('Create')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('creates a new workbook when form is submitted', async () => {
    render(<Sidebar />);
    
    const createButton = screen.getByTitle('Create new workbook');
    fireEvent.click(createButton);
    
    const input = screen.getByPlaceholderText('Workbook name');
    fireEvent.change(input, { target: { value: 'New Workbook' } });
    
    const submitButton = screen.getByText('Create');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockStoreState.addWorkbook).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'New Workbook',
          description: '',
          notebooks: []
        })
      );
    });
  });

  it('cancels workbook creation when cancel button is clicked', () => {
    render(<Sidebar />);
    
    const createButton = screen.getByTitle('Create new workbook');
    fireEvent.click(createButton);
    
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    expect(screen.queryByPlaceholderText('Workbook name')).not.toBeInTheDocument();
  });

  it('expands workbook when clicked', () => {
    render(<Sidebar />);
    
    const workbookElement = screen.getByText('Test Workbook');
    fireEvent.click(workbookElement.closest('div')!);
    
    expect(mockStoreState.selectWorkbook).toHaveBeenCalledWith(mockWorkbook);
  });

  it('shows notebooks when workbook is expanded', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook
    });

    render(<Sidebar />);
    
    // Simulate expanded state by clicking the workbook
    const workbookElement = screen.getByText('Test Workbook');
    fireEvent.click(workbookElement.closest('div')!);
    
    expect(screen.getByText('📓 Test Notebook')).toBeInTheDocument();
  });

  it('selects notebook when clicked', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook
    });

    render(<Sidebar />);
    
    // First expand the workbook
    const workbookElement = screen.getByText('Test Workbook');
    fireEvent.click(workbookElement.closest('div')!);
    
    // Then click the notebook
    const notebookElement = screen.getByText('📓 Test Notebook');
    fireEvent.click(notebookElement);
    
    expect(mockStoreState.selectNotebook).toHaveBeenCalledWith(mockWorkbook.notebooks[0]);
  });

  it('shows delete confirmation for workbook', () => {
    // Mock window.confirm
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
    
    render(<Sidebar />);
    
    const deleteButton = screen.getByTitle('Delete workbook');
    fireEvent.click(deleteButton);
    
    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete "Test Workbook" and all its notebooks?');
    expect(mockStoreState.deleteWorkbook).toHaveBeenCalledWith('wb_1');
    
    confirmSpy.mockRestore();
  });

  it('handles keyboard navigation in forms', () => {
    render(<Sidebar />);
    
    const createButton = screen.getByTitle('Create new workbook');
    fireEvent.click(createButton);
    
    const input = screen.getByPlaceholderText('Workbook name');
    fireEvent.change(input, { target: { value: 'Test' } });
    
    // Test Enter key
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(mockStoreState.addWorkbook).toHaveBeenCalled();
  });
});