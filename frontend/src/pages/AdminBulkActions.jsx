import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import BulkStudentUpload from '../components/BulkStudentUpload';
import BulkQuestionUpload from '../components/BulkQuestionUpload';

export default function AdminBulkActions({ token }) {
  return (
    <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Paper sx={{ p: 4, minWidth: 320, mb: 3 }}>
        <Typography variant="h5" mb={2}>Bulk Actions</Typography>
        <Typography variant="body2" mb={2}>
          Use the forms below to upload students to batches or add questions to tests in bulk. Download the provided templates to prepare your data.
        </Typography>
        <BulkStudentUpload token={token} />
        <BulkQuestionUpload token={token} />
      </Paper>
    </Box>
  );
}
