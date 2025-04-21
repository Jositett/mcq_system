import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert, List, ListItem, ListItemText, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
import ConfirmDialog from './ConfirmDialog';
import { useToast } from './ToastContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function InstructorBatches({ token, user }) {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [targetBatch, setTargetBatch] = useState(null);
  const showToast = useToast();

  const fetchBatches = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/instructors/${user.id}/batches`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBatches(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch batches');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (user?.id && token) fetchBatches(); }, [token, user]);

  const handleDelete = (batch) => {
    setTargetBatch(batch);
    setConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!targetBatch) return;
    try {
      await axios.delete(`${API_URL}/batches/${targetBatch.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showToast(`Batch '${targetBatch.name || targetBatch.id}' deleted.`, 'success');
      fetchBatches();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to delete batch', 'error');
    } finally {
      setConfirmOpen(false);
      setTargetBatch(null);
    }
  };

  return (
    <Box sx={{ mt: 2, width: '100%', maxWidth: 600 }}>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" mb={2}>My Batches</Typography>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {!loading && !error && (
          <List>
            {batches.length === 0 ? (
              <ListItem><ListItemText primary="No batches found." /></ListItem>
            ) : (
              batches.map((batch, i) => (
                <ListItem key={i}
                  secondaryAction={
                    <IconButton
                      aria-label={`Delete batch ${batch.name || batch.id}`}
                      color="error"
                      onClick={() => handleDelete(batch)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText primary={batch.name || `Batch #${batch.id}`} secondary={`ID: ${batch.id}`} />
                </ListItem>
              ))
            )}
          </List>
        )}
        <ConfirmDialog
          open={confirmOpen}
          title="Confirm Delete"
          content={targetBatch ? `Are you sure you want to delete batch '${targetBatch.name || targetBatch.id}'?` : ''}
          onClose={() => setConfirmOpen(false)}
          onConfirm={confirmDelete}
        />
      </Paper>
    </Box>
  );
}
