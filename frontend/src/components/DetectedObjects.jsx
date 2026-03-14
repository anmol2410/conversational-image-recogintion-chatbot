export default function DetectedObjects({ objects = [] }) {
  const counts = {};
  objects.forEach((o) => {
    counts[o.name] = (counts[o.name] || 0) + 1;
  });
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);

  return (
    <div className="detected-objects">
      <h4>Detected Objects</h4>
      {entries.length === 0 ? (
        <p className="empty-state">No objects detected yet. Ask a question about the image.</p>
      ) : (
        <ul className="object-list">
          {entries.map(([name, count]) => {
            const sample = objects.find((o) => o.name === name);
            const conf = sample ? (sample.confidence * 100).toFixed(0) : "—";
            return (
              <li key={name} className="object-item">
                <span className="obj-name">{name}</span>
                <span className="obj-count">({count})</span>
                <span className="obj-conf">{conf}%</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
