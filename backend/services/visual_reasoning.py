"""
Visual pipeline: YOLO detection + BLIP caption + OCR + relations -> AI reasoning.
Supports detection caching and fast follow-up questions.
"""
import hashlib
import os
import cv2
from pathlib import Path
from typing import List, Dict, Any, Optional

# Cache: image_path_hash -> { "objects", "caption", "ocr_text", "relationships" }
_detection_cache: Dict[str, Dict[str, Any]] = {}
_cache_max = 50


def _cache_key(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return path


def _get_cached(path: str) -> Optional[Dict[str, Any]]:
    key = _cache_key(path)
    return _detection_cache.get(key)


def _set_cache(path: str, data: Dict[str, Any]) -> None:
    global _detection_cache
    key = _cache_key(path)
    _detection_cache[key] = data
    if len(_detection_cache) > _cache_max:
        keys = list(_detection_cache.keys())
        for k in keys[: _cache_max // 2]:
            del _detection_cache[k]


def _safety_warnings(objects: List[Dict]) -> List[str]:
    """Check for potentially dangerous objects."""
    dangerous = ["knife", "gun", "weapon", "fire", "explosive", "scissors"]
    found = [o["name"] for o in objects if o.get("name", "").lower() in dangerous]
    if not found:
        return []
    return [f"Caution: potentially dangerous item(s) detected: {', '.join(found)}."]


def _should_use_fast_mode() -> bool:
    """
    Fast mode is useful on small/free instances (like Render free tier).
    - Enable explicitly with FAST_MODE=true
    - Auto-enable on Render unless FAST_MODE=false is set
    """
    fast_env = os.getenv("FAST_MODE")
    if fast_env is not None:
        return fast_env.strip().lower() in {"1", "true", "yes", "on"}
    return os.getenv("RENDER") is not None


def run_visual_pipeline(
    image_path: str,
    question: str,
    session_id: Optional[str] = None,
    use_cache: bool = True,
    conversation_manager: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Run full pipeline: YOLO + BLIP caption + OCR + relations → chatbot.
    Returns: success, detected_objects, caption, ocr_text, relationships, safety_warnings, answer, session_id.
    """
    import sys
    backend = Path(__file__).resolve().parent.parent
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))

    from models.yolo_detector import detect_objects, compute_relations
    from models.caption_model import get_caption
    from models.ocr_model import get_text_in_image, get_ocr_text_flat
    from chatbot.ai_chatbot import generate_answer

    conv = conversation_manager
    if conv is None:
        from services.conversation_manager import get_conversation_manager
        conv = get_conversation_manager()

    cached = _get_cached(image_path) if use_cache else None
    if cached:
        objects = cached["objects"]
        caption = cached.get("caption", "")
        ocr_text = cached.get("ocr_text", "")
        relationships = cached.get("relationships", [])
    else:
        objects = detect_objects(image_path)
        caption = "" if _should_use_fast_mode() else get_caption(image_path)
        ocr_raw = get_text_in_image(image_path)
        ocr_text = " ".join(t[0] for t in ocr_raw).strip() if ocr_raw else get_ocr_text_flat(image_path)
        img = cv2.imread(image_path)
        h, w = (img.shape[0], img.shape[1]) if img is not None else (0, 0)
        relationships = compute_relations(objects, h, w) if objects else []
        if use_cache:
            _set_cache(image_path, {
                "objects": objects,
                "caption": caption,
                "ocr_text": ocr_text,
                "relationships": relationships,
            })

    safety = _safety_warnings(objects)
    session_id = conv.update_image_context(
        session_id, image_path, objects, caption,
        ocr_text=ocr_text, relationships=relationships,
    )
    history = conv.get_history(session_id)
    answer = generate_answer(
        objects, question,
        caption=caption,
        history=history,
        ocr_text=ocr_text,
        relationships=relationships,
        safety_warnings=safety,
    )
    conv.append_turn(session_id, "user", question)
    conv.append_turn(session_id, "bot", answer)

    return {
        "success": True,
        "detected_objects": objects,
        "caption": caption,
        "ocr_text": ocr_text,
        "relationships": relationships,
        "safety_warnings": safety,
        "answer": answer,
        "session_id": session_id,
    }


def run_followup_question(
    question: str,
    session_id: str,
    conversation_manager: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Answer follow-up question from session context only (no image re-upload/re-detection).
    """
    import sys
    backend = Path(__file__).resolve().parent.parent
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))

    from chatbot.ai_chatbot import generate_answer

    conv = conversation_manager
    if conv is None:
        from services.conversation_manager import get_conversation_manager
        conv = get_conversation_manager()

    context = conv.get_context(session_id)
    objects = context.get("objects", [])
    caption = context.get("caption", "")
    ocr_text = context.get("ocr_text", "")
    relationships = context.get("relationships", [])
    history = context.get("history", [])
    safety = _safety_warnings(objects)

    answer = generate_answer(
        objects,
        question,
        caption=caption,
        history=history,
        ocr_text=ocr_text,
        relationships=relationships,
        safety_warnings=safety,
    )
    conv.append_turn(session_id, "user", question)
    conv.append_turn(session_id, "bot", answer)

    return {
        "success": True,
        "detected_objects": objects,
        "caption": caption,
        "ocr_text": ocr_text,
        "relationships": relationships,
        "safety_warnings": safety,
        "answer": answer,
        "session_id": session_id,
        "from_cache": True,
    }
