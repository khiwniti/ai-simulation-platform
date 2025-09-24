'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, FileText, Zap, Code, Calculator, Beaker, Brain } from 'lucide-react';
import { Button } from '../ui/button';

interface CreateNotebookModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateNotebook: (notebookData: {
    name: string;
    description: string;
    template: string;
    type: string;
  }) => void;
}

const notebookTemplates = [
  {
    id: 'blank',
    name: 'Blank Notebook',
    description: 'Start with an empty notebook',
    icon: FileText,
    type: 'general',
    color: 'from-gray-500 to-gray-600'
  },
  {
    id: 'physics-simulation',
    name: 'Physics Simulation',
    description: 'Pre-configured for physics simulations',
    icon: Zap,
    type: 'physics',
    color: 'from-blue-500 to-purple-600'
  },
  {
    id: 'data-analysis',
    name: 'Data Analysis',
    description: 'Tools for data science and analytics',
    icon: Calculator,
    type: 'data',
    color: 'from-green-500 to-teal-600'
  },
  {
    id: 'ml-experiment',
    name: 'ML Experiment',
    description: 'Machine learning experiment template',
    icon: Brain,
    type: 'ml',
    color: 'from-purple-500 to-pink-600'
  },
  {
    id: 'engineering-analysis',
    name: 'Engineering Analysis',
    description: 'Structural and thermal analysis tools',
    icon: Beaker,
    type: 'engineering',
    color: 'from-orange-500 to-red-600'
  },
  {
    id: 'code-notebook',
    name: 'Code Notebook',
    description: 'General purpose coding environment',
    icon: Code,
    type: 'code',
    color: 'from-indigo-500 to-blue-600'
  }
];

export function CreateNotebookModal({ isOpen, onClose, onCreateNotebook }: CreateNotebookModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState('blank');
  const [notebookName, setNotebookName] = useState('');
  const [notebookDescription, setNotebookDescription] = useState('');

  const handleCreate = () => {
    if (!notebookName.trim()) return;

    const template = notebookTemplates.find(t => t.id === selectedTemplate);
    
    onCreateNotebook({
      name: notebookName,
      description: notebookDescription,
      template: selectedTemplate,
      type: template?.type || 'general'
    });

    // Reset form
    setNotebookName('');
    setNotebookDescription('');
    setSelectedTemplate('blank');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Create New EnsimuNotebook
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    Choose a template and configure your notebook
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onClose}
                  className="p-2"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              <div className="overflow-y-auto max-h-[calc(90vh-8rem)]">
                {/* Template Selection */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Choose a Template
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {notebookTemplates.map((template) => (
                      <motion.div
                        key={template.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all ${
                          selectedTemplate === template.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}
                        onClick={() => setSelectedTemplate(template.id)}
                      >
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`p-2 rounded-lg bg-gradient-to-br ${template.color}`}>
                            <template.icon className="w-5 h-5 text-white" />
                          </div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {template.name}
                          </h4>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {template.description}
                        </p>
                        {selectedTemplate === template.id && (
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="absolute top-2 right-2 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center"
                          >
                            <div className="w-2 h-2 bg-white rounded-full" />
                          </motion.div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Notebook Configuration */}
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Notebook Details
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Notebook Name *
                      </label>
                      <input
                        type="text"
                        value={notebookName}
                        onChange={(e) => setNotebookName(e.target.value)}
                        placeholder="Enter notebook name..."
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Description (Optional)
                      </label>
                      <textarea
                        value={notebookDescription}
                        onChange={(e) => setNotebookDescription(e.target.value)}
                        placeholder="Describe what this notebook will be used for..."
                        rows={3}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {notebookTemplates.find(t => t.id === selectedTemplate)?.name} selected
                </div>
                <div className="flex items-center space-x-3">
                  <Button variant="outline" onClick={onClose}>
                    Cancel
                  </Button>
                  <Button
                    variant="gradient"
                    onClick={handleCreate}
                    disabled={!notebookName.trim()}
                  >
                    Create Notebook
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}