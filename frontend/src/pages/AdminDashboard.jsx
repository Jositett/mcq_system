import React from 'react';
import { Typography, Paper, Box } from '@mui/material';
import AdminUsers from '../components/AdminUsers';
import AdminStats from '../components/AdminStats';
import AdminBulkActions from './AdminBulkActions';
import { Button, Tabs, Tab } from '@mui/material';

export default function AdminDashboard({ user }) {
  const token = localStorage.getItem('access_token');
  const [tab, setTab] = React.useState(0);
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
      <Paper sx={{ p: 4, minWidth: 320, mb: 3 }}>
        <Typography variant="h5" mb={2}>Welcome, {user?.full_name || user?.username || 'Admin'}!</Typography>
        <Typography variant="body1">Role: {user?.role}</Typography>
      </Paper>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Users" />
        <Tab label="Bulk Actions" />
      </Tabs>
      {tab === 0 && <><AdminStats token={token} /><AdminUsers token={token} /></>}
      {tab === 1 && <AdminBulkActions token={token} />}
    </Box>
  );
}
