'use client'

import { useState, useEffect } from 'react'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)

  // Enhanced Web3/MetaMask prevention
  useEffect(() => {
    const preventWeb3Completely = () => {
      try {
        // Multiple layers of ethereum object blocking
        if (typeof window !== 'undefined') {
          // Delete any existing ethereum object
          delete (window as any).ethereum;
          delete (window as any).web3;
          delete (window as any).Web3;
          
          // Create permanent blocks
          Object.defineProperty(window, 'ethereum', {
            get: () => undefined,
            set: () => false,
            configurable: false,
            enumerable: false
          });
          
          Object.defineProperty(window, 'web3', {
            get: () => undefined,
            set: () => false,
            configurable: false,
            enumerable: false
          });
          
          // Block common Web3 detection patterns
          const blockWeb3Detection = () => {
            const scripts = document.querySelectorAll('script');
            scripts.forEach(script => {
              if (script.src && script.src.includes('metamask')) {
                script.remove();
              }
            });
          };
          
          // Run blocking immediately and on DOM changes
          blockWeb3Detection();
          
          // Observer to block any dynamically added Web3 scripts
          const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
              mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                  const element = node as Element;
                  if (element.tagName === 'SCRIPT') {
                    const script = element as HTMLScriptElement;
                    if (script.src && script.src.includes('metamask')) {
                      script.remove();
                    }
                  }
                }
              });
            });
          });
          
          observer.observe(document.body, {
            childList: true,
            subtree: true
          });
          
          // Override any potential Web3 provider injection
          const originalDefineProperty = Object.defineProperty;
          Object.defineProperty = function(obj, prop, descriptor) {
            if (prop === 'ethereum' || prop === 'web3' || prop === 'Web3') {
              return obj; // Block Web3 property definitions
            }
            return originalDefineProperty.call(this, obj, prop, descriptor);
          };
        }
      } catch (error) {
        // Silently handle any errors
      }
    };

    preventWeb3Completely();
    
    // Run prevention multiple times to catch late injections
    const intervals = [100, 500, 1000, 2000];
    intervals.forEach(delay => {
      setTimeout(preventWeb3Completely, delay);
    });
    
  }, [])

  const handleNavigateToApp = () => {
    setIsLoading(true)
    // Redirect to the actual frontend app
    window.location.href = '/app'
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          <div className="mb-8">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
              AI Jupyter Platform
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              AI-powered engineering simulation platform with interactive Jupyter notebooks
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 rounded-lg p-6">
              <div className="text-blue-600 text-3xl mb-3">🧠</div>
              <h3 className="font-semibold text-gray-900 mb-2">AI-Powered</h3>
              <p className="text-gray-600 text-sm">
                Intelligent code suggestions and automated analysis
              </p>
            </div>
            
            <div className="bg-green-50 rounded-lg p-6">
              <div className="text-green-600 text-3xl mb-3">📊</div>
              <h3 className="font-semibold text-gray-900 mb-2">Visualizations</h3>
              <p className="text-gray-600 text-sm">
                Interactive 3D physics simulations and data plots
              </p>
            </div>
            
            <div className="bg-purple-50 rounded-lg p-6">
              <div className="text-purple-600 text-3xl mb-3">⚡</div>
              <h3 className="font-semibold text-gray-900 mb-2">Real-time</h3>
              <p className="text-gray-600 text-sm">
                Live collaboration and instant feedback
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <button
              onClick={handleNavigateToApp}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 text-lg"
            >
              {isLoading ? 'Loading...' : 'Launch Platform'}
            </button>
            
            <div className="text-sm text-gray-500">
              <p>✅ Frontend Ready • ✅ Next.js 14 • ✅ TypeScript • ✅ Tailwind CSS</p>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-4 text-sm text-gray-600">
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              System Online
            </span>
            <span className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
              Ready for Development
            </span>
          </div>
        </div>
      </div>
    </main>
  )
}