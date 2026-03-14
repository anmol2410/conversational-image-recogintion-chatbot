"""
Session-based conversation memory: last image analysis (objects, caption) + chat history.
In-memory store keyed by session_id; suitable for single-server deployment.
"""
import uuid
from typing import List, Dict, Any, Optional

# session_id -> { "objects", "caption", "ocr_text", "relationships", "image_path", "history" }
_sessions: Dict[str, Dict[str, Any]] = {}


def _ensure_session(session_id: Optional[str]) -> str:
    if not session_id or session_id not in _sessions:
        new_id = str(uuid.uuid4())
        _sessions[new_id] = {
            "objects": [],
            "caption": "",
            "ocr_text": "",
            "relationships": [],
            "image_path": "",
            "history": [],
        }
        return new_id
    return session_id


def get_conversation_manager():
    return ConversationManager()


class ConversationManager:
    """Per-session state: current detection, caption, OCR, relationships, and chat history."""

    def update_image_context(
        self,
        session_id: Optional[str],
        image_path: str,
        objects: List[Dict],
        caption: str,
        ocr_text: str = "",
        relationships: Optional[List[str]] = None,
    ) -> str:
        """Store new image analysis for this session. Returns session_id."""
        sid = _ensure_session(session_id)
        _sessions[sid]["image_path"] = image_path
        _sessions[sid]["objects"] = objects
        _sessions[sid]["caption"] = caption
        _sessions[sid]["ocr_text"] = ocr_text or ""
        _sessions[sid]["relationships"] = list(relationships or [])
        return sid

    def get_context(self, session_id: Optional[str]) -> Dict[str, Any]:
        """Return current objects, caption, OCR, relationships, and history for session."""
        sid = _ensure_session(session_id)
        s = _sessions[sid]
        return {
            "objects": s["objects"],
            "caption": s["caption"],
            "ocr_text": s.get("ocr_text", ""),
            "relationships": s.get("relationships", []),
            "image_path": s["image_path"],
            "history": list(s["history"]),
        }

    def append_turn(self, session_id: str, role: str, text: str) -> None:
        """Append a user or bot message to history."""
        if session_id not in _sessions:
            _ensure_session(session_id)
        _sessions[session_id]["history"].append({"role": role, "text": text})

    def get_history(self, session_id: Optional[str]) -> List[Dict[str, str]]:
        """Return chat history for LLM context."""
        sid = _ensure_session(session_id)
        return list(_sessions[sid]["history"])
