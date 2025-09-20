'use client';

import React from 'react';

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  return (
    <div className={`sidebar w-64 bg-gray-100 border-r border-gray-200 min-h-screen ${className}`}>
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Workbooks
        </h2>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <span className="text-4xl">📚</span>
          </div>
          <p className="text-sm text-gray-500">
            No workbooks yet
          </p>
          <button className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors">
            Create Workbook
          </button>
        </div>
      </div>
    </div>
  );
};