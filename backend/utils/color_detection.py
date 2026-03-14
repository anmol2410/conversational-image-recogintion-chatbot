"""Dominant color extraction from image regions (RGB to color name)."""
import cv2
import numpy as np


def get_dominant_color(image: np.ndarray, bbox: list) -> str:
    """Extract dominant color from a region in the image (BGR)."""
    try:
        x1, y1, x2, y2 = [int(x) for x in bbox]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image.shape[1], x2)
        y2 = min(image.shape[0], y2)
        if x1 >= x2 or y1 >= y2:
            return "unknown"
        region = image[y1:y2, x1:x2]
        if region.size == 0:
            return "unknown"
        region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        h, w = region_rgb.shape[:2]
        if h > 30 and w > 30:
            region_rgb = region_rgb[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]
        pixels = region_rgb.reshape(-1, 3)
        avg_color = pixels.mean(axis=0)
        r, g, b = avg_color[0], avg_color[1], avg_color[2]
        return get_color_name(r, g, b)
    except Exception:
        return "unknown"


def get_color_name(r: float, g: float, b: float) -> str:
    """Map RGB to a color name."""
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val
    if diff < 0.15:
        if max_val > 0.7:
            return "white"
        if max_val < 0.2:
            return "black"
        return "gray"
    if r_norm == max_val:
        if g_norm > b_norm:
            return "orange" if g_norm > 0.4 else "red"
        return "dark red" if r_norm < 0.5 else "red"
    if g_norm == max_val:
        return "green" if g_norm > 0.5 else "dark green"
    if b_norm == max_val:
        if r_norm > 0.3:
            return "purple"
        return "blue" if b_norm > 0.5 else "dark blue"
    if r_norm > 0.6 and g_norm > 0.6 and b_norm < 0.3:
        return "yellow"
    return "mixed"
