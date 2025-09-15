'use client';

import React, { useState } from 'react';
import { useWorkbookStore } from '@/stores/workbookStore';
import { Workbook, Notebook } from '@ai-jupyter/shared';

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const {
    workbooks,
    selectedWorkbook,
    selectedNotebook,
    selectWorkbook,
    selectNotebook,
    addWorkbook,
    addNotebook,
    deleteWorkbook,
    deleteNotebook
  } = useWorkbookStore();

  const [expandedWorkbooks, setExpandedWorkbooks] = useState<Set<string>>(new Set());
  const [showNewWorkbookForm, setShowNewWorkbookForm] = useState(false);
  const [showNewNotebookForm, setShowNewNotebookForm] = useState<string | null>(null);
  const [newWorkbookName, setNewWorkbookName] = useState('');
  const [newNotebookName, setNewNotebookName] = useState('');

  const toggleWorkbook = (workbookId: string) => {
    const newExpanded = new Set(expandedWorkbooks);
    if (newExpanded.has(workbookId)) {
      newExpanded.delete(workbookId);
    } else {
      newExpanded.add(workbookId);
    }
    setExpandedWorkbooks(newExpanded);
  };

  const handleCreateWorkbook = () => {
    if (newWorkbookName.trim()) {
      const newWorkbook: Workbook = {
        id: `wb_${Date.now()}`,
        name: newWorkbookName.trim(),
        description: '',
        notebooks: [],
        createdAt: new Date(),
        updatedAt: new Date()
      };
      addWorkbook(newWorkbook);
      setNewWorkbookName('');
      setShowNewWorkbookForm(false);
    }
  };

  const handleCreateNotebook = (workbookId: string) => {
    if (newNotebookName.trim()) {
      const newNotebook: Notebook = {
        id: `nb_${Date.now()}`,
        title: newNotebookName.trim(),
        description: '',
        workbookId,
        cells: [],
        metadata: {},
        createdAt: new Date(),
        updatedAt: new Date(),
        version: 1
      };
      addNotebook(workbookId, newNotebook);
      setNewNotebookName('');
      setShowNewNotebookForm(null);
    }
  };

  const handleDeleteWorkbook = (workbook: Workbook, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${workbook.name}" and all its notebooks?`)) {
      deleteWorkbook(workbook.id);
    }
  };

  const handleDeleteNotebook = (notebook: Notebook, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${notebook.title}"?`)) {
      deleteNotebook(notebook.id);
    }
  };

  return (
    <div className={`sidebar ${className}`}>
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Workbooks
          </h2>
          <button
            onClick={() => setShowNewWorkbookForm(true)}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            title="Create new workbook"
          >
            +
          </button>
        </div>

        {showNewWorkbookForm && (
          <div className="mb-4 p-3 bg-gray-100 dark:bg-gray-800 rounded">
            <input
              type="text"
              value={newWorkbookName}
              onChange={(e) => setNewWorkbookName(e.target.value)}
              placeholder="Workbook name"
              className="w-full px-2 py-1 text-sm border rounded mb-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateWorkbook();
                if (e.key === 'Escape') {
                  setShowNewWorkbookForm(false);
                  setNewWorkbookName('');
                }
              }}
            />
            <div className="flex gap-2">
              <button
                onClick={handleCreateWorkbook}
                className="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600"
              >
                Create
              </button>
              <button
                onClick={() => {
                  setShowNewWorkbookForm(false);
                  setNewWorkbookName('');
                }}
                className="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {workbooks.length === 0 && !showNewWorkbookForm && (
          <div className="text-gray-500 dark:text-gray-400 text-sm text-center py-8">
            No workbooks yet. Create your first workbook to get started.
          </div>
        )}

        <div className="space-y-2">
          {workbooks.map((workbook) => (
            <div key={workbook.id} className="border rounded dark:border-gray-600">
              <div
                className={`flex items-center justify-between p-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 rounded ${
                  selectedWorkbook?.id === workbook.id ? 'bg-blue-100 dark:bg-blue-900' : ''
                }`}
                onClick={() => {
                  selectWorkbook(workbook);
                  toggleWorkbook(workbook.id);
                }}
              >
                <div className="flex items-center flex-1">
                  <span className="mr-2 text-gray-500">
                    {expandedWorkbooks.has(workbook.id) ? '▼' : '▶'}
                  </span>
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
                    {workbook.name}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowNewNotebookForm(workbook.id);
                    }}
                    className="px-1 py-1 text-xs text-gray-500 hover:text-blue-500"
                    title="Add notebook"
                  >
                    +
                  </button>
                  <button
                    onClick={(e) => handleDeleteWorkbook(workbook, e)}
                    className="px-1 py-1 text-xs text-gray-500 hover:text-red-500"
                    title="Delete workbook"
                  >
                    ×
                  </button>
                </div>
              </div>

              {expandedWorkbooks.has(workbook.id) && (
                <div className="pl-6 pb-2">
                  {showNewNotebookForm === workbook.id && (
                    <div className="mb-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <input
                        type="text"
                        value={newNotebookName}
                        onChange={(e) => setNewNotebookName(e.target.value)}
                        placeholder="Notebook name"
                        className="w-full px-2 py-1 text-xs border rounded mb-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleCreateNotebook(workbook.id);
                          if (e.key === 'Escape') {
                            setShowNewNotebookForm(null);
                            setNewNotebookName('');
                          }
                        }}
                      />
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleCreateNotebook(workbook.id)}
                          className="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600"
                        >
                          Create
                        </button>
                        <button
                          onClick={() => {
                            setShowNewNotebookForm(null);
                            setNewNotebookName('');
                          }}
                          className="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  {workbook.notebooks.length === 0 && showNewNotebookForm !== workbook.id && (
                    <div className="text-xs text-gray-400 py-2">No notebooks</div>
                  )}

                  {workbook.notebooks.map((notebook) => (
                    <div
                      key={notebook.id}
                      className={`flex items-center justify-between p-1 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-xs ${
                        selectedNotebook?.id === notebook.id ? 'bg-blue-50 dark:bg-blue-800' : ''
                      }`}
                      onClick={() => selectNotebook(notebook)}
                    >
                      <span className="text-gray-700 dark:text-gray-300 truncate flex-1">
                        📓 {notebook.title}
                      </span>
                      <button
                        onClick={(e) => handleDeleteNotebook(notebook, e)}
                        className="px-1 text-gray-400 hover:text-red-500"
                        title="Delete notebook"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};