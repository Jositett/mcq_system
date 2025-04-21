import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert, List, ListItem, ListItemText, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
import ConfirmDialog from './ConfirmDialog';
import { useToast } from './ToastContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function InstructorTests({ token, user }) {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [targetTest, setTargetTest] = useState(null);
  const showToast = useToast();

  const fetchTests = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/instructors/${user.id}/tests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTests(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch tests');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (user?.id && token) fetchTests(); }, [token, user]);

  const handleDelete = (test) => {
    setTargetTest(test);
    setConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!targetTest) return;
    try {
      await axios.delete(`${API_URL}/tests/${targetTest.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showToast(`Test '${targetTest.title || targetTest.id}' deleted.`, 'success');
      fetchTests();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to delete test', 'error');
    } finally {
      setConfirmOpen(false);
      setTargetTest(null);
    }
  };

  return (
    <Box sx={{ mt: 2, width: '100%', maxWidth: 600 }}>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" mb={2}>My Tests</Typography>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {!loading && !error && (
          <List>
            {tests.length === 0 ? (
              <ListItem><ListItemText primary="No tests found." /></ListItem>
            ) : (
              tests.map((test, i) => (
                <ListItem key={i}
                  secondaryAction={
                    <IconButton
                      aria-label={`Delete test ${test.title || test.id}`}
                      color="error"
                      onClick={() => handleDelete(test)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText primary={test.title || `Test #${test.id}`} secondary={`ID: ${test.id}`} />
                </ListItem>
              ))
            )}
          </List>
        )}
        <ConfirmDialog
          open={confirmOpen}
          title="Confirm Delete"
          content={targetTest ? `Are you sure you want to delete test '${targetTest.title || targetTest.id}'?` : ''}
          onClose={() => setConfirmOpen(false)}
          onConfirm={confirmDelete}
        />
      </Paper>
    </Box>
  );
}
