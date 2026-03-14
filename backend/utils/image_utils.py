"""Image handling: save uploads, preprocessing, resize for models."""
import os
import uuid
import cv2
import numpy as np
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
MAX_IMAGE_DIM = 640  # YOLO-friendly; BLIP can use same or smaller
JPEG_QUALITY = 95

os.makedirs(UPLOAD_DIR, exist_ok=True)


def ensure_upload_dir() -> str:
    """Ensure upload directory exists; return path."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


def save_upload_image(file: UploadFile) -> str:
    """Save uploaded file to disk with UUID prefix. Returns path."""
    ensure_upload_dir()
    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    content = file.file.read()
    with open(path, "wb") as f:
        f.write(content)
    return path


def preprocess_image(image_path: str, max_dim: int = MAX_IMAGE_DIM) -> np.ndarray:
    """
    Load image and optionally resize for faster inference while preserving aspect ratio.
    Returns BGR numpy array (OpenCV format).
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img
