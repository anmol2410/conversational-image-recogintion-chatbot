# AI Visual Assistant — System Architecture

## High-level flow

```
┌─────────────┐     POST /analyze/      ┌─────────────┐
│   React     │  (file + question +     │   FastAPI   │
│   Frontend  │   session_id?)          │   Backend   │
└──────┬──────┘                         └──────┬──────┘
       │                                       │
       │ 1. Upload image                       │ 2. Save image
       │ 2. Send question                     │ 3. Run pipeline
       │ 3. Display bbox + answer             └──────┬──────┘
       │                                            │
       │                                    ┌───────▼───────┐
       │                                    │ Visual        │
       │                                    │ Pipeline      │
       │                                    └───────┬───────┘
       │                                            │
       │         ┌──────────────────────────────────┼──────────────────────┐
       │         │                                  │                      │
       │    ┌────▼────┐  ┌─────────────┐  ┌────────▼────────┐  ┌──────────▼──────────┐
       │    │ YOLOv8  │  │ BLIP        │  │ Conversation    │  │ AI Chatbot          │
       │    │ Detector│  │ Caption     │  │ Manager         │  │ (LLM or rule-based) │
       │    └────┬────┘  └──────┬──────┘  │ (session state) │  └──────────┬──────────┘
       │         │              │         └─────────────────┘             │
       │         │              │                                          │
       │    objects + bbox     caption                    history + context
       │         │              │                                          │
       │         └──────────────┴──────────────────────────► answer
       │
       ◄───────────────────────────────────────────────────────────────────
                    JSON: detected_objects, caption, answer, session_id
```

## Backend structure

```
backend/
├── main.py                    # FastAPI app, POST /analyze/, GET /health
├── models/
│   ├── yolo_detector.py      # YOLOv8 detection, bbox, color, position, size, relations
│   ├── caption_model.py      # BLIP image captioning (optional)
│   └── ocr_model.py          # EasyOCR text detection (optional)
├── services/
│   ├── visual_reasoning.py   # Pipeline: YOLO + BLIP + OCR + relations → chatbot; caching
│   └── conversation_manager.py  # Session: objects, caption, ocr_text, relationships, history
├── chatbot/
│   └── ai_chatbot.py         # LLM or rule-based; full context (scene, OCR, relations, safety)
└── utils/
    ├── image_utils.py        # Save upload, preprocessing
    └── color_detection.py    # RGB → color name per region
```

## Data flow

1. **Request:** Client sends image + question (+ optional `session_id`).
2. **Save:** Image saved under `uploads/` with UUID name.
3. **Cache:** If same image (hash) was analyzed before, reuse detection, caption, OCR, relations.
4. **Detection:** YOLOv8 returns objects with bbox, confidence, color, position, size; relations computed between objects.
5. **Caption:** BLIP generates scene description (or empty if not installed).
6. **OCR:** EasyOCR extracts visible text (optional).
7. **Safety:** Check for dangerous objects; add warnings if any.
8. **Session:** Conversation manager updates session (objects, caption, ocr_text, relationships) and appends user/bot turn.
9. **Answer:** AI chatbot gets full context and returns detailed natural-language answer (LLM or rule-based).
10. **Response:** JSON with `detected_objects`, `caption`, `ocr_text`, `relationships`, `safety_warnings`, `answer`, `session_id`.

## Frontend structure

```
frontend/src/
├── App.js              # Main layout, state, API calls, session_id
├── App.css             # Two-column layout, theme, components
├── context/
│   └── ThemeContext.jsx # Dark/light theme
└── components/
    ├── CameraCapture.jsx        # Webcam capture (getUserMedia)
    ├── BoundingBoxOverlay.jsx   # Canvas overlay for bboxes
    ├── ObjectStatsSidebar.jsx   # Object counts + confidence
    ├── ImageAnalysisReport.jsx  # Collapsible report: scene, objects, relations, text, safety
    └── VoiceInputButton.jsx     # Speech-to-text (Web Speech API)
```

## Optional: LLM, caption, OCR

- **OCR:** Requires `easyocr`. If not installed, text detection is skipped.

- **LLM:** Set `OPENAI_API_KEY` (and optionally `OPENAI_API_BASE`, `LLM_MODEL`). For Ollama, set `OPENAI_API_BASE=http://localhost:11434/v1` and no key. If unset, rule-based answers are used.
- **Caption:** Requires `transformers` and `torch`. If not installed, caption is empty and answers use only detection data.
