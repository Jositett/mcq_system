import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, CircularProgress, Alert, Grid } from '@mui/material';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function AdminStats({ token }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchStats() {
      setError('');
      setLoading(true);
      try {
        // Simulate stats: count users by role (since no dedicated endpoint)
        const res = await axios.get(`${API_URL}/users/`, { headers: { Authorization: `Bearer ${token}` } });
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
    <Box sx={{ mt: 2, width: '100%', maxWidth: 600 }}>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" mb={2}>User Summary</Typography>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {stats && !loading && !error && (
          <Grid container spacing={2}>
            <Grid item xs={6}><Typography>Total Users:</Typography></Grid>
            <Grid item xs={6}><Typography>{stats.total}</Typography></Grid>
            <Grid item xs={6}><Typography>Students:</Typography></Grid>
            <Grid item xs={6}><Typography>{stats.students}</Typography></Grid>
            <Grid item xs={6}><Typography>Instructors:</Typography></Grid>
            <Grid item xs={6}><Typography>{stats.instructors}</Typography></Grid>
            <Grid item xs={6}><Typography>Admins:</Typography></Grid>
            <Grid item xs={6}><Typography>{stats.admins}</Typography></Grid>
          </Grid>
        )}
      </Paper>
    </Box>
  );
}
