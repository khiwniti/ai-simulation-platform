import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Jupyter Notebook Platform',
  description: 'AI-powered engineering simulation platform with Jupyter notebooks',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Comprehensive Web3/MetaMask prevention script
              (function() {
                'use strict';
                
                // Immediately override console methods to suppress MetaMask errors
                const originalConsoleError = console.error;
                const originalConsoleWarn = console.warn;
                const originalConsoleLog = console.log;
                
                console.error = function(...args) {
                  const message = args.join(' ').toLowerCase();
                  if (message.includes('metamask') || 
                      message.includes('ethereum') || 
                      message.includes('wallet') ||
                      message.includes('web3') ||
                      message.includes('connect') && message.includes('failed')) {
                    return; // Suppress Web3-related errors
                  }
                  originalConsoleError.apply(console, args);
                };
                
                console.warn = function(...args) {
                  const message = args.join(' ').toLowerCase();
                  if (message.includes('metamask') || message.includes('ethereum') || message.includes('wallet')) {
                    return; // Suppress Web3-related warnings
                  }
                  originalConsoleWarn.apply(console, args);
                };
                
                // Override window.ethereum completely
                Object.defineProperty(window, 'ethereum', {
                  get: function() {
                    return undefined;
                  },
                  set: function() {
                    return false;
                  },
                  configurable: false,
                  enumerable: false
                });
                
                // Block common Web3 globals
                const web3Globals = ['web3', 'Web3', 'ethereum', 'metamask', 'MetaMask'];
                web3Globals.forEach(global => {
                  try {
                    Object.defineProperty(window, global, {
                      get: function() { return undefined; },
                      set: function() { return false; },
                      configurable: false,
                      enumerable: false
                    });
                  } catch (e) {
                    // Ignore errors when overriding
                  }
                });
                
                // Override document.addEventListener to block Web3 events
                const originalAddEventListener = document.addEventListener;
                document.addEventListener = function(type, listener, options) {
                  if (type === 'DOMContentLoaded' && listener.toString().includes('ethereum')) {
                    return; // Block Web3-related DOM listeners
                  }
                  return originalAddEventListener.call(this, type, listener, options);
                };
                
                // Override window.addEventListener for Web3 events
                const originalWindowAddEventListener = window.addEventListener;
                window.addEventListener = function(type, listener, options) {
                  if ((type === 'load' || type === 'DOMContentLoaded') && 
                      listener.toString().includes('ethereum')) {
                    return; // Block Web3-related window listeners
                  }
                  return originalWindowAddEventListener.call(this, type, listener, options);
                };
                
                // Prevent extension script injection
                const originalCreateElement = document.createElement;
                document.createElement = function(tagName) {
                  const element = originalCreateElement.call(this, tagName);
                  if (tagName.toLowerCase() === 'script') {
                    const originalSetAttribute = element.setAttribute;
                    element.setAttribute = function(name, value) {
                      if (name === 'src' && value && value.includes('metamask')) {
                        return; // Block MetaMask script loading
                      }
                      return originalSetAttribute.call(this, name, value);
                    };
                  }
                  return element;
                };
                
                // Block fetch requests to Web3 endpoints
                const originalFetch = window.fetch;
                window.fetch = function(input, init) {
                  const url = typeof input === 'string' ? input : input.url;
                  if (url && (url.includes('metamask') || url.includes('ethereum') || url.includes('web3'))) {
                    return Promise.reject(new Error('Web3 requests blocked'));
                  }
                  return originalFetch.call(this, input, init);
                };
                
                // Suppress unhandled promise rejections from Web3
                window.addEventListener('unhandledrejection', function(event) {
                  const reason = event.reason?.message || event.reason || '';
                  if (typeof reason === 'string' && 
                      (reason.includes('MetaMask') || 
                       reason.includes('ethereum') || 
                       reason.includes('wallet') ||
                       reason.includes('connect'))) {
                    event.preventDefault();
                    event.stopPropagation();
                  }
                });
                
                // Block error events from Web3
                window.addEventListener('error', function(event) {
                  const message = event.message || '';
                  if (message.includes('MetaMask') || 
                      message.includes('ethereum') || 
                      message.includes('wallet')) {
                    event.preventDefault();
                    event.stopPropagation();
                  }
                });
                
              })();
            `,
          }}
        />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}