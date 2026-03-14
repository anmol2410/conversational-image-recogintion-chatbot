import { useRef } from "react";
import VoiceInputButton from "./VoiceInputButton";

export default function ChatInput({
  question,
  onQuestionChange,
  onSubmit,
  loading,
  hasImage,
  onUploadClick,
  onCameraClick,
}) {
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    onSubmit(q);
  };

  return (
    <div className="chat-input-wrap">
      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <div className="input-actions">
          <label className="input-action-btn" title="Upload image">
            📎 Upload
            <input type="file" accept="image/*" onChange={onUploadClick} hidden />
          </label>
          <button type="button" className="input-action-btn" onClick={onCameraClick} title="Camera">
            📷 Camera
          </button>
        </div>
        <div className="input-field-wrap">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder={hasImage ? "Ask about the image..." : "Upload an image first"}
            value={question}
            onChange={(e) => onQuestionChange(e.target.value)}
            disabled={loading || !hasImage}
          />
          <VoiceInputButton onTranscript={onQuestionChange} disabled={loading} />
          <button
            type="submit"
            className="send-btn"
            disabled={loading || !question.trim() || !hasImage}
            title="Send"
          >
            {loading ? "⏳" : "➤"}
          </button>
        </div>
      </form>
    </div>
  );
}
