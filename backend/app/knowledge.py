from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "faq.json"

FALLBACK_ANSWER = (
    "Hiện mình chưa tìm thấy thông tin này trong tài liệu học vụ/tuyển sinh demo. "
    "Bạn thử hỏi về: học phí, tốt nghiệp, thi lại, học bổng, ngành tuyển sinh, "
    "hồ sơ xét tuyển, lịch nộp hồ sơ, hoặc địa chỉ VKU."
)

SUGGESTIONS = [
    "Học phí học kỳ 1 năm 2025-2026?",
    "Thời gian thu học phí học kỳ 2?",
    "Thông báo học phí GDQP năm 2025?",
    "Học phí học kỳ hè?",
    "Học phí trình độ thạc sĩ?",
    "Địa chỉ VKU ở đâu?",
]


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@lru_cache(maxsize=1)
def load_faq() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def search_faq(message: str, top_k: int = 3) -> list[dict[str, Any]]:
    query = _normalize(message)
    tokens = set(query.split())
    scored: list[tuple[float, dict[str, Any]]] = []

    for item in load_faq():
        score = 0.0
        for kw in item.get("keywords", []):
            nk = _normalize(kw)
            if nk and nk in query:
                score += 3.0
            elif nk and any(tok in nk or nk in tok for tok in tokens if len(tok) > 2):
                score += 1.2
        nq = _normalize(item.get("question", ""))
        overlap = tokens.intersection(set(nq.split()))
        score += len(overlap) * 0.8
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


OUT_OF_SCOPE = [
    "thoi tiet",
    "weather",
    "gpa cua toi",
    "diem cua toi",
    "mat khau",
    "bitcoin",
    "bong da",
]


def answer_question(message: str) -> dict[str, Any]:
    normalized = _normalize(message)
    if any(phrase in normalized for phrase in OUT_OF_SCOPE):
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
            "category": None,
            "confidence": 0.0,
            "mode": "fallback",
        }

    hits = search_faq(message)
    if not hits:
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
            "category": None,
            "confidence": 0.0,
            "mode": "fallback",
        }

    best = hits[0]
    confidence = min(0.95, 0.55 + 0.1 * len(hits))
    sources = [
        {
            "id": h["id"],
            "title": h.get("question", h["id"]),
            "category": h.get("category_name", h.get("category")),
            "file": h.get("source", "demo"),
        }
        for h in hits
    ]
    return {
        "answer": best["answer"],
        "sources": sources,
        "category": best.get("category_name"),
        "confidence": round(confidence, 2),
        "mode": "faq-demo",
    }
