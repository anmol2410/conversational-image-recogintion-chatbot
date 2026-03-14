from ultralytics import YOLO
import cv2
import numpy as np
from collections import Counter

# Load lightweight YOLO model
model = YOLO("yolov8n.pt")

def get_dominant_color(image, bbox):
    """Extract dominant color from a region in the image"""
    try:
        x1, y1, x2, y2 = bbox
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Ensure coordinates are within image bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image.shape[1], x2)
        y2 = min(image.shape[0], y2)
        
        # Make sure we have valid coordinates
        if x1 >= x2 or y1 >= y2:
            return "unknown"
        
        region = image[y1:y2, x1:x2]
        
        if region.size == 0:
            return "unknown"
        
        # Convert BGR to RGB for analysis
        region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        
        # Sample center pixels for faster processing
        h, w = region_rgb.shape[:2]
        if h > 30 and w > 30:
            region_rgb = region_rgb[h//4:3*h//4, w//4:3*w//4]
        
        # Reshape to analyze colors
        pixels = region_rgb.reshape(-1, 3)
        
        # Calculate average color
        avg_color = pixels.mean(axis=0)
        r, g, b = avg_color[0], avg_color[1], avg_color[2]
        
        # Determine color name
        color_name = get_color_name(r, g, b)
        return color_name
    except:
        return "unknown"

def get_color_name(r, g, b):
    """Convert RGB to color name"""
    # Normalize values to 0-1 range
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val
    
    # Check if it's grayscale (all channels similar)
    if diff < 0.15:
        if max_val > 0.7:
            return "white"
        elif max_val < 0.2:
            return "black"
        else:
            return "gray"
    
    # Determine the dominant color
    if r_norm == max_val:
        # Red family
        if g_norm > b_norm:
            return "orange" if g_norm > 0.4 else "red"
        else:
            return "dark red" if r_norm < 0.5 else "red"
    elif g_norm == max_val:
        # Green family
        return "green" if g_norm > 0.5 else "dark green"
    elif b_norm == max_val:
        # Blue family
        if r_norm > 0.3:
            return "purple"
        else:
            return "blue" if b_norm > 0.5 else "dark blue"
    
    # Yellow and other combinations
    if r_norm > 0.6 and g_norm > 0.6 and b_norm < 0.3:
        return "yellow"
    
    return "mixed"

def get_position(bbox, image_height, image_width):
    """Get position description (left/center/right, top/middle/bottom)"""
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    # Horizontal position
    if center_x < image_width * 0.33:
        h_pos = "left"
    elif center_x > image_width * 0.67:
        h_pos = "right"
    else:
        h_pos = "center"
    
    # Vertical position
    if center_y < image_height * 0.33:
        v_pos = "top"
    elif center_y > image_height * 0.67:
        v_pos = "bottom"
    else:
        v_pos = "middle"
    
    return f"{v_pos}-{h_pos}"

def detect_objects(image_path):
    """Detect objects with detailed information - optimized for speed"""
    try:
        # Read image with OpenCV for color analysis - ORIGINAL SIZE
        cv_image = cv2.imread(image_path)
        if cv_image is None:
            return []
        
        image_height, image_width = cv_image.shape[:2]
        
        # Run YOLO detection on original image
        results = model(image_path, conf=0.5)
        detected_objects = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                
                obj_name = model.names[cls_id]
                color = get_dominant_color(cv_image, bbox)
                position = get_position(bbox, image_height, image_width)
                state = get_object_state(obj_name, confidence)
                
                detected_objects.append({
                    "name": obj_name,
                    "confidence": round(confidence, 2),
                    "color": color,
                    "position": position,
                    "bbox": [float(x) for x in bbox],
                    "state": state
                })
        
        return detected_objects
    except Exception as e:
        print(f"Error in detect_objects: {e}")
        return []

def get_object_state(obj_name, confidence):
    """Determine possible state of object based on class"""
    # Motion indicators based on confidence and object type
    movement_prone = ["person", "dog", "cat", "bird", "horse", "cow", "sheep", "elephant", 
                      "bear", "zebra", "giraffe", "car", "truck", "bicycle", "motorcycle"]
    
    if obj_name.lower() in movement_prone:
        if confidence > 0.85:
            return "clearly visible"
        elif confidence > 0.7:
            return "visible"
        else:
            return "partially visible"
    
    return "detected"