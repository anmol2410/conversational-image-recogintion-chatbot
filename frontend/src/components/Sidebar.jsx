import ThemeToggle from "./ThemeToggle";

export default function Sidebar({ onNewChat, onClearChat, isCollapsed, onToggleCollapse }) {
  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <span className="sidebar-icon">🤖</span>
          {!isCollapsed && <span className="sidebar-title">AI Vision</span>}
        </div>
        <button
          type="button"
          className="sidebar-collapse-btn"
          onClick={onToggleCollapse}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? "›" : "‹"}
        </button>
      </div>

      {!isCollapsed && (
        <>
          <button type="button" className="sidebar-btn primary" onClick={onNewChat}>
            <span>+</span> New Chat
          </button>
          <button type="button" className="sidebar-btn" onClick={onClearChat}>
            Clear Chat
          </button>
        </>
      )}

      <div className="sidebar-footer">
        {!isCollapsed && (
          <p className="sidebar-subtitle">Conversational Image Recognition</p>
        )}
        <ThemeToggle />
      </div>
    </aside>
  );
}
