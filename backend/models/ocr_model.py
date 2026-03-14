"""
OCR for text detection in images. Uses EasyOCR when available, else returns empty.
Enables answers like "What is written on the notebook?"
"""
from typing import List, Tuple

_reader = None


def get_text_in_image(image_path: str) -> List[Tuple[str, List]]:
    """
    Return list of (text, bbox) detected in the image.
    bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] or similar for EasyOCR.
    """
    global _reader
    try:
        import easyocr
        if _reader is None:
            _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        result = _reader.readtext(image_path)
        # result: list of (bbox, text, confidence)
        return [(item[1], item[0]) for item in result if item[2] > 0.3]
    except ImportError:
        return []
    except Exception as e:
        print(f"OCR error: {e}")
        return []


def get_ocr_text_flat(image_path: str) -> str:
    """Return all detected text joined by space, for context."""
    items = get_text_in_image(image_path)
    if not items:
        return ""
    return " ".join(t[0] for t in items).strip()
