import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { api } from '../api';

export default function AdminStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Get auth token from Redux store
  const { token } = useSelector(state => state.auth);

  useEffect(() => {
    async function fetchStats() {
      setError('');
      setLoading(true);
      try {
        // Simulate stats: count users by role (since no dedicated endpoint)
        const res = await api.get('/users/');
        const users = res.data;
        const stats = {
          total: users.length,
          students: users.filter(u => u.role === 'student').length,
          instructors: users.filter(u => u.role === 'instructor').length,
          admins: users.filter(u => u.role === 'admin').length,
        };
        setStats(stats);
      } catch (err) {
        setError('Failed to fetch stats');
      } finally {
        setLoading(false);
      }
    }
    if (token) fetchStats();
  }, [token]);

  return (
    <div className="w-full max-w-4xl mx-auto mt-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-4 transition-colors duration-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">User Summary</h2>
        
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
        
        {/* Stats display */}
        {stats && !loading && !error && (
          <div className="grid grid-cols-2 gap-4">
            <div className="text-gray-700 dark:text-gray-300 font-medium">Total Users:</div>
            <div className="text-gray-900 dark:text-white">{stats.total}</div>
            
            <div className="text-gray-700 dark:text-gray-300 font-medium">Students:</div>
            <div className="text-gray-900 dark:text-white">{stats.students}</div>
            
            <div className="text-gray-700 dark:text-gray-300 font-medium">Instructors:</div>
            <div className="text-gray-900 dark:text-white">{stats.instructors}</div>
            
            <div className="text-gray-700 dark:text-gray-300 font-medium">Admins:</div>
            <div className="text-gray-900 dark:text-white">{stats.admins}</div>
          </div>
        )}
      </div>
    </div>
  );
}
