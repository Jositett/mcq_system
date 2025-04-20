import React, { useState } from "react";
import FaceCapture from "../components/FaceCapture";

export default function FaceCheckinPage() {
  const [image, setImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCapture = async (imgData) => {
    setImage(imgData);
    setUploading(true);
    setResult(null);
    // Example: send to backend for training/check-in
    try {
      const response = await fetch("/api/attendance/face-checkin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imgData }),
      });
      const data = await response.json();
      setResult(data);
    } catch (e) {
      setResult({ error: "Failed to upload/check-in." });
    }
    setUploading(false);
  };

  return (
    <div style={{ maxWidth: 420, margin: "2rem auto", padding: 16, border: "1px solid #eee", borderRadius: 12 }}>
      <h2>Face Recognition Check-In</h2>
      <FaceCapture onCapture={handleCapture} />
      {uploading && <p>Uploading and processing...</p>}
      {image && result && (
        <div style={{ marginTop: 16 }}>
          {result.error ? (
            <span style={{ color: "red" }}>{result.error}</span>
          ) : (
            <span style={{ color: "green" }}>Check-in successful!</span>
          )}
        </div>
      )}
    </div>
  );
}
