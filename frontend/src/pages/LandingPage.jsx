import React from 'react';
import { Typography, Box } from '@mui/material';

export default function LandingPage() {
  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h3" gutterBottom>
        Welcome to the MCQ System
      </Typography>
      <Typography variant="h6" color="text.secondary">
        Please login or register to continue.
      </Typography>
    </Box>
  );
}
