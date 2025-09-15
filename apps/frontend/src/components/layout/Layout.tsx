'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { MainContent } from './MainContent';
import { ChatInterface } from '../chat/ChatInterface';
import { ChatToggleButton } from '../chat/ChatToggleButton';

interface LayoutProps {
  children?: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="layout-container">
      <Sidebar />
      <MainContent />
      <ChatToggleButton />
      <ChatInterface />
      {children}
    </div>
  );
};