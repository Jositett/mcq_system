import React from 'react';
import { Typography, Paper, Box, Tabs, Tab } from '@mui/material';
import InstructorBatches from '../components/InstructorBatches';
import InstructorTests from '../components/InstructorTests';
import InstructorBulkActions from './InstructorBulkActions';

export default function InstructorDashboard({ user }) {
  const token = localStorage.getItem('access_token');
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
      <Paper sx={{ p: 4, minWidth: 320, mb: 3 }}>
        <Typography variant="h5" mb={2}>Welcome, {user?.full_name || user?.username || 'Instructor'}!</Typography>
        <Typography variant="body1">Role: {user?.role}</Typography>
      </Paper>
      <InstructorBatches token={token} user={user} />
      <InstructorTests token={token} user={user} />
      {/* Add instructor's tests and other features here */}
    </Box>
  );
}
