import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchInstructorTests, deleteTest } from '../features/testSlice';
import ConfirmDialog from './ConfirmDialog';

export default function InstructorTests() {
  const dispatch = useDispatch();
  const { user } = useSelector(state => state.auth);
  const { tests, status, error } = useSelector(state => state.tests);
  const loading = status === 'loading';
  
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [targetTest, setTargetTest] = useState(null);
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });

  // Show notification
  const showNotification = (message, type = 'success') => {
    setNotification({ show: true, message, type });
    setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
    }, 3000);
  };

  useEffect(() => {
    if (user?.id) {
      dispatch(fetchInstructorTests(user.id));
    }
  }, [dispatch, user]);

  const handleDelete = (test) => {
    setTargetTest(test);
    setConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!targetTest) return;
    try {
      await dispatch(deleteTest(targetTest.id)).unwrap();
      showNotification(`Test '${targetTest.title || targetTest.id}' deleted.`, 'success');
    } catch (err) {
      showNotification(err.message || 'Failed to delete test', 'error');
    } finally {
      setConfirmOpen(false);
      setTargetTest(null);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-4 transition-colors duration-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">My Tests</h2>
        
        {/* Notification */}
        {notification.show && (
          <div className={`mb-4 p-3 rounded-md ${notification.type === 'success' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'}`}>
            {notification.message}
          </div>
        )}
        
        {/* Loading state */}
        {loading && (
          <div className="flex justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
          </div>
        )}
        
        {/* Error state */}
        {error && (
          <div className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 p-3 rounded-md mb-4">
            {error}
          </div>
        )}
        
        {/* Tests list */}
        {!loading && !error && (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {tests.length === 0 ? (
              <li className="py-3 text-gray-500 dark:text-gray-400">No tests found.</li>
            ) : (
              tests.map((test, i) => (
                <li key={i} className="py-3 flex justify-between items-center">
                  <div>
                    <h3 className="text-gray-800 dark:text-white font-medium">{test.title || `Test #${test.id}`}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">ID: {test.id}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(test)}
                    className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-1 rounded-full hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors duration-200"
                    aria-label={`Delete test ${test.title || test.id}`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </li>
              ))
            )}
          </ul>
        )}
        
        {/* Confirmation Dialog */}
        <ConfirmDialog
          open={confirmOpen}
          title="Confirm Delete"
          content={targetTest ? `Are you sure you want to delete test '${targetTest.title || targetTest.id}'?` : ''}
          onClose={() => setConfirmOpen(false)}
          onConfirm={confirmDelete}
        />
      </div>
    </div>
  );
}
