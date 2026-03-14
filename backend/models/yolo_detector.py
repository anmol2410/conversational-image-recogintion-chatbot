"""YOLOv8 object detection with attributes: bbox, color, position, state."""
import cv2
from pathlib import Path
from typing import List, Dict, Any, Optional

# Lazy load to allow GPU detection
_model = None


def _get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        model_path = Path(__file__).resolve().parent.parent / "yolov8n.pt"
        _model = YOLO(str(model_path)) if model_path.exists() else YOLO("yolov8n.pt")
    return _model


import sys
_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))
from utils.color_detection import get_dominant_color


def get_position(bbox: list, image_height: int, image_width: int) -> str:
    """Position description: vertical-horizontal (e.g. middle-left)."""
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    h_pos = "left" if cx < image_width * 0.33 else ("right" if cx > image_width * 0.67 else "center")
    v_pos = "top" if cy < image_height * 0.33 else ("bottom" if cy > image_height * 0.67 else "middle")
    return f"{v_pos}-{h_pos}"


def get_object_state(obj_name: str, confidence: float) -> str:
    """State label from confidence and object type."""
    movement_prone = [
        "person", "dog", "cat", "bird", "horse", "cow", "sheep", "elephant",
        "bear", "zebra", "giraffe", "car", "truck", "bicycle", "motorcycle"
    ]
    if obj_name.lower() in movement_prone:
        if confidence > 0.85:
            return "clearly visible"
        if confidence > 0.7:
            return "visible"
        return "partially visible"
    return "detected"


def _relative_size(bbox: list, image_height: int, image_width: int) -> str:
    """Describe object size relative to image (small / medium / large)."""
    x1, y1, x2, y2 = bbox
    area = (x2 - x1) * (y2 - y1)
    total = image_height * image_width
    pct = area / total if total > 0 else 0
    if pct < 0.02:
        return "small"
    if pct < 0.15:
        return "medium"
    return "large"


def compute_relations(objects: List[Dict], img_h: int, img_w: int) -> List[str]:
    """Compute simple spatial relations between objects (e.g. 'person is left of car')."""
    if len(objects) < 2:
        return []
    relations = []
    for i, a in enumerate(objects):
        ax1, ay1, ax2, ay2 = a["bbox"]
        acx = (ax1 + ax2) / 2
        acy = (ay1 + ay2) / 2
        for j, b in enumerate(objects):
            if i >= j:
                continue
            bx1, by1, bx2, by2 = b["bbox"]
            bcx = (bx1 + bx2) / 2
            bcy = (by1 + by2) / 2
            dx = abs(acx - bcx)
            dy = abs(acy - bcy)
            dist = (dx * dx + dy * dy) ** 0.5
            max_span = max(img_w, img_h) * 0.4
            if dist > max_span:
                continue
            aname, bname = a["name"], b["name"]
            if acx < bcx - img_w * 0.05:
                relations.append(f"{aname} is to the left of {bname}")
            elif acx > bcx + img_w * 0.05:
                relations.append(f"{aname} is to the right of {bname}")
            if acy < bcy - img_h * 0.05:
                relations.append(f"{aname} is above {bname}")
            elif acy > bcy + img_h * 0.05:
                relations.append(f"{aname} is below {bname}")
            if dist < max_span * 0.5:
                relations.append(f"{aname} is near {bname}")
    return relations[:15]  # cap to avoid clutter


def detect_objects(
    image_path: str,
    conf_threshold: float = 0.5,
    cv_image: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Run YOLOv8 and return list of objects with name, confidence, color, position, bbox, state, size.
    If cv_image is provided (BGR), use it for color analysis; else read from image_path.
    """
    try:
        model = _get_model()
        cv_img = cv_image if cv_image is not None else cv2.imread(image_path)
        if cv_img is None:
            return []
        h, w = cv_img.shape[:2]
        results = model(image_path, conf=conf_threshold, verbose=False)
        out = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().tolist()
                name = model.names[cls_id]
                color = get_dominant_color(cv_img, bbox)
                position = get_position(bbox, h, w)
                state = get_object_state(name, confidence)
                size_desc = _relative_size(bbox, h, w)
                out.append({
                    "name": name,
                    "confidence": round(confidence, 2),
                    "color": color,
                    "position": position,
                    "bbox": [float(x) for x in bbox],
                    "state": state,
                    "size": size_desc,
                })
        return out
    except Exception as e:
        print(f"YOLO detect_objects error: {e}")
        return []
