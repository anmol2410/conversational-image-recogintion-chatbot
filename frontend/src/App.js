import { useState } from "react";
import axios from "axios";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import ImagePreview from "./components/ImagePreview";
import DetectedObjects from "./components/DetectedObjects";
import CameraCapture from "./components/CameraCapture";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function AppContent() {
  const { theme } = useTheme();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [detectedObjects, setDetectedObjects] = useState([]);
  const [caption, setCaption] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [relationships, setRelationships] = useState([]);
  const [safetyWarnings, setSafetyWarnings] = useState([]);
  const [showCamera, setShowCamera] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });

  const processImage = (file) => {
    if (!file || !file.type.startsWith("image/")) {
      setError("Please upload a valid image file");
      return;
    }
    if (preview) URL.revokeObjectURL(preview);
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setError("");
    setDetectedObjects([]);
    setCaption("");
    setOcrText("");
    setRelationships([]);
    setSafetyWarnings([]);
    setMessages((prev) => [...prev, { type: "info", text: `Image: ${file.name}`, timestamp: new Date() }]);
    const img = new Image();
    img.onload = () => setImageDimensions({ width: img.naturalWidth, height: img.naturalHeight });
    img.src = URL.createObjectURL(file);
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) processImage(file);
  };

  const handleCameraCapture = (file) => {
    processImage(file);
    setShowCamera(false);
  };

  const handleNewChat = () => {
    setImage(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    setMessages([]);
    setQuestion("");
    setSessionId(null);
    setDetectedObjects([]);
    setCaption("");
    setOcrText("");
    setRelationships([]);
    setSafetyWarnings([]);
    setError("");
  };

  const handleClearChat = () => {
    setMessages([]);
    setSessionId(null);
    setDetectedObjects([]);
    setCaption("");
    setOcrText("");
    setRelationships([]);
    setSafetyWarnings([]);
  };

  const handleSubmitQuestion = (questionToSend) => {
    if (!image || !questionToSend.trim()) return;

    setMessages((prev) => [...prev, { type: "user", text: questionToSend, timestamp: new Date() }]);
    setQuestion("");
    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", image);
    formData.append("question", questionToSend);
    if (sessionId) formData.append("session_id", sessionId);

    axios
      .post(`${API_URL}/analyze/`, formData)
      .then((response) => {
        if (response.data.session_id) setSessionId(response.data.session_id);
        if (response.data.detected_objects) setDetectedObjects(response.data.detected_objects);
        if (response.data.caption !== undefined) setCaption(response.data.caption);
        if (response.data.ocr_text !== undefined) setOcrText(response.data.ocr_text);
        if (Array.isArray(response.data.relationships)) setRelationships(response.data.relationships);
        if (Array.isArray(response.data.safety_warnings)) setSafetyWarnings(response.data.safety_warnings);
        setMessages((prev) => [
          ...prev,
          { type: "bot", text: response.data.answer || "No answer.", timestamp: new Date() },
        ]);
      })
      .catch((err) => {
        const isNetworkError =
          err.code === "ERR_NETWORK" ||
          err.message === "Network Error" ||
          (err.response === undefined && err.request !== undefined);
        const msg = isNetworkError
          ? "Backend not running. Start it with: uvicorn main:app --reload"
          : err.response?.data?.detail || err.message || "Request failed";
        setError(isNetworkError ? "Backend not reachable" : "Error analyzing image.");
        setMessages((prev) => [...prev, { type: "error", text: String(msg), timestamp: new Date() }]);
      })
      .finally(() => setLoading(false));
  };

  const downloadReport = () => {
    if (!detectedObjects.length && !caption && !ocrText && messages.length === 0) return;
    const lines = [
      "AI Visual Understanding Assistant — Report",
      "---------------------------------------------",
      caption ? `Scene: ${caption}` : "",
      relationships.length ? "Relationships:\n  " + relationships.join("\n  ") : "",
      ocrText ? `Text: ${ocrText}` : "",
      safetyWarnings.length ? "Safety: " + safetyWarnings.join(" ") : "",
      "Objects:",
      ...detectedObjects.map((o) => `  - ${o.name}: ${(o.confidence * 100).toFixed(0)}% (${o.color}, ${o.position})`),
      "",
      "Conversation:",
      ...messages.map((m) => `[${m.type}] ${m.text}`),
    ];
    const blob = new Blob([lines.filter(Boolean).join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "analysis-report.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processImage(file);
  };

  return (
    <div className={`app-root theme-${theme}`}>
      <Sidebar
        onNewChat={handleNewChat}
        onClearChat={handleClearChat}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((c) => !c)}
      />

      <div className="main-area">
        <header className="main-header">
          <h1>Conversational Image Recognition</h1>
        </header>

        <div className="content-grid">
          <section className="center-panel">
            <ChatWindow
              messages={messages}
              loading={loading}
              preview={preview}
              onUploadClick={handleImageChange}
            />
            {error && <div className="error-banner">{error}</div>}
            <ChatInput
              question={question}
              onQuestionChange={setQuestion}
              onSubmit={handleSubmitQuestion}
              loading={loading}
              hasImage={!!image}
              onUploadClick={handleImageChange}
              onCameraClick={() => setShowCamera(true)}
            />
          </section>

          <aside className="right-panel">
            <div className="right-panel-inner">
              <ImagePreview
                preview={preview}
                detectedObjects={detectedObjects}
                imageDimensions={imageDimensions}
                onImageChange={handleImageChange}
                onDrop={handleDrop}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDragEnter={handleDrag}
                dragActive={dragActive}
              />
              <DetectedObjects objects={detectedObjects} />
              {(caption || relationships.length || ocrText) && (
                <div className="analysis-summary">
                  <h4>AI Summary</h4>
                  {caption && <p>{caption}</p>}
                  {relationships.length > 0 && (
                    <p className="relations">Relations: {relationships.slice(0, 3).join("; ")}</p>
                  )}
                  {ocrText && <p className="ocr">Text: "{ocrText}"</p>}
                </div>
              )}
              {(detectedObjects.length > 0 || messages.length > 0) && (
                <button type="button" className="download-report-btn" onClick={downloadReport}>
                  📄 Download Report
                </button>
              )}
            </div>
          </aside>
        </div>
      </div>

      {showCamera && (
        <CameraCapture onCapture={handleCameraCapture} onClose={() => setShowCamera(false)} />
      )}
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
