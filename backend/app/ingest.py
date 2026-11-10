from __future__ import annotations

import time
from datetime import datetime, timezone

from . import ollama_client
from .normalized_corpus import ROOT, iter_normalized_chunks
from .rag_store import save_store


def run_ingest() -> dict:
    if not ollama_client.is_available():
        raise SystemExit(
            "Ollama chưa chạy. Hãy mở Ollama rồi: ollama pull nomic-embed-text"
        )

    docs = iter_normalized_chunks()
    if not docs:
        raise SystemExit(f"Không có markdown trong {ROOT}/hoc-phi hoặc {ROOT}/quy-che")

    chunks_out: list[dict] = []
    print(f"Tìm thấy {len(docs)} đoạn từ markdown đã chuẩn hóa. Bắt đầu ingest...")
    for i, doc in enumerate(docs):
        rel = doc["source"]
        piece = f"Tài liệu: {rel}\n{doc['text']}"
        emb = ollama_client.embed(piece)
        chunks_out.append(
            {
                "id": doc["id"],
                "text": piece,
                "source": rel,
                "chunk_index": i,
                "embedding": emb,
                "metadata": doc.get("metadata") or {},
                "kind": doc.get("kind"),
            }
        )
        if (i + 1) % 25 == 0 or i + 1 == len(docs):
            print(f"  - đã embed {i + 1}/{len(docs)}")
        time.sleep(0.01)

    fee_n = sum(1 for d in docs if d.get("kind") == "hoc-phi")
    reg_n = sum(1 for d in docs if d.get("kind") == "quy-che")
    meta = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "docs_root": str(ROOT),
        "collections": ["hoc-phi", "quy-che"],
        "file_count": len({d["source"] for d in docs}),
        "fee_record_count": fee_n,
        "regulation_chunk_count": reg_n,
        "chunk_count": len(chunks_out),
        "embed_model": ollama_client.EMBED_MODEL,
        "chat_model": ollama_client.CHAT_MODEL,
    }
    save_store(chunks_out, meta)
    print(f"Xong. {len(chunks_out)} chunks (học phí {fee_n}, quy chế {reg_n})")
    return meta


if __name__ == "__main__":
    run_ingest()
