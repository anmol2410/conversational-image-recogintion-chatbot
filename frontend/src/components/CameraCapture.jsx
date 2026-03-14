import { useState, useRef, useEffect } from "react";

/**
 * Camera capture: getUserMedia stream, capture frame, return as File for upload.
 * Props: onCapture(file), onClose()
 */
export default function CameraCapture({ onCapture, onClose }) {
  const [stream, setStream] = useState(null);
  const [error, setError] = useState("");
  const [capturing, setCapturing] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    let s = null;
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then((mediaStream) => {
        s = mediaStream;
        setStream(s);
        if (videoRef.current) videoRef.current.srcObject = s;
      })
      .catch((err) => {
        setError("Could not access camera: " + (err.message || "Permission denied"));
      });
    return () => {
      if (s) s.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    if (!stream || !videoRef.current) return;
    videoRef.current.srcObject = stream;
  }, [stream]);

  const capture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !stream) return;
    setCapturing(true);
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => {
        const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
        onCapture(file);
        setCapturing(false);
      },
      "image/jpeg",
      0.92
    );
  };

  return (
    <div className="camera-capture-overlay">
      <div className="camera-capture-box">
        <div className="camera-capture-header">
          <h3>Capture from camera</h3>
          <button type="button" className="camera-close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        {error ? (
          <p className="camera-error">{error}</p>
        ) : (
          <>
            <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
            <canvas ref={canvasRef} style={{ display: "none" }} />
            <div className="camera-actions">
              <button type="button" className="camera-capture-btn" onClick={capture} disabled={capturing || !stream}>
                {capturing ? "Capturing…" : "📷 Capture photo"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
