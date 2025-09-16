'use client';

import React from 'react';
import { useWorkbookStore } from '@/stores/workbookStore';

interface MainContentProps {
  className?: string;
}

export const MainContent: React.FC<MainContentProps> = ({ className = '' }) => {
  const { selectedWorkbook, selectedNotebook } = useWorkbookStore();

  const renderWelcomeScreen = () => (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="max-w-md">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          AI Jupyter Notebook Platform
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          AI-powered engineering simulation platform with Jupyter notebooks and NVIDIA PhysX AI integration.
        </p>
        <div className="space-y-3 text-left">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-2">📚</span>
            Create workbooks to organize your simulation projects
          </div>
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-2">📓</span>
            Add notebooks for interactive physics simulations
          </div>
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-2">🤖</span>
            Get AI assistance from specialized physics agents
          </div>
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-2">🎮</span>
            Leverage NVIDIA PhysX AI for advanced simulations
          </div>
        </div>
      </div>
    </div>
  );

  const renderWorkbookView = () => (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
          {selectedWorkbook?.name}
        </h2>
        {selectedWorkbook?.description && (
          <p className="text-gray-600 dark:text-gray-400">
            {selectedWorkbook.description}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {selectedWorkbook?.notebooks.map((notebook) => (
          <div
            key={notebook.id}
            className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer dark:border-gray-600 dark:hover:bg-gray-800"
            onClick={() => useWorkbookStore.getState().selectNotebook(notebook)}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 truncate">
                {notebook.title}
              </h3>
              <span className="text-xs text-gray-500 ml-2">
                v{notebook.version}
              </span>
            </div>
            {notebook.description && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                {notebook.description}
              </p>
            )}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{notebook.cells.length} cells</span>
              <span>
                {new Date(notebook.updatedAt).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}

        {selectedWorkbook?.notebooks.length === 0 && (
          <div className="col-span-full text-center py-12">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <span className="text-4xl">📓</span>
            </div>
            <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400 mb-2">
              No notebooks yet
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Create your first notebook to start building simulations
            </p>
          </div>
        )}
      </div>
    </div>
  );

  const renderNotebookView = () => (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
          <span 
            className="cursor-pointer hover:text-blue-500"
            onClick={() => useWorkbookStore.getState().selectNotebook(null)}
          >
            {selectedWorkbook?.name}
          </span>
          <span className="mx-2">/</span>
          <span>{selectedNotebook?.title}</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
          {selectedNotebook?.title}
        </h2>
        {selectedNotebook?.description && (
          <p className="text-gray-600 dark:text-gray-400">
            {selectedNotebook.description}
          </p>
        )}
      </div>

      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 text-center">
        <div className="text-gray-400 dark:text-gray-500 mb-4">
          <span className="text-4xl">⚡</span>
        </div>
        <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400 mb-2">
          Notebook Editor Coming Soon
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
          The notebook editor with Monaco integration and AI assistance will be implemented in the next task.
        </p>
        <div className="text-xs text-gray-400 dark:text-gray-500 space-y-1">
          <div>Cells: {selectedNotebook?.cells.length || 0}</div>
          <div>Version: {selectedNotebook?.version}</div>
          <div>Last updated: {selectedNotebook ? new Date(selectedNotebook.updatedAt).toLocaleString() : 'N/A'}</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`main-content ${className}`}>
      {!selectedWorkbook && renderWelcomeScreen()}
      {selectedWorkbook && !selectedNotebook && renderWorkbookView()}
      {selectedWorkbook && selectedNotebook && renderNotebookView()}
    </div>
  );
};