"""Image captioning with BLIP (optional). Falls back to text summary if unavailable."""
from typing import Optional

_caption_model = None
_caption_processor = None


def get_caption(image_path: str) -> str:
    """
    Generate a short image caption. Uses BLIP if transformers/torch available;
    otherwise returns a placeholder that visual_reasoning can replace with object summary.
    """
    global _caption_model, _caption_processor
    try:
        from PIL import Image
    except ImportError:
        return ""
    try:
        if _caption_model is None:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            _caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            _caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        image = Image.open(image_path).convert("RGB")
        inputs = _caption_processor(images=image, return_tensors="pt")
        out = _caption_model.generate(**inputs, max_length=50)
        caption = _caption_processor.decode(out[0], skip_special_tokens=True)
        return caption.strip() or ""
    except Exception as e:
        print(f"Caption model error (using fallback): {e}")
        return ""


def get_caption_available() -> bool:
    """Return True if BLIP can be loaded (for optional features)."""
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        return True
    except ImportError:
        return False
