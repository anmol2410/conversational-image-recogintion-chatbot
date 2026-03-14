"""
Professional AI Visual Assistant: LLM when configured, else rule-based.
Uses full context: objects (with size), caption, OCR text, relationships, safety.
"""
import os
from typing import List, Dict, Any, Optional

# Optional LLM client (OpenAI-compatible or Ollama)
def _call_llm(system_prompt: str, user_prompt: str, history: List[Dict[str, str]]) -> Optional[str]:
    """Call LLM if API key/base set. Returns None if unavailable."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")
    base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    if not api_key and "ollama" not in base.lower():
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key or "ollama", base_url=base if "ollama" in base.lower() else None)
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-10:]:
            role = "user" if h.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": h.get("text", "")})
        messages.append({"role": "user", "content": user_prompt})
        r = client.chat.completions.create(model=model, messages=messages, max_tokens=500)
        return (r.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"LLM call failed: {e}")
        return None


def _build_context(
    objects: List[Dict],
    caption: str,
    ocr_text: str = "",
    relationships: Optional[List[str]] = None,
    safety_warnings: Optional[List[str]] = None,
) -> str:
    """Build rich text context for the AI from detection, caption, OCR, relations."""
    parts = []
    if caption:
        parts.append(f"Scene description (image caption): {caption}")
    if objects:
        obj_lines = []
        for o in objects:
            size = o.get("size", "")
            line = f"- {o['name']} (confidence {o['confidence']*100:.0f}%): color={o['color']}, position={o['position']}, size={size}, state={o.get('state', '')}"
            obj_lines.append(line)
        parts.append("Detected objects:\n" + "\n".join(obj_lines))
    if relationships:
        parts.append("Spatial relationships:\n" + "\n".join(f"- {r}" for r in relationships))
    if ocr_text:
        parts.append(f"Text visible in the image: \"{ocr_text}\"")
    if safety_warnings:
        parts.append("Safety: " + " ".join(safety_warnings))
    return "\n\n".join(parts) if parts else "No object detection or caption available."


SYSTEM_PROMPT = """You are a professional AI Visual Understanding Assistant (like ChatGPT Vision or Google Gemini Vision). You answer questions about an image using ONLY the provided context: scene description, detected objects (with color, position, size, confidence), spatial relationships between objects, and any text detected in the image (OCR).

Answer in detailed, natural language. Be conversational and helpful.
- For "what do you see?" or "describe the image": give a rich scene description (e.g. "The image shows a classroom scene. Four students are sitting at desks writing in notebooks while a woman stands in front of them. A backpack is visible near one of the students.").
- For counting: give the number and briefly mention context.
- For colors, positions, relationships: answer precisely from the context.
- For "what text is written?" or "what does the text say?": use only the OCR text from the context; if no text is given, say no text was detected.
- For safety: if the context mentions dangerous items, state them clearly and advise caution.
Do not invent objects, text, or details not present in the context. If the context does not contain the answer, say so briefly."""


def generate_answer(
    objects: List[Dict[str, Any]],
    question: str,
    caption: str = "",
    history: Optional[List[Dict[str, str]]] = None,
    ocr_text: str = "",
    relationships: Optional[List[str]] = None,
    safety_warnings: Optional[List[str]] = None,
) -> str:
    """
    Generate answer using LLM if configured, else rule-based.
    history: list of {"role": "user"|"bot", "text": "..."}
    """
    history = history or []
    context = _build_context(objects, caption, ocr_text, relationships, safety_warnings)
    user_prompt = f"Context from image analysis:\n{context}\n\nUser question: {question}"

    answer = _call_llm(SYSTEM_PROMPT, user_prompt, history)
    if answer:
        return answer
    return _rule_based_answer(objects, question, caption, ocr_text, relationships, safety_warnings)


def _rule_based_answer(
    objects: List[Dict],
    question: str,
    caption: str = "",
    ocr_text: str = "",
    relationships: Optional[List[str]] = None,
    safety_warnings: Optional[List[str]] = None,
) -> str:
    """Fallback: rule-based answers with scene, OCR, relations, safety."""
    q = question.lower()
    rels = relationships or []

    # Text / OCR
    if "text" in q or "written" in q or "say" in q or "read" in q or "what does it say" in q:
        if ocr_text:
            return f"The text visible in the image reads: \"{ocr_text}\"."
        return "No text was detected in the image."

    # Safety
    if "danger" in q or "safe" in q or "dangerous" in q:
        if safety_warnings:
            return " ".join(safety_warnings)
        return "I don't see any obviously dangerous objects in the image."

    if not objects and not caption:
        return "I couldn't detect any objects in this image. Try another image or rephrase your question."

    by_name = {}
    for obj in objects:
        n = obj["name"]
        by_name.setdefault(n, []).append(obj)

    # Counting
    if "how many" in q:
        for name in by_name:
            if name in q:
                return f"I can see {len(by_name[name])} {name}(s)."
        return f"I can see {len(objects)} object(s) in total."

    # Color
    if "color" in q or "colour" in q:
        for obj in objects:
            if obj["name"].lower() in q:
                return f"The {obj['name']} is {obj['color']}."
        return "Here are the colors I see: " + ", ".join(f"{o['name']} is {o['color']}" for o in objects) + "."

    # Position
    if "where" in q or "position" in q or "located" in q:
        for obj in objects:
            if obj["name"].lower() in q:
                return f"The {obj['name']} is in the {obj['position']} of the image."
        return "Object positions: " + ", ".join(f"{o['name']} at {o['position']}" for o in objects) + "."

    # Relationships
    if "near" in q or "next to" in q or "relation" in q or "between" in q:
        if rels:
            return " ".join(rels[:5]) + "."
        return "Object positions: " + ", ".join(f"{o['name']} at {o['position']}" for o in objects) + "."

    # Presence
    if "is there" in q or "can you see" in q or "are there" in q:
        for name in by_name:
            if name in q:
                return f"Yes, I can see {len(by_name[name])} {name}(s)."
        return "I didn't detect that specific object in the image."

    # Describe scene / what do you see
    if "describe" in q or "explain" in q or "what do you see" in q or "what's in" in q or "what is happening" in q:
        return _scene_description(objects, caption, rels)

    # Confidence
    if "confidence" in q or "sure" in q or "accuracy" in q:
        return "Detection confidence: " + ", ".join(f"{o['name']} ({o['confidence']*100:.0f}%)" for o in objects) + "."

    return _scene_description(objects, caption, rels)


def _scene_description(objects: List[Dict], caption: str, relationships: List[str]) -> str:
    """Produce a natural scene description from objects, caption, and relations."""
    if caption:
        out = caption.rstrip(". ") + ". "
    else:
        out = "The image shows "
    if not objects:
        return out.strip() or "I couldn't detect specific objects in this image."
    by_name = {}
    for o in objects:
        by_name.setdefault(o["name"], []).append(o)
    parts = []
    for name, objs in by_name.items():
        n = len(objs)
        if n == 1:
            parts.append(f"a {name} ({objs[0]['color']}, {objs[0]['position']})")
        else:
            parts.append(f"{n} {name}s")
    out += " ".join(parts) + "."
    if relationships:
        out += " " + " ".join(relationships[:3]) + "."
    return out
