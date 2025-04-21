import React, { useRef, useState, useEffect } from "react";
import Human from "human";

/**
 * FaceCapture component
 * Allows user to capture a photo from their webcam for facial recognition training.
 * Usage: <FaceCapture onCapture={handleCapture} />
 * onCapture receives a base64 image string.
 */
export default function FaceCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const [captured, setCaptured] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [faceBox, setFaceBox] = useState(null);

  const human = useRef(new Human()).current;

  useEffect(() => {
    let raf;
    async function detectFace() {
      if (videoRef.current && streaming) {
        setDetecting(true);
        const result = await human.detect(videoRef.current);
        if (result.face && result.face.length > 0) {
          const box = result.face[0].box;
          setFaceBox(box);
        } else {
          setFaceBox(null);
        }
        setDetecting(false);
        raf = requestAnimationFrame(detectFace);
      }
    }
    if (streaming) detectFace();
    return () => raf && cancelAnimationFrame(raf);
  }, [streaming, human]);

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
    setFaceBox(null);
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    let dataUrl = canvas.toDataURL("image/png");
    // Optionally crop to face box
    if (faceBox) {
      const ctx = canvas.getContext("2d");
      const { left, top, width, height } = faceBox;
      const faceImg = ctx.getImageData(left, top, width, height);
      const faceCanvas = document.createElement('canvas');
      faceCanvas.width = width;
      faceCanvas.height = height;
      faceCanvas.getContext('2d').putImageData(faceImg, 0, 0);
      dataUrl = faceCanvas.toDataURL("image/png");
    }
    setCaptured(dataUrl);
    stopCamera();
    if (onCapture) onCapture(dataUrl);
  };

  return (
    <div className="text-center">
      <h3 className="text-lg font-semibold mb-2">Facial Recognition Check-In</h3>
      {!streaming && !captured && (
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" onClick={startCamera}>Start Camera</button>
      )}
      {streaming && (
        <div className="relative inline-block">
          <video ref={videoRef} autoPlay width={320} height={240} className="rounded" />
          {/* Face box overlay */}
          {faceBox && (
            <div
              className="absolute border-2 border-green-500"
              style={{
                left: faceBox.left,
                top: faceBox.top,
                width: faceBox.width,
                height: faceBox.height,
                pointerEvents: 'none',
              }}
            />
          )}
          <br />
          <button className="bg-green-600 text-white px-3 py-1 rounded mr-2 mt-2" onClick={capturePhoto} disabled={!faceBox || detecting}>
            {detecting ? 'Detecting...' : 'Capture Photo'}
          </button>
          <button className="bg-gray-400 text-white px-3 py-1 rounded mt-2" onClick={stopCamera}>Cancel</button>
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
