# Chạy demo — RAG tự build (Ollama)

## Kiến trúc

- **RAG tự build:** DOCX/PDF → chunk → embed (`nomic-embed-text`) → retrieve → LLM Ollama (`qwen2.5:3b`, tránh thinking của qwen3)
- **Fallback:** FAQ demo nếu chưa ingest / Ollama tắt
- **Cloud:** cùng stack lên **EC2 + S3** (credit $120)
- **Không dùng Bedrock**

Chi tiết: `docs/11-rag-ollama-huong-dan.md`

## 1. Ollama

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
ollama list
```

## 2. Ingest + web

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ingest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000  
Health: http://127.0.0.1:8000/api/health → `"rag_ready": true`

## Câu hỏi demo (đúng nguồn đang index)

Hiện vector store chủ yếu là **học phí** (`hoc-vu/hoc-phi/*.docx`):

1. Thời gian nộp học phí hè 2024-2025?  
2. Nộp học phí bằng QR hay chuyển khoản?  
3. Số tài khoản nộp học phí VKU?  
4. Thời tiết Đà Nẵng hôm nay? → không có trong tài liệu  

> Quy chế PDF chưa vào RAG nếu không extract được chữ — cần OCR/PDF text rồi ingest lại.

## Ghi chú báo cáo

> Nhóm tự xây pipeline RAG (ingest–retrieve–generate) với mô hình open-source qua Ollama; triển khai trên AWS EC2 và lưu tài liệu trên S3. Không sử dụng Amazon Bedrock.
