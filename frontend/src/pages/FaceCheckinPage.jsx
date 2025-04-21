import React, { useState } from "react";
import FaceCapture from "../components/FaceCapture";
import Human from 'human';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function FaceCheckinPage() {
  const [image, setImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const human = new Human();

  async function extractEmbedding(imgSrc) {
    const img = document.createElement('img');
    img.src = imgSrc;
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
    });
    const result = await human.detect(img);
    if (!result.face || result.face.length === 0) throw new Error('No face detected');
    return result.face[0].embedding.join(',');
  }

  const handleCapture = async (imgData) => {
    setImage(imgData);
    setUploading(true);
    setResult(null);
    try {
      const embedding = await extractEmbedding(imgData);
      const response = await axios.post(`${API_URL}/attendance/face-checkin`, {
        embedding
      });
      setResult({ success: true });
    } catch (e) {
      setResult({ error: e.response?.data?.detail || e.message || "Failed to upload/check-in." });
    }
    setUploading(false);
  };

  return (
    <div className="flex flex-col items-center mt-6">
      <div className="bg-white rounded shadow p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold mb-3">Face Recognition Check-In</h2>
        <FaceCapture onCapture={handleCapture} />
        {uploading && <div className="my-2 text-blue-700">Uploading and processing...</div>}
        {image && result && (
          <div className="mt-4">
            {result.error ? (
              <div className="p-2 bg-red-100 text-red-800 rounded">{result.error}</div>
            ) : (
              <div className="p-2 bg-green-100 text-green-800 rounded">Check-in successful!</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
