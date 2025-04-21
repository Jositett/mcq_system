import React, { createContext, useContext, useState, useCallback, Fragment } from 'react';
import { Transition } from '@headlessui/react';

const ToastContext = createContext();

export function ToastProvider({ children }) {
  const [toast, setToast] = useState({ open: false, message: '', type: 'info' });

  const showToast = useCallback((message, type = 'info') => {
    setToast({ open: true, message, type });
    // Auto-hide after 4 seconds
    setTimeout(() => {
      setToast(t => ({ ...t, open: false }));
    }, 4000);
  }, []);

  const handleClose = () => setToast(t => ({ ...t, open: false }));

  // Get the appropriate styling based on toast type
  const getToastStyles = (type) => {
    switch(type) {
      case 'success':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-green-300 dark:border-green-800';
      case 'error':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 border-red-300 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 border-yellow-300 dark:border-yellow-800';
      case 'info':
      default:
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-blue-300 dark:border-blue-800';
    }
  };

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      
      {/* Toast notification */}
      <div className="fixed bottom-4 inset-x-0 flex justify-center items-center z-50 pointer-events-none">
        <Transition
          show={toast.open}
          as={Fragment}
          enter="transform ease-out duration-300 transition"
          enterFrom="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
          enterTo="translate-y-0 opacity-100 sm:translate-x-0"
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div 
            className={`max-w-sm w-full shadow-lg rounded-lg pointer-events-auto border ${getToastStyles(toast.type)} p-4`}
          >
            <div className="flex items-start">
              <div className="flex-1">
                <p className="text-sm font-medium">{toast.message}</p>
              </div>
              <div className="ml-4 flex-shrink-0 flex">
                <button
                  onClick={handleClose}
                  className="inline-flex rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
