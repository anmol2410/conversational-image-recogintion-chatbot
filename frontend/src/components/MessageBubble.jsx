export default function MessageBubble({ type, text, timestamp, isLoading }) {
  const isUser = type === "user";
  const isError = type === "error";
  const isInfo = type === "info";

  return (
    <div className={`message-bubble message-${type}`}>
      {!isUser && (
        <div className="message-avatar ai">
          <span>🤖</span>
        </div>
      )}
      <div className="message-body">
        <div className={`message-content ${isError ? "error" : ""} ${isInfo ? "info" : ""}`}>
          {isLoading ? (
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          ) : (
            text
          )}
        </div>
        {timestamp && !isLoading && (
          <div className="message-time">
            {timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </div>
        )}
      </div>
      {isUser && (
        <div className="message-avatar user">
          <span>👤</span>
        </div>
      )}
    </div>
  );
}
