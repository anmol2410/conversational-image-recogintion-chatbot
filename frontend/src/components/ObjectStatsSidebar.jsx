/**
 * Sidebar listing detected objects with counts and confidence.
 * Props: objects [{ name, confidence, color?, position? }]
 */
export default function ObjectStatsSidebar({ objects = [] }) {
  const counts = {};
  objects.forEach((o) => {
    counts[o.name] = (counts[o.name] || 0) + 1;
  });
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);

  return (
    <div className="object-stats-sidebar">
      <h3 className="object-stats-title">Detected objects</h3>
      {entries.length === 0 ? (
        <p className="object-stats-empty">No objects detected yet.</p>
      ) : (
        <ul className="object-stats-list">
          {entries.map(([name, count]) => {
            const sample = objects.find((o) => o.name === name);
            const conf = sample ? (sample.confidence * 100).toFixed(0) : "—";
            return (
              <li key={name} className="object-stats-item">
                <span className="object-name">{name}</span>
                <span className="object-count">({count})</span>
                <span className="object-conf">{conf}%</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
