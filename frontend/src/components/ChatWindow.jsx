import { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages, loading, preview, onUploadClick }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <main className="chat-window">
      <div className="chat-messages">
        {messages.length === 0 && !preview && (
          <div className="chat-welcome">
            <div className="welcome-icon">👁</div>
            <h2>Visual AI Assistant</h2>
            <p>Upload or capture an image, then ask anything about it.</p>
            <p className="welcome-hint">Try: "What do you see?" or "How many people are there?"</p>
            <label className="welcome-upload-cta">
              <span>📷</span> Upload image to start
              <input type="file" accept="image/*" onChange={(e) => onUploadClick?.(e)} hidden />
            </label>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble
            key={idx}
            type={msg.type}
            text={msg.text}
            timestamp={msg.timestamp}
            isLoading={false}
          />
        ))}

        {loading && (
          <MessageBubble type="bot" text="" timestamp={null} isLoading />
        )}

        <div ref={endRef} />
      </div>
    </main>
  );
}
