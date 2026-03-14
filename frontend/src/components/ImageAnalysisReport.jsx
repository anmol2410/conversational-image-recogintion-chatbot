/**
 * Image Analysis Report panel: objects, scene, relationships, text, safety.
 */
export default function ImageAnalysisReport({
  objects = [],
  caption = "",
  ocrText = "",
  relationships = [],
  safetyWarnings = [],
  isOpen,
  onToggle,
}) {
  const hasContent = objects.length > 0 || caption || ocrText || relationships.length > 0 || safetyWarnings.length > 0;

  return (
    <div className="analysis-report-panel">
      <button
        type="button"
        className="analysis-report-toggle"
        onClick={onToggle}
        aria-expanded={isOpen}
      >
        <span>📋 Image Analysis Report</span>
        <span className="toggle-icon">{isOpen ? "▼" : "▶"}</span>
      </button>
      {isOpen && (
        <div className="analysis-report-content">
          {!hasContent && (
            <p className="report-empty">Ask a question about the image to generate the report.</p>
          )}
          {caption && (
            <section className="report-section">
              <h4>Scene description</h4>
              <p>{caption}</p>
            </section>
          )}
          {objects.length > 0 && (
            <section className="report-section">
              <h4>Objects detected</h4>
              <ul className="report-list">
                {objects.map((o, i) => (
                  <li key={i}>
                    {o.name} — {(o.confidence * 100).toFixed(0)}% ({o.color}, {o.position}
                    {o.size ? `, ${o.size}` : ""})
                  </li>
                ))}
              </ul>
            </section>
          )}
          {relationships.length > 0 && (
            <section className="report-section">
              <h4>Relationships</h4>
              <ul className="report-list">
                {relationships.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </section>
          )}
          {ocrText && (
            <section className="report-section">
              <h4>Text in image</h4>
              <p className="report-ocr">"{ocrText}"</p>
            </section>
          )}
          {safetyWarnings.length > 0 && (
            <section className="report-section report-safety">
              <h4>⚠️ Safety</h4>
              <ul className="report-list">
                {safetyWarnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
