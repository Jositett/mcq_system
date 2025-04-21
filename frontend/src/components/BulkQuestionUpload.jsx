import React, { useRef, useState } from 'react';
import { useSelector } from 'react-redux';
import Papa from 'papaparse';
import { api } from '../api';

export default function BulkQuestionUpload() {
  const fileInput = useRef();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState([]);
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });
  
  // Get auth token from Redux store
  const { token } = useSelector(state => state.auth);

  // Show notification
  const showNotification = (message, type = 'success') => {
    setNotification({ show: true, message, type });
    setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
    }, 3000);
  };

  const handleFile = (e) => {
    setError('');
    setPreview([]);
    const file = e.target.files[0];
    if (!file) return;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.errors.length) {
          setError('CSV parse error: ' + results.errors[0].message);
        } else {
          setPreview(results.data);
        }
      }
    });
  };

  const handleUpload = async () => {
    if (!preview.length) return;
    setUploading(true);
    setError('');
    try {
      await api.post('/tests/questions/bulk', preview);
      showNotification('Bulk question upload successful!', 'success');
      setPreview([]);
      fileInput.current.value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Bulk upload failed');
      showNotification('Bulk upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mt-4 w-full max-w-3xl">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-4 transition-colors duration-200">
        {/* Notification */}
        {notification.show && (
          <div className={`mb-4 p-3 rounded-md ${notification.type === 'success' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'}`}>
            {notification.message}
          </div>
        )}
        
        <h2 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Bulk Add Questions to Tests</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Download the <a href="/bulk_questions_template.csv" target="_blank" rel="noopener" className="text-blue-600 dark:text-blue-400 hover:underline">CSV template</a> and fill in question details. Then upload the completed file below.
        </p>
        <p className="text-gray-700 dark:text-gray-300 mb-4 font-medium">
          <span className="font-semibold">Question Types:</span> mcq, true_false, short_answer
        </p>
        
        <input type="file" accept=".csv" ref={fileInput} onChange={handleFile} className="hidden" />
        
        <div className="flex flex-wrap gap-3 mb-4">
          <button 
            onClick={() => fileInput.current.click()} 
            disabled={uploading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            Choose CSV
          </button>
          
          <button 
            onClick={handleUpload} 
            disabled={!preview.length || uploading}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            Upload
          </button>
          
          {uploading && (
            <div className="ml-2 flex items-center">
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-blue-500"></div>
              <span className="ml-2 text-gray-600 dark:text-gray-300">Uploading...</span>
            </div>
          )}
        </div>
        
        {error && (
          <div className="mb-4 p-3 rounded-md bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200">
            {error}
          </div>
        )}
        
        {preview.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Preview ({preview.length} questions):</h3>
            <div className="max-h-40 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-md p-2 bg-gray-50 dark:bg-gray-900/50">
              <ul className="space-y-1">
                {preview.map((row, idx) => (
                  <li key={idx} className="text-sm text-gray-600 dark:text-gray-300">
                    {row.test_name} - {row.question_text} ({row.question_type})
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
