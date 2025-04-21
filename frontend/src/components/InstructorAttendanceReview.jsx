import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * InstructorAttendanceReview
 * Allows instructors to review, approve, or reject flagged/pending attendance check-ins for their own students/batches.
 * Shows face match confidence and captured image (if available from backend).
 */
export default function InstructorAttendanceReview({ token, instructorId }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionStatus, setActionStatus] = useState('');

  useEffect(() => {
    async function fetchRecords() {
      setError(''); setLoading(true);
      try {
        const res = await axios.get(`${API_URL}/attendance/review/instructor/${instructorId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setRecords(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch records');
      } finally {
        setLoading(false);
      }
    }
    if (token && instructorId) fetchRecords();
  }, [token, instructorId, actionStatus]);

  async function handleAction(id, action) {
    setActionStatus('');
    try {
      await axios.post(`${API_URL}/attendance/review/${id}`, { action }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActionStatus(`Attendance ${action}d.`);
    } catch (err) {
      setActionStatus(err.response?.data?.detail || `Failed to ${action}`);
    }
  }

  return (
    <div className="bg-white rounded shadow p-6 w-full max-w-2xl mx-auto mt-6">
      <h2 className="text-xl font-semibold mb-4">Instructor Attendance Review</h2>
      {loading && <div className="text-blue-700">Loading...</div>}
      {error && <div className="p-2 bg-red-100 text-red-800 rounded mb-2">{error}</div>}
      {actionStatus && <div className="p-2 bg-green-100 text-green-800 rounded mb-2">{actionStatus}</div>}
      {!loading && !error && records.length === 0 && (
        <div className="text-gray-500">No flagged or pending attendance records.</div>
      )}
      {!loading && !error && records.length > 0 && (
        <table className="min-w-full text-sm border">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-2 py-1">Student</th>
              <th className="border px-2 py-1">Date</th>
              <th className="border px-2 py-1">Status</th>
              <th className="border px-2 py-1">Confidence</th>
              <th className="border px-2 py-1">Image</th>
              <th className="border px-2 py-1">Action</th>
            </tr>
          </thead>
          <tbody>
            {records.map((rec) => (
              <tr key={rec.id}>
                <td className="border px-2 py-1">{rec.student_name || rec.student_id}</td>
                <td className="border px-2 py-1">{rec.date || rec.created_at}</td>
                <td className="border px-2 py-1">{rec.status}</td>
                <td className="border px-2 py-1">{rec.confidence !== undefined ? `${(rec.confidence * 100).toFixed(1)}%` : '-'}</td>
                <td className="border px-2 py-1">
                  {rec.image_url ? <img src={rec.image_url} alt="face" className="w-12 h-12 object-cover rounded" /> : '-'}</td>
                <td className="border px-2 py-1 space-x-2">
                  <button className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded" onClick={() => handleAction(rec.id, 'approve')}>Approve</button>
                  <button className="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded" onClick={() => handleAction(rec.id, 'reject')}>Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
