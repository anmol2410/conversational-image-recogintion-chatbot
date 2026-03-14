# AI Visual Assistant — API Documentation

Base URL: `http://127.0.0.1:8000` (default)

## Endpoints

### GET `/health`

Health check.

**Response**
```json
{ "status": "ok", "service": "AI Visual Assistant" }
```

---

### POST `/analyze/`

Analyze an image and answer a natural-language question. Supports **conversation memory** via `session_id`.

**Request:** `multipart/form-data`

| Field        | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| `file`      | File   | Yes      | Image file (JPEG, PNG, WebP, BMP)               |
| `question`  | string | Yes      | Question about the image                         |
| `session_id`| string | No       | Session ID for follow-up questions (returned in first response) |

**Response**
```json
{
  "success": true,
  "detected_objects": [
    {
      "name": "person",
      "confidence": 0.92,
      "color": "blue",
      "position": "middle-center",
      "bbox": [100.2, 80.5, 250.1, 380.0],
      "state": "clearly visible",
      "size": "medium"
    }
  ],
  "caption": "a person standing next to a car",
  "ocr_text": "Hello World",
  "relationships": ["person is to the left of car", "person is near car"],
  "safety_warnings": [],
  "answer": "The image shows a person standing next to a car. The person is in the middle-center and the car is on the right.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error response** (e.g. invalid image or server error)
```json
{
  "success": false,
  "detected_objects": [],
  "caption": "",
  "ocr_text": "",
  "relationships": [],
  "safety_warnings": [],
  "answer": "Sorry, I couldn't process the image or your question. Please try again.",
  "session_id": null
}
```

---

## Question types supported

- **Counting:** e.g. "How many people are there?"
- **Spatial:** e.g. "Where is the dog?"
- **Color:** e.g. "What color is the car?"
- **Relationship:** e.g. "Is the dog near the person?"
- **Scene:** e.g. "Describe the image", "What do you see?", "What is happening?"
- **Text/OCR:** e.g. "What text is written?", "What does the sign say?"
- **Safety:** e.g. "Is there anything dangerous?"
- **Confidence:** e.g. "How confident are you?"

---

## OpenAPI (Swagger)

Interactive docs: **http://127.0.0.1:8000/docs**  
ReDoc: **http://127.0.0.1:8000/redoc**
