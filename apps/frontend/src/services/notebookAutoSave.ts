/**
 * Notebook auto-save service for frontend
 */

import { Notebook, Cell } from '@ai-jupyter/shared';

interface AutoSaveData {
  cells?: Cell[];
  metadata?: Record<string, any>;
  lastModified?: string;
}

interface AutoSaveStatus {
  isEnabled: boolean;
  lastSaveTime: Date | null;
  interval: number; // milliseconds
  hasUnsavedChanges: boolean;
  isSaving: boolean;
}

class NotebookAutoSaveService {
  private interval: number = 30000; // 30 seconds
  private timers: Map<string, NodeJS.Timeout> = new Map();
  private saveStatus: Map<string, AutoSaveStatus> = new Map();
  private changeTracking: Map<string, Set<string>> = new Map(); // notebook id -> changed cell ids

  constructor() {
    // Listen for page unload to save any pending changes
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', this.saveAllPendingChanges.bind(this));
    }
  }

  /**
   * Enable auto-save for a notebook
   */
  enableAutoSave(notebookId: string, interval?: number): void {
    if (interval) {
      this.interval = interval;
    }

    this.saveStatus.set(notebookId, {
      isEnabled: true,
      lastSaveTime: null,
      interval: this.interval,
      hasUnsavedChanges: false,
      isSaving: false
    });

    this.changeTracking.set(notebookId, new Set());

    // Start auto-save timer
    this.startAutoSaveTimer(notebookId);
  }

  /**
   * Disable auto-save for a notebook
   */
  disableAutoSave(notebookId: string): void {
    const timer = this.timers.get(notebookId);
    if (timer) {
      clearInterval(timer);
      this.timers.delete(notebookId);
    }

    const status = this.saveStatus.get(notebookId);
    if (status) {
      status.isEnabled = false;
    }

    this.changeTracking.delete(notebookId);
  }

  /**
   * Track cell changes for auto-save
   */
  trackCellChange(notebookId: string, cellId: string): void {
    const status = this.saveStatus.get(notebookId);
    if (!status || !status.isEnabled) {
      return;
    }

    // Mark cell as changed
    const changedCells = this.changeTracking.get(notebookId);
    if (changedCells) {
      changedCells.add(cellId);
    }

    // Mark notebook as having unsaved changes
    status.hasUnsavedChanges = true;
  }

  /**
   * Track metadata changes for auto-save
   */
  trackMetadataChange(notebookId: string): void {
    const status = this.saveStatus.get(notebookId);
    if (!status || !status.isEnabled) {
      return;
    }

    status.hasUnsavedChanges = true;
  }

  /**
   * Force save a notebook immediately
   */
  async forceSave(notebook: Notebook): Promise<boolean> {
    const status = this.saveStatus.get(notebook.id);
    if (!status) {
      return false;
    }

    if (status.isSaving) {
      return false; // Already saving
    }

    try {
      status.isSaving = true;
      const success = await this.performAutoSave(notebook);
      
      if (success) {
        status.lastSaveTime = new Date();
        status.hasUnsavedChanges = false;
        this.changeTracking.set(notebook.id, new Set());
      }

      return success;
    } finally {
      status.isSaving = false;
    }
  }

  /**
   * Get auto-save status for a notebook
   */
  getStatus(notebookId: string): AutoSaveStatus | null {
    return this.saveStatus.get(notebookId) || null;
  }

  /**
   * Save all notebooks with pending changes
   */
  async saveAllPendingChanges(): Promise<void> {
    const promises: Promise<any>[] = [];

    for (const [notebookId, status] of this.saveStatus.entries()) {
      if (status.hasUnsavedChanges && !status.isSaving) {
        // This would need access to the notebook data
        // In a real implementation, this would be handled differently
        console.log(`Saving pending changes for notebook ${notebookId}`);
      }
    }

    await Promise.allSettled(promises);
  }

  private startAutoSaveTimer(notebookId: string): void {
    const timer = setInterval(() => {
      const status = this.saveStatus.get(notebookId);
      if (!status || !status.isEnabled || !status.hasUnsavedChanges || status.isSaving) {
        return;
      }

      // This would need access to the current notebook state
      // In practice, this would be triggered by a store subscription
      this.triggerAutoSave(notebookId);
    }, this.interval);

    this.timers.set(notebookId, timer);
  }

  private async triggerAutoSave(notebookId: string): Promise<void> {
    // This would need to get the current notebook state from the store
    // For now, we'll emit an event that the store can listen to
    const event = new CustomEvent('autoSaveRequested', {
      detail: { notebookId }
    });
    
    if (typeof window !== 'undefined') {
      window.dispatchEvent(event);
    }
  }

  private async performAutoSave(notebook: Notebook): Promise<boolean> {
    try {
      const changedCells = this.changeTracking.get(notebook.id) || new Set();
      
      const autoSaveData: AutoSaveData = {
        cells: notebook.cells.filter(cell => changedCells.has(cell.id)),
        metadata: notebook.metadata,
        lastModified: new Date().toISOString()
      };

      const response = await fetch(`/api/v1/notebooks/${notebook.id}/auto-save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(autoSaveData),
      });

      return response.ok;
    } catch (error) {
      console.error('Auto-save failed:', error);
      return false;
    }
  }
}

// Global instance
export const notebookAutoSaveService = new NotebookAutoSaveService();

// React hook for using auto-save
import React from 'react';

export function useNotebookAutoSave(notebook: Notebook | null) {
  const [status, setStatus] = React.useState<AutoSaveStatus | null>(null);

  React.useEffect(() => {
    if (!notebook) {
      return;
    }

    // Enable auto-save
    notebookAutoSaveService.enableAutoSave(notebook.id);

    // Listen for auto-save requests
    const handleAutoSaveRequest = (event: CustomEvent) => {
      if (event.detail.notebookId === notebook.id) {
        notebookAutoSaveService.forceSave(notebook);
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('autoSaveRequested', handleAutoSaveRequest as EventListener);
    }

    // Update status periodically
    const statusTimer = setInterval(() => {
      const currentStatus = notebookAutoSaveService.getStatus(notebook.id);
      setStatus(currentStatus);
    }, 1000);

    return () => {
      notebookAutoSaveService.disableAutoSave(notebook.id);
      
      if (typeof window !== 'undefined') {
        window.removeEventListener('autoSaveRequested', handleAutoSaveRequest as EventListener);
      }
      
      clearInterval(statusTimer);
    };
  }, [notebook?.id]);

  return {
    status,
    trackCellChange: (cellId: string) => {
      if (notebook) {
        notebookAutoSaveService.trackCellChange(notebook.id, cellId);
      }
    },
    trackMetadataChange: () => {
      if (notebook) {
        notebookAutoSaveService.trackMetadataChange(notebook.id);
      }
    },
    forceSave: () => {
      if (notebook) {
        return notebookAutoSaveService.forceSave(notebook);
      }
      return Promise.resolve(false);
    }
  };
}
