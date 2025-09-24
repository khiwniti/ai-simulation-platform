'use client';

import React from 'react';

interface MainContentProps {
  className?: string;
}

export const MainContent: React.FC<MainContentProps> = ({ className = '' }) => {
  const renderWelcomeScreen = () => (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="max-w-md">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          AI Jupyter Notebook Platform
        </h1>
        <p className="text-gray-600 mb-6">
          AI-powered engineering simulation platform with Jupyter notebooks and NVIDIA PhysX AI integration.
        </p>
        <div className="space-y-3 text-left">
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-2">📚</span>
            Create workbooks to organize your simulation projects
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-2">📓</span>
            Add notebooks for interactive physics simulations
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-2">🤖</span>
            Get AI assistance from specialized physics agents
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-2">🎮</span>
            Leverage NVIDIA PhysX AI for advanced simulations
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`main-content min-h-screen bg-white ${className}`}>
      {renderWelcomeScreen()}
    </div>
  );
};