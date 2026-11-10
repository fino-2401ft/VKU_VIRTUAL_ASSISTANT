from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

STORE_DIR = Path(__file__).resolve().parent.parent / "data" / "vector_store"
CHUNKS_PATH = STORE_DIR / "chunks.json"
META_PATH = STORE_DIR / "meta.json"


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def store_exists() -> bool:
    return CHUNKS_PATH.exists() and META_PATH.exists()


def load_chunks() -> list[dict[str, Any]]:
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def save_store(chunks: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    META_PATH.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def search(query_embedding: list[float], top_k: int = 4) -> list[dict[str, Any]]:
    chunks = load_chunks()
    scored: list[tuple[float, dict[str, Any]]] = []
    for ch in chunks:
        emb = ch.get("embedding") or []
        score = _cosine(query_embedding, emb)
        if score > 0:
            scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, ch in scored[:top_k]:
        item = {k: v for k, v in ch.items() if k != "embedding"}
        item["score"] = round(score, 4)
        results.append(item)
    return results


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> list[str]:
    """
    Ưu tiên cắt theo dòng để không làm vỡ các dòng mức học phí
    (tránh lỗi '497.800' bị cắt thành '0 đồng...').
    """
    if not text or not text.strip():
        return []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []

    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for ln in lines:
        add_len = len(ln) + (1 if buf else 0)
        if buf and buf_len + add_len > chunk_size:
            chunks.append("\n".join(buf))
            # overlap theo số dòng cuối
            keep: list[str] = []
            keep_len = 0
            for old in reversed(buf):
                if keep_len + len(old) + 1 > overlap:
                    break
                keep.insert(0, old)
                keep_len += len(old) + 1
            buf = keep
            buf_len = keep_len
        buf.append(ln)
        buf_len += add_len
    if buf:
        chunks.append("\n".join(buf))
    return chunks
