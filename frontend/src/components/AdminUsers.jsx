import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
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
    <Box sx={{ mt: 2, width: '100%', maxWidth: 800 }}>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" mb={2}>All Users</Typography>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {!loading && !error && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Full Name</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.length === 0 ? (
                  <TableRow><TableCell colSpan={6}>No users found.</TableCell></TableRow>
                ) : (
                  users.map((user, i) => (
                    <TableRow key={i}>
                      <TableCell>{user.id}</TableCell>
                      <TableCell>{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.full_name}</TableCell>
                      <TableCell>{user.role}</TableCell>
                      <TableCell>
                        <IconButton
                          aria-label={`Delete user ${user.username}`}
                          color="error"
                          disabled={user.id === currentUserId}
                          onClick={() => handleDelete(user)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <ConfirmDialog
          open={confirmOpen}
          title="Confirm Delete"
          content={targetUser ? `Are you sure you want to delete user '${targetUser.username}'?` : ''}
          onClose={() => setConfirmOpen(false)}
          onConfirm={confirmDelete}
        />
      </Paper>
    </Box>
  );
}
