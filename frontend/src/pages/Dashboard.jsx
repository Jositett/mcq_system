import React from 'react';
import { Typography, Paper, Box } from '@mui/material';
import FaceUpload from '../components/FaceUpload';
import AttendanceCheckin from '../components/AttendanceCheckin';
import AttendanceHistory from '../components/AttendanceHistory';

export default function Dashboard({ user }) {
  const token = localStorage.getItem('access_token');
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
      <Paper sx={{ p: 4, minWidth: 320, mb: 3 }}>
        <Typography variant="h5" mb={2}>Welcome, {user?.full_name || user?.username || 'User'}!</Typography>
        <Typography variant="body1">Role: {user?.role}</Typography>
      </Paper>
      {user?.role === 'student' && <>
        <FaceUpload token={token} />
        <AttendanceCheckin token={token} />
        <AttendanceHistory token={token} user={user} />
      </>}
      {/* Instructor/Admin widgets will go here in the future */}
    </Box>
  );
}
