import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import InstructorBulkStudentUpload from '../components/InstructorBulkStudentUpload';

export default function InstructorBulkActions({ token, user }) {
  return (
    <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Paper sx={{ p: 4, minWidth: 320, mb: 3 }}>
        <Typography variant="h5" mb={2}>Bulk Actions</Typography>
        <Typography variant="body2" mb={2}>
          Use the form below to upload students to your batches in bulk. Download the provided template to prepare your data.
        </Typography>
        <InstructorBulkStudentUpload token={token} instructorId={user.id} />
      </Paper>
    </Box>
  );
}
