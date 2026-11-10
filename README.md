# VKU Virtual Assistant

Trợ lý ảo tra cứu **học vụ** và **tuyển sinh** VKU — **tự build RAG AI** (Ollama) triển khai Cloud trên **AWS EC2 + S3**.

Môn: Điện toán đám mây · Nhóm 4 người  
**Không dùng Amazon Bedrock.**

## Trạng thái hiện tại

RAG local đã chạy: FastAPI + Ollama (`qwen3:4b` + `nomic-embed-text`) + vector store từ DOCX học phí.

- Hướng dẫn chạy: [DEMO.md](DEMO.md)  
- Kiến trúc RAG: [docs/11-rag-ollama-huong-dan.md](docs/11-rag-ollama-huong-dan.md)  
- Deploy AWS: [docs/09-aws-cau-hinh-du-an.md](docs/09-aws-cau-hinh-du-an.md)

### Chạy demo RAG

```powershell
ollama pull qwen3:4b
ollama pull nomic-embed-text

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ingest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000 — `/api/health` cần `"rag_ready": true`.

## Kiến trúc (đã chốt)

```text
Web chat → FastAPI (EC2)
         → retrieve vector store + Ollama (embed/chat)
         → tài liệu từ data/pdfs (sync S3)
```

## Tài liệu

| File | Nội dung |
|---|---|
| [docs/01-MVP.md](docs/01-MVP.md) | Phạm vi MVP (RAG tự build) |
| [docs/05-kien-truc.md](docs/05-kien-truc.md) | Sơ đồ kiến trúc |
| [docs/09-aws-cau-hinh-du-an.md](docs/09-aws-cau-hinh-du-an.md) | Cấu hình AWS EC2+S3 |
| [docs/11-rag-ollama-huong-dan.md](docs/11-rag-ollama-huong-dan.md) | Pipeline RAG Ollama |
| [DEMO.md](DEMO.md) | Chạy demo nhanh |

## Cấu trúc thư mục

```text
├── README.md
├── DEMO.md
├── docs/
├── data/pdfs/          # tài liệu học vụ / tuyển sinh
├── frontend/           # web chat
└── backend/            # FastAPI + RAG + ingest
```
