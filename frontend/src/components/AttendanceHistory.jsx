import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function AttendanceHistory({ token, user }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchHistory() {
      setError('');
      setLoading(true);
      try {
        const res = await axios.get(`${API_URL}/attendance/history/${user.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setHistory(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch attendance history');
      } finally {
        setLoading(false);
      }
    }
    if (user?.id && token) fetchHistory();
  }, [token, user]);

  return (
    <Box sx={{ mt: 2, width: '100%', maxWidth: 600 }}>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" mb={2}>Attendance History</Typography>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {!loading && !error && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {history.length === 0 ? (
                  <TableRow><TableCell colSpan={2}>No records found.</TableCell></TableRow>
                ) : (
                  history.map((row, i) => (
                    <TableRow key={i}>
                      <TableCell>{row.date || row.created_at}</TableCell>
                      <TableCell>{row.status}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
}
