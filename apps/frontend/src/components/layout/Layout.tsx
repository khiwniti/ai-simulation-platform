'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { MainContent } from './MainContent';

interface LayoutProps {
  children?: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="layout-container flex min-h-screen bg-white">
      <Sidebar />
      <div className="flex-1">
        <MainContent />
        {children}
      </div>
    </div>
  );
};