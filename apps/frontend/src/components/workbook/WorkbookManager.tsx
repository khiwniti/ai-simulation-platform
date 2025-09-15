'use client';

import React, { useEffect } from 'react';
import { useWorkbookStore } from '@/stores/workbookStore';
import { Workbook } from '@ai-jupyter/shared';

interface WorkbookManagerProps {
  className?: string;
}

export const WorkbookManager: React.FC<WorkbookManagerProps> = ({ className = '' }) => {
  const {
    workbooks,
    loading,
    error,
    setWorkbooks,
    setLoading,
    setError,
    addWorkbook,
    updateWorkbook,
    deleteWorkbook
  } = useWorkbookStore();

  // Simulate API calls - in real implementation, these would be actual API calls
  const loadWorkbooks = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock data for demonstration
      const mockWorkbooks: Workbook[] = [
        {
          id: 'wb_1',
          name: 'Physics Simulations',
          description: 'Collection of physics simulation notebooks',
          notebooks: [
            {
              id: 'nb_1',
              title: 'Particle Dynamics',
              description: 'Basic particle physics simulation',
              workbookId: 'wb_1',
              cells: [],
              metadata: {},
              createdAt: new Date('2024-01-15'),
              updatedAt: new Date('2024-01-20'),
              version: 1
            },
            {
              id: 'nb_2',
              title: 'Fluid Dynamics',
              description: 'Water flow simulation using PhysX',
              workbookId: 'wb_1',
              cells: [],
              metadata: {},
              createdAt: new Date('2024-01-18'),
              updatedAt: new Date('2024-01-22'),
              version: 2
            }
          ],
          createdAt: new Date('2024-01-15'),
          updatedAt: new Date('2024-01-22')
        },
        {
          id: 'wb_2',
          name: 'Engineering Analysis',
          description: 'Structural and mechanical analysis notebooks',
          notebooks: [
            {
              id: 'nb_3',
              title: 'Beam Analysis',
              description: 'Structural beam stress analysis',
              workbookId: 'wb_2',
              cells: [],
              metadata: {},
              createdAt: new Date('2024-01-10'),
              updatedAt: new Date('2024-01-25'),
              version: 1
            }
          ],
          createdAt: new Date('2024-01-10'),
          updatedAt: new Date('2024-01-25')
        }
      ];
      
      setWorkbooks(mockWorkbooks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load workbooks');
    } finally {
      setLoading(false);
    }
  };

  const createWorkbook = async (name: string, description: string = '') => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const newWorkbook: Workbook = {
        id: `wb_${Date.now()}`,
        name,
        description,
        notebooks: [],
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      addWorkbook(newWorkbook);
      return newWorkbook;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create workbook');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateWorkbookData = async (id: string, updates: Partial<Workbook>) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      updateWorkbook(id, { ...updates, updatedAt: new Date() });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update workbook');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteWorkbookData = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      deleteWorkbook(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete workbook');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Load workbooks on component mount
  useEffect(() => {
    if (workbooks.length === 0) {
      loadWorkbooks();
    }
  }, []);

  // Expose methods for external use
  React.useImperativeHandle(React.createRef(), () => ({
    loadWorkbooks,
    createWorkbook,
    updateWorkbook: updateWorkbookData,
    deleteWorkbook: deleteWorkbookData
  }));

  if (loading && workbooks.length === 0) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading workbooks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded">
          <div className="flex items-center">
            <span className="mr-2">⚠️</span>
            <div>
              <strong className="font-bold">Error:</strong>
              <span className="block sm:inline ml-1">{error}</span>
            </div>
          </div>
          <button
            onClick={loadWorkbooks}
            className="mt-2 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // This component manages workbook state but doesn't render UI directly
  // The actual UI is handled by Sidebar and MainContent components
  return null;
};

// Export the manager functions for use in other components
export const useWorkbookManager = () => {
  const store = useWorkbookStore();
  
  return {
    ...store,
    // Add any additional manager-specific methods here
  };
};