import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Alert, MenuItem } from '@mui/material';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function Register({ onRegister }) {
  const [form, setForm] = useState({ username: '', email: '', full_name: '', role: 'student', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    try {
      await axios.post(`${API_URL}/auth/register`, form);
      setSuccess('Registration successful! Please log in.');
      if (onRegister) onRegister();
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <Paper sx={{ p: 4, minWidth: 320 }}>
        <Typography variant="h5" mb={2}>Register</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField label="Username" name="username" value={form.username} onChange={handleChange} fullWidth margin="normal" required />
          <TextField label="Email" name="email" type="email" value={form.email} onChange={handleChange} fullWidth margin="normal" required />
          <TextField label="Full Name" name="full_name" value={form.full_name} onChange={handleChange} fullWidth margin="normal" required />
          <TextField select label="Role" name="role" value={form.role} onChange={handleChange} fullWidth margin="normal" required>
            <MenuItem value="student">Student</MenuItem>
            <MenuItem value="instructor">Instructor</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
          </TextField>
          <TextField label="Password" name="password" type="password" value={form.password} onChange={handleChange} fullWidth margin="normal" required />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Register
          </Button>
        </form>
      </Paper>
    </Box>
  );
}
