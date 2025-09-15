import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MainContent } from '@/components/layout/MainContent';
import { useWorkbookStore } from '@/stores/workbookStore';
import { Workbook, Notebook } from '@ai-jupyter/shared';

// Mock the store
jest.mock('@/stores/workbookStore');
const mockUseWorkbookStore = useWorkbookStore as jest.MockedFunction<typeof useWorkbookStore>;

const mockWorkbook: Workbook = {
  id: 'wb_1',
  name: 'Test Workbook',
  description: 'Test workbook description',
  notebooks: [
    {
      id: 'nb_1',
      title: 'Test Notebook',
      description: 'Test notebook description',
      workbookId: 'wb_1',
      cells: [{ id: 'cell_1' } as any],
      metadata: {},
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-02'),
      version: 1
    }
  ],
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01')
};

const mockNotebook: Notebook = mockWorkbook.notebooks[0];

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

describe('MainContent', () => {
  beforeEach(() => {
    mockUseWorkbookStore.mockReturnValue(mockStoreState);
    jest.clearAllMocks();
  });

  it('renders welcome screen when no workbook is selected', () => {
    render(<MainContent />);
    
    expect(screen.getByText('AI Jupyter Notebook Platform')).toBeInTheDocument();
    expect(screen.getByText('AI-powered engineering simulation platform with Jupyter notebooks and NVIDIA PhysX AI integration.')).toBeInTheDocument();
    expect(screen.getByText('Create workbooks to organize your simulation projects')).toBeInTheDocument();
  });

  it('renders workbook view when workbook is selected but no notebook', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook
    });

    render(<MainContent />);
    
    expect(screen.getByText('Test Workbook')).toBeInTheDocument();
    expect(screen.getByText('Test workbook description')).toBeInTheDocument();
    expect(screen.getByText('Test Notebook')).toBeInTheDocument();
  });

  it('renders notebook view when both workbook and notebook are selected', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook,
      selectedNotebook: mockNotebook
    });

    render(<MainContent />);
    
    expect(screen.getByText('Test Notebook')).toBeInTheDocument();
    expect(screen.getByText('Notebook Editor Coming Soon')).toBeInTheDocument();
    expect(screen.getByText('Cells: 1')).toBeInTheDocument();
    expect(screen.getByText('Version: 1')).toBeInTheDocument();
  });

  it('shows empty state when workbook has no notebooks', () => {
    const emptyWorkbook = { ...mockWorkbook, notebooks: [] };
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: emptyWorkbook
    });

    render(<MainContent />);
    
    expect(screen.getByText('No notebooks yet')).toBeInTheDocument();
    expect(screen.getByText('Create your first notebook to start building simulations')).toBeInTheDocument();
  });

  it('allows clicking on notebook cards to select them', () => {
    const mockSelectNotebook = jest.fn();
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook,
      selectNotebook: mockSelectNotebook
    });

    // Mock the store's getState method
    useWorkbookStore.getState = jest.fn().mockReturnValue({
      selectNotebook: mockSelectNotebook
    });

    render(<MainContent />);
    
    const notebookCard = screen.getByText('Test Notebook').closest('div');
    fireEvent.click(notebookCard!);
    
    expect(mockSelectNotebook).toHaveBeenCalledWith(mockNotebook);
  });

  it('shows breadcrumb navigation in notebook view', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook,
      selectedNotebook: mockNotebook
    });

    render(<MainContent />);
    
    expect(screen.getByText('Test Workbook')).toBeInTheDocument();
    expect(screen.getByText('Test Notebook')).toBeInTheDocument();
    expect(screen.getByText('/')).toBeInTheDocument();
  });

  it('allows navigation back to workbook view from notebook view', () => {
    const mockSelectNotebook = jest.fn();
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook,
      selectedNotebook: mockNotebook,
      selectNotebook: mockSelectNotebook
    });

    // Mock the store's getState method
    useWorkbookStore.getState = jest.fn().mockReturnValue({
      selectNotebook: mockSelectNotebook
    });

    render(<MainContent />);
    
    const breadcrumbLink = screen.getByText('Test Workbook');
    fireEvent.click(breadcrumbLink);
    
    expect(mockSelectNotebook).toHaveBeenCalledWith(null);
  });

  it('displays notebook metadata correctly', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook,
      selectedNotebook: mockNotebook
    });

    render(<MainContent />);
    
    expect(screen.getByText('Cells: 1')).toBeInTheDocument();
    expect(screen.getByText('Version: 1')).toBeInTheDocument();
    expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
  });

  it('displays notebook card information correctly in workbook view', () => {
    mockUseWorkbookStore.mockReturnValue({
      ...mockStoreState,
      selectedWorkbook: mockWorkbook
    });

    render(<MainContent />);
    
    expect(screen.getByText('Test Notebook')).toBeInTheDocument();
    expect(screen.getByText('Test notebook description')).toBeInTheDocument();
    expect(screen.getByText('v1')).toBeInTheDocument();
    expect(screen.getByText('1 cells')).toBeInTheDocument();
    expect(screen.getByText('1/1/2024')).toBeInTheDocument();
  });
});