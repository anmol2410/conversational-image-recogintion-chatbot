import { useState } from "react";
import BoundingBoxOverlay from "./BoundingBoxOverlay";

export default function ImagePreview({
  preview,
  detectedObjects,
  imageDimensions,
  onImageChange,
  onDrop,
  onDragOver,
  onDragLeave,
  onDragEnter,
  dragActive,
}) {
  const [zoom, setZoom] = useState(false);

  if (!preview) {
    return (
      <div
        className={`image-preview-upload ${dragActive ? "active" : ""}`}
        onDragEnter={onDragEnter}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <label className="upload-zone">
          <span className="upload-icon">📷</span>
          <span>Drop image here or upload</span>
          <input type="file" accept="image/*" onChange={onImageChange} hidden />
        </label>
      </div>
    );
  }

  return (
    <div className="image-preview-card">
      <div
        className={`image-preview-inner ${zoom ? "zoomed" : ""}`}
        onClick={() => setZoom(!zoom)}
      >
        <BoundingBoxOverlay
          imageUrl={preview}
          objects={detectedObjects}
          imageWidth={imageDimensions.width}
          imageHeight={imageDimensions.height}
        />
      </div>
      <label className="change-image-btn">
        Change image
        <input type="file" accept="image/*" onChange={onImageChange} hidden />
      </label>
    </div>
  );
}
