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

from . import ollama_client
from .knowledge import SUGGESTIONS, answer_question, load_faq
from .rag import answer_with_rag, rag_ready
from .rag_store import load_chunks, store_exists

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(
    title="VKU Virtual Assistant API",
    description="Trợ lý ảo học vụ & tuyển sinh VKU — RAG (Ollama) + FAQ fallback",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def resolve_answer(message: str) -> dict[str, Any]:
    """Ưu tiên RAG Ollama; lỗi/thiếu thì fallback FAQ."""
    if rag_ready():
        try:
            return answer_with_rag(message)
        except Exception as exc:  # noqa: BLE001
            faq = answer_question(message)
            faq["answer"] = (
                f"(RAG tạm lỗi: {exc})\n\n" + faq["answer"]
                if faq.get("mode") == "faq-demo"
                else faq["answer"]
            )
            faq["mode"] = "faq-fallback"
            return faq
    return answer_question(message)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "vku-virtual-assistant",
        "faq_items": len(load_faq()),
        "ollama": ollama_client.is_available(),
        "vector_store": store_exists(),
        "chunk_count": len(load_chunks()) if store_exists() else 0,
        "rag_ready": rag_ready(),
        "chat_model": ollama_client.CHAT_MODEL,
        "embed_model": ollama_client.EMBED_MODEL,
        "note": "RAG tự build (Ollama + vector store). Triển khai Cloud: EC2 + S3. Không dùng Bedrock.",
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

    result = resolve_answer(body.message)
    history.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "ts": time.time(),
            "sources": result["sources"],
            "mode": result.get("mode"),
        }
    )
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
