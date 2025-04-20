import React, { useRef, useState } from "react";

/**
 * FaceCapture component
 * Allows user to capture a photo from their webcam for facial recognition training.
 * Usage: <FaceCapture onCapture={handleCapture} />
 * onCapture receives a base64 image string.
 */
export default function FaceCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const [captured, setCaptured] = useState(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      setStreaming(true);
    } catch (err) {
      alert("Could not access camera: " + err.message);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    }
    setStreaming(false);
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL("image/png");
    setCaptured(dataUrl);
    stopCamera();
    if (onCapture) onCapture(dataUrl);
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h3>Facial Recognition Check-In</h3>
      {!streaming && !captured && (
        <button onClick={startCamera}>Start Camera</button>
      )}
      {streaming && (
        <div>
          <video ref={videoRef} autoPlay style={{ width: 320, height: 240, borderRadius: 8 }} />
          <br />
          <button onClick={capturePhoto}>Capture Photo</button>
          <button onClick={stopCamera} style={{ marginLeft: 8 }}>Cancel</button>
        </div>
      )}
      <canvas ref={canvasRef} style={{ display: "none" }} />
      {captured && (
        <div>
          <h4>Captured Image:</h4>
          <img src={captured} alt="Face capture" style={{ width: 160, borderRadius: 8 }} />
          <br />
          <button onClick={() => setCaptured(null)}>Retake</button>
        </div>
      )}
    </div>
  );
}
