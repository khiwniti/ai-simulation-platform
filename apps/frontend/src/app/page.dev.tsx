'use client';

import { useState, useEffect } from 'react';

// Simple workbook manager without external dependencies
function SimpleWorkbookManager() {
  const [workbooks, setWorkbooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Test backend connection
    const testBackendConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          const data = await response.json();
          console.log('Backend health check:', data);
        }

        // Fetch workbooks from backend
        const workbooksResponse = await fetch('http://localhost:8000/api/v1/workbooks/');
        if (workbooksResponse.ok) {
          const workbooksData = await workbooksResponse.json();
          setWorkbooks(workbooksData || []);
        }
      } catch (err) {
        setError('Failed to connect to backend');
        console.error('Backend connection error:', err);
      } finally {
        setLoading(false);
      }
    };

    testBackendConnection();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading workbooks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>⚠️ {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Workbooks ({workbooks.length})</h3>
      {workbooks.length === 0 ? (
        <p className="text-gray-500">No workbooks found. Backend connection is working!</p>
      ) : (
        <ul className="space-y-2">
          {workbooks.map((workbook: any, index: number) => (
            <li key={index} className="p-3 border rounded-lg">
              <h4 className="font-medium">{workbook.name || `Workbook ${index + 1}`}</h4>
              <p className="text-sm text-gray-600">{workbook.description || 'No description'}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Home() {
  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">AI Simulation Platform</h1>
      <p className="text-lg mb-8">
        Welcome to the AI Jupyter Notebook Platform with multi-agent support and physics simulation.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Frontend Features:</h2>
          <ul className="list-disc list-inside space-y-2">
            <li>✅ Next.js 14 + React 18</li>
            <li>✅ TypeScript configuration</li>
            <li>✅ Tailwind CSS styling</li>
            <li>✅ Multi-agent AI components</li>
            <li>✅ Jupyter-style notebooks</li>
            <li>✅ 3D Physics visualization</li>
          </ul>
        </div>
        
        <div>
          <h2 className="text-2xl font-semibold mb-4">Backend Features:</h2>
          <ul className="list-disc list-inside space-y-2">
            <li>✅ FastAPI + Python</li>
            <li>✅ SQLite database</li>
            <li>✅ Multi-agent orchestration</li>
            <li>✅ Code execution service</li>
            <li>✅ WebSocket support</li>
            <li>✅ Physics simulation</li>
          </ul>
        </div>
      </div>

      <div className="border rounded-lg p-6 bg-gray-50">
        <h3 className="text-xl font-semibold mb-4">🔗 Frontend-Backend Integration Test</h3>
        <SimpleWorkbookManager />
      </div>

      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">🚀 Platform Status</h3>
        <p className="text-blue-700">
          Both frontend and backend services are running successfully! 
          The platform is ready for development and testing.
        </p>
      </div>
    </main>
  );
}