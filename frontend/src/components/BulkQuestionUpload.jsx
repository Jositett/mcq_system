import React, { useRef, useState } from 'react';
import { Box, Button, Typography, Paper, Alert, CircularProgress, Link } from '@mui/material';
import Papa from 'papaparse';
import { api } from '../api';
import { useToast } from './ToastContext';

export default function BulkQuestionUpload({ token }) {
  const fileInput = useRef();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState([]);
  const showToast = useToast();

  const handleFile = (e) => {
    setError('');
    setPreview([]);
    const file = e.target.files[0];
    if (!file) return;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.errors.length) {
          setError('CSV parse error: ' + results.errors[0].message);
        } else {
          setPreview(results.data);
        }
      }
    });
  };

  const handleUpload = async () => {
    if (!preview.length) return;
    setUploading(true);
    setError('');
    try {
      await api.post('/tests/questions/bulk', preview, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showToast('Bulk question upload successful!', 'success');
      setPreview([]);
      fileInput.current.value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Bulk upload failed');
      showToast('Bulk upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ mt: 2, maxWidth: 600 }}>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" mb={1}>Bulk Add Questions to Tests</Typography>
        <Typography variant="body2" mb={2}>
          Download the <Link href="/bulk_questions_template.csv" target="_blank" rel="noopener">CSV template</Link> and fill in question details. Then upload the completed file below.<br/>
          <b>Question Types:</b> mcq, true_false, short_answer
        </Typography>
        <input type="file" accept=".csv" ref={fileInput} onChange={handleFile} style={{ display: 'none' }} />
        <Button variant="contained" onClick={() => fileInput.current.click()} disabled={uploading} sx={{ mr: 2 }}>Choose CSV</Button>
        <Button variant="contained" color="success" onClick={handleUpload} disabled={!preview.length || uploading}>Upload</Button>
        {uploading && <CircularProgress size={24} sx={{ ml: 2 }} />}
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {preview.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2">Preview ({preview.length} questions):</Typography>
            <ul style={{ maxHeight: 120, overflowY: 'auto' }}>
              {preview.map((row, idx) => (
                <li key={idx}>{row.test_name} - {row.question_text} ({row.question_type})</li>
              ))}
            </ul>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
