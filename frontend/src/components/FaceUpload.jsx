import React, { useRef, useState } from 'react';
import { Box, Button, Typography, Paper, Alert, CircularProgress } from '@mui/material';
import * as faceapi from 'face-api.js';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function FaceUpload({ token, onSuccess }) {
  const fileInput = useRef();
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function loadModels() {
    await faceapi.nets.ssdMobilenetv1.loadFromUri('/models');
    await faceapi.nets.faceRecognitionNet.loadFromUri('/models');
    await faceapi.nets.faceLandmark68Net.loadFromUri('/models');
  }

  async function extractEmbedding(img) {
    const detection = await faceapi.detectSingleFace(img).withFaceLandmarks().withFaceDescriptor();
    if (!detection) throw new Error('No face detected');
    return Array.from(detection.descriptor).join(',');
  }

  async function handleFileChange(e) {
    setError(''); setStatus(''); setLoading(true);
    const file = e.target.files[0];
    if (!file) return setLoading(false);
    try {
      await loadModels();
      const img = await faceapi.bufferToImage(file);
      const embedding = await extractEmbedding(img);
      // Send embedding to backend
      await axios.post(`${API_URL}/face/upload`, {
        embedding,
        created_at: new Date().toISOString().slice(0,10)
      }, { headers: { Authorization: `Bearer ${token}` } });
      setStatus('Face embedding uploaded successfully!');
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to process image');
    } finally {
      setLoading(false);
      fileInput.current.value = '';
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 2 }}>
      <Paper sx={{ p: 3, mb: 2, minWidth: 320 }}>
        <Typography variant="h6" mb={2}>Upload Face Image</Typography>
        {status && <Alert severity="success">{status}</Alert>}
        {error && <Alert severity="error">{error}</Alert>}
        <Button variant="contained" component="label" disabled={loading}>
          Select Image
          <input type="file" accept="image/*" hidden ref={fileInput} onChange={handleFileChange} />
        </Button>
        {loading && <CircularProgress size={24} sx={{ ml: 2 }} />}
        <Typography variant="body2" mt={2} color="text.secondary">
          Only one face per image. Embedding is extracted client-side for privacy.
        </Typography>
      </Paper>
    </Box>
  );
}
