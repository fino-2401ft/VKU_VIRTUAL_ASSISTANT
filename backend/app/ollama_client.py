from __future__ import annotations

import os
from typing import Any

import httpx

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
# qwen3 hay "thinking" trong content → mặc định dùng qwen2.5 cho demo nhanh
CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")


def is_available(timeout: float = 2.0) -> bool:
    try:
        r = httpx.get(f"{OLLAMA_BASE}/api/tags", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def embed(text: str, timeout: float = 45.0) -> list[float]:
    r = httpx.post(
        f"{OLLAMA_BASE}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    emb = data.get("embedding")
    if not emb:
        raise RuntimeError(f"Ollama embed trả về rỗng: {data}")
    return emb


def _strip_reasoning(content: str) -> str:
    """Qwen3 đôi khi nhét suy nghĩ vào content dù think=false."""
    text = (content or "").strip()
    if "</think>" in text:
        text = text.split("</think>", 1)[-1].strip()
    # cắt block think nếu còn mở
    lower = text.lower()
    if "<think>" in lower:
        # bỏ mọi thứ trước câu trả lời tiếng Việt thường gặp
        for marker in ("Trả lời:", "Câu trả lời:", "Đáp án:"):
            if marker in text:
                text = text.split(marker, 1)[-1].strip()
                break
    # nếu vẫn là đoạn suy nghĩ tiếng Anh dài, lấy phần sau dòng trống cuối
    english_starts = ("okay,", "okay ", "let's", "first,", "looking at", "the user")
    if text.lower().startswith(english_starts) and "\n\n" in text:
        parts = [p.strip() for p in text.split("\n\n") if p.strip()]
        # ưu tiên đoạn cuối có dấu tiếng Việt
        for part in reversed(parts):
            if any(ch in part for ch in "ăâêôơưđĂÂÊÔƠƯĐ"):
                return part
        return parts[-1]
    return text


def chat(prompt: str, system: str, timeout: float = 60.0) -> str:
    # qwen3 hay "think" trong content → tắt think + /no_think + lọc output
    # Timeout ngắn trên EC2 nhỏ: quá hạn thì main.py fallback FAQ.
    user_content = f"{prompt}\n\n/no_think"
    r = httpx.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": CHAT_MODEL,
            "stream": False,
            "think": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            "options": {
                "temperature": 0.1,
                "num_predict": 400,
            },
        },
        timeout=timeout,
    )
    r.raise_for_status()
    data: dict[str, Any] = r.json()
    msg = data.get("message") or {}
    content = (msg.get("content") or "").strip()
    return _strip_reasoning(content)
