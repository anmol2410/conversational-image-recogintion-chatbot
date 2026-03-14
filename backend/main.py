"""
AI Visual Assistant API: image analysis with YOLOv8 + caption + LLM/rule-based QA.
Endpoints: POST /analyze/ (image + question + optional session_id), GET /health.
"""
import sys
from pathlib import Path

# Ensure backend root is on path when running uvicorn from project root or backend
_BACKEND = Path(__file__).resolve().parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from services.visual_reasoning import run_visual_pipeline
from services.conversation_manager import get_conversation_manager

app = FastAPI(
    title="AI Visual Assistant",
    description="Visual understanding with YOLOv8, image captioning, and conversational AI.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_conversation_manager = get_conversation_manager()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Visual Assistant"}


@app.post("/analyze/")
async def analyze_image(
    file: UploadFile = File(...),
    question: str = Form(...),
    session_id: str = Form(None),
):
    """
    Analyze image and answer question. Uses session_id for conversation memory.
    Returns: success, detected_objects, caption, answer, session_id.
    """
    try:
        image_path = await save_upload_image_async(file)
        result = await run_visual_pipeline_async(
            image_path,
            question.strip(),
            session_id=session_id or None,
            conversation_manager=_conversation_manager,
        )
        return result
    except Exception as e:
        print(f"Analyze error: {e}")
        return {
            "success": False,
            "detected_objects": [],
            "caption": "",
            "ocr_text": "",
            "relationships": [],
            "safety_warnings": [],
            "answer": "Sorry, I couldn't process the image or your question. Please try again.",
            "session_id": None,
        }


async def save_upload_image_async(file: UploadFile) -> str:
    """Save uploaded file (async read, then write on disk)."""
    import asyncio
    import uuid
    import os
    from utils.image_utils import ensure_upload_dir
    content = await file.read()
    ensure_upload_dir()
    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    path = os.path.join("uploads", f"{uuid.uuid4()}{ext}")

    def _write():
        with open(path, "wb") as f:
            f.write(content)

    await asyncio.to_thread(_write)
    return path


async def run_visual_pipeline_async(
    image_path: str,
    question: str,
    session_id: str = None,
    conversation_manager=None,
):
    """Run pipeline in thread pool to avoid blocking event loop."""
    import asyncio
    return await asyncio.to_thread(
        run_visual_pipeline,
        image_path,
        question,
        session_id=session_id,
        use_cache=True,
        conversation_manager=conversation_manager,
    )
