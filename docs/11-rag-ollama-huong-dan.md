# Hướng RAG tự build (Ollama) — chính thức

> Đây là hướng triển khai **đã chốt** của dự án. Không dùng Amazon Bedrock.

## Kiến trúc

```text
data/pdfs/** (DOCX/PDF)
        ↓  ingest (một lần / khi thêm file)
   chunk + embedding (Ollama nomic-embed-text)
        ↓
   Vector store local (backend/data/vector_store/)
        ↓
User hỏi → retrieve top-k đoạn
        ↓
Ollama LLM (qwen2.5:3b / llama3.2:3b) sinh trả lời + sources
        ↓
FastAPI /api/chat → Web UI
```

Sau này đưa cùng stack lên **EC2** (trả bằng credit $120).

## Phase làm việc

| Phase | Việc | Ở đâu |
|---|---|---|
| 1 | Cài Ollama + pull model | Laptop |
| 2 | Ingest tài liệu → vector store | Laptop |
| 3 | Chat RAG qua web | Laptop |
| 4 | Deploy EC2 + S3 sync docs | AWS |

## Bước 1 — Cài Ollama (laptop)

1. Tải: https://ollama.com/download  
2. Cài xong, mở PowerShell:

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
ollama list
```

3. Kiểm tra API: mở http://127.0.0.1:11434 — phải thấy Ollama đang chạy.

## Bước 2 — Chạy backend RAG

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ingest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000 — hỏi về học phí.

- Có Ollama + đã ingest → `mode: rag-ollama`  
- Ollama tắt / chưa ingest → fallback FAQ demo  

## Bước 3 — Lên EC2 (sau khi local OK)

1. EC2 Ubuntu, RAM ≥ 8GB (vd. `t3.large` / `t3.xlarge`)  
2. Cài Ollama + pull cùng 2 model  
3. Clone repo, `ingest`, chạy uvicorn (hoặc systemd)  
4. Security Group: mở 80/443; **không** public port 11434  
5. **Stop** instance khi không demo  

Chi tiết deploy EC2 sẽ bổ sung khi Phase 1–3 xong.

## So sánh với Bedrock (1 slide báo cáo)

| | Bedrock KB (không chọn) | RAG tự build + Ollama trên EC2 (**đã chọn**) |
|---|---|---|
| Model | Managed | Open-source tự host |
| Pipeline RAG | AWS quản lý | Nhóm tự build (ingest–retrieve–generate) |
| Phí | Token + KB | Giờ EC2 (credit $120) |
| Ops | Ít | Tự cài, Stop máy khi không dùng |
| Lý do chọn | Phụ thuộc managed AI / account hạn chế | Chủ động, đúng tinh thần tự xây hệ thống |
