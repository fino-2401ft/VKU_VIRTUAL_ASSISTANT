from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .knowledge import SUGGESTIONS, answer_question, load_faq

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(
    title="VKU Virtual Assistant API",
    description="Demo trợ lý ảo học vụ & tuyển sinh VKU (local MVP)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# sessionId -> list of {role, content, ts}
SESSIONS: dict[str, list[dict[str, Any]]] = {}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict[str, Any]]
    category: str | None
    confidence: float
    mode: str


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "vku-virtual-assistant",
        "faq_items": len(load_faq()),
        "note": "Local demo — sẽ thay bằng API Gateway + Lambda + Bedrock KB trên AWS",
    }


@app.get("/api/suggestions")
def suggestions():
    return {"suggestions": SUGGESTIONS}


@app.get("/api/categories")
def categories():
    cats: dict[str, str] = {}
    for item in load_faq():
        cats[item["category"]] = item.get("category_name", item["category"])
    return {"categories": [{"id": k, "name": v} for k, v in sorted(cats.items())]}


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())
    history = SESSIONS.setdefault(session_id, [])
    history.append({"role": "user", "content": body.message, "ts": time.time()})

    result = answer_question(body.message)
    history.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "ts": time.time(),
            "sources": result["sources"],
        }
    )
    # giữ tối đa 40 message / session (demo in-memory)
    SESSIONS[session_id] = history[-40:]

    return ChatResponse(
        session_id=session_id,
        answer=result["answer"],
        sources=result["sources"],
        category=result["category"],
        confidence=result["confidence"],
        mode=result["mode"],
    )


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    return {"session_id": session_id, "messages": SESSIONS.get(session_id, [])}


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

    @app.get("/")
    def index():
        return FileResponse(FRONTEND_DIR / "index.html")
