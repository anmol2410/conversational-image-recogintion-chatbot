/**
 * Draws bounding boxes on top of the image using a canvas overlay.
 * Props: imageUrl (or image element), objects [{ bbox: [x1,y1,x2,y2], name, color?, confidence }], width, height
 */
import { useRef, useEffect } from "react";

const BOX_COLORS = [
  "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
  "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
];

export default function BoundingBoxOverlay({ imageUrl, objects = [], imageWidth, imageHeight }) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    const rect = container.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;

    // When no image or no objects, clear the canvas so previous boxes don't stay
    if (!imageUrl || !objects.length) {
      canvas.width = w;
      canvas.height = h;
      ctx.clearRect(0, 0, w, h);
      return;
    }

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const r = container.getBoundingClientRect();
      const scaleX = r.width / (imageWidth || img.naturalWidth);
      const scaleY = r.height / (imageHeight || img.naturalHeight);

      canvas.width = r.width;
      canvas.height = r.height;
      const c = canvas.getContext("2d");
      c.clearRect(0, 0, r.width, r.height);

      objects.forEach((obj, i) => {
        const bbox = obj.bbox;
        if (!bbox || bbox.length < 4) return;
        const [x1, y1, x2, y2] = bbox;
        const sx1 = x1 * scaleX;
        const sy1 = y1 * scaleY;
        const sx2 = x2 * scaleX;
        const sy2 = y2 * scaleY;
        const color = BOX_COLORS[i % BOX_COLORS.length];
        c.strokeStyle = color;
        c.lineWidth = 2;
        c.strokeRect(sx1, sy1, sx2 - sx1, sy2 - sy1);
        const label = `${obj.name} ${(obj.confidence * 100).toFixed(0)}%`;
        c.font = "12px sans-serif";
        const tw = c.measureText(label).width;
        c.fillStyle = color;
        c.fillRect(sx1, sy1 - 18, tw + 8, 18);
        c.fillStyle = "#fff";
        c.fillText(label, sx1 + 4, sy1 - 5);
      });
    };
    img.src = imageUrl;
  }, [imageUrl, objects, imageWidth, imageHeight]);

  if (!imageUrl) return null;

  return (
    <div ref={containerRef} className="bbox-overlay-container">
      <img src={imageUrl} alt="Preview" className="bbox-base-image" />
      <canvas ref={canvasRef} className="bbox-canvas" />
    </div>
  );
}
