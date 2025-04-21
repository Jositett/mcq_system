import React, { useEffect, useState } from 'react';

import axios from 'axios';
import ConfirmDialog from './ConfirmDialog';
import { useToast } from './ToastContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function AdminUsers({ token }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [targetUser, setTargetUser] = useState(null);
  const showToast = useToast();
  const currentUserId = (() => {
    try {
      return JSON.parse(localStorage.getItem('user'))?.id;
    } catch {
      return null;
    }
  })();

  const fetchUsers = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/users/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (token) fetchUsers(); }, [token]);

  const handleDelete = async (user) => {
    setTargetUser(user);
    setConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!targetUser) return;
    try {
      await axios.delete(`${API_URL}/users/${targetUser.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showToast(`User '${targetUser.username}' deleted.`, 'success');
      fetchUsers();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to delete user', 'error');
    } finally {
      setConfirmOpen(false);
      setTargetUser(null);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto mt-6">
      <div className="bg-white rounded shadow p-6 mb-4">
        <h2 className="text-lg font-semibold mb-4">Users</h2>
        {loading && <div className="text-blue-700">Loading...</div>}
        {error && <div className="p-2 bg-red-100 text-red-800 rounded mb-2">{error}</div>}
        {!loading && !error && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border px-3 py-2">Username</th>
                  <th className="border px-3 py-2">Email</th>
                  <th className="border px-3 py-2">Role</th>
                  <th className="border px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td className="border px-3 py-2 text-center" colSpan={4}>No users found.</td></tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td className="border px-3 py-2">{user.username}</td>
                      <td className="border px-3 py-2">{user.email}</td>
                      <td className="border px-3 py-2 capitalize">{user.role}</td>
                      <td className="border px-3 py-2">
                        <button
                          onClick={() => handleDelete(user)}
                          disabled={user.id === currentUserId}
                          className={`px-2 py-1 rounded text-white ${user.id === currentUserId ? 'bg-gray-400 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700'}`}
                          title="Delete user"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
        {confirmOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div className="bg-white rounded shadow-lg p-6 w-full max-w-xs">
              <h3 className="text-lg font-bold mb-2">Delete User?</h3>
              <p className="mb-4">Are you sure you want to delete '{targetUser?.username}'?</p>
              <div className="flex justify-end space-x-2">
                <button className="px-3 py-1 rounded bg-gray-200 text-gray-800" onClick={() => setConfirmOpen(false)}>Cancel</button>
                <button className="px-3 py-1 rounded bg-red-600 text-white" onClick={confirmDelete}>Delete</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
