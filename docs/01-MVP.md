# Phạm vi MVP — VKU Virtual Assistant

> Đã chốt: **tự build RAG AI** (Ollama + vector store) triển khai trên **AWS EC2 + S3**.  
> **Không dùng Amazon Bedrock.**

## 1. Mục tiêu MVP

Xây trợ lý ảo web chat giúp sinh viên / thí sinh tra cứu thông tin **học vụ** và **tuyển sinh** VKU từ tài liệu DOCX/PDF, theo mô hình Cloud Computing trên AWS (IaaS + lưu trữ S3).

## 2. CÓ làm trong MVP

| # | Hạng mục | Mô tả |
|---|---|---|
| 1 | Web chat | Giao diện hỏi–đáp trên trình duyệt |
| 2 | RAG tự build | Ingest tài liệu → chunk → embedding → retrieve → LLM sinh trả lời |
| 3 | LLM / Embed | Ollama open-source (`qwen3:4b`, `nomic-embed-text`) |
| 4 | Vector store | Local file store (deploy cùng app trên EC2) |
| 5 | Tài liệu | DOCX/PDF trong `data/pdfs` (sau này sync từ S3) |
| 6 | Backend API | FastAPI `POST /api/chat` |
| 7 | Cloud AWS | EC2 chạy app + Ollama; S3 lưu tài liệu; (tuỳ chọn) CloudFront cho FE |
| 8 | Nguồn trích dẫn | Hiển thị file nguồn khi trả lời |
| 9 | Vận hành | Budget alert, tắt EC2 khi không dùng, bảng chi phí |

## 3. KHÔNG làm trong MVP

- Amazon Bedrock / Bedrock Knowledge Bases
- Fine-tune / train LLM từ đầu
- Zalo / Facebook / app mobile
- Đăng nhập hệ thống điểm thật của trường
- Admin CMS phức tạp

## 4. Tám nhóm câu hỏi ưu tiên

| ID | Nhóm | Ví dụ | Nguồn |
|---|---|---|---|
| Q1 | Học phí | “Học phí hè 2024-2025?” | `hoc-vu/hoc-phi` |
| Q2 | Quy chế đào tạo | “Điều kiện tốt nghiệp?” | `hoc-vu/quy-che` (cần PDF text/OCR) |
| Q3 | Thi / đánh giá | “Thi lại thế nào?” | quy chế |
| Q4 | Học bổng | “Điều kiện học bổng?” | học vụ |
| Q5–Q7 | Tuyển sinh | ngành / hồ sơ / lịch | `tuyen-sinh/` |
| Q8 | FAQ chung | địa chỉ / liên hệ | FAQ hoặc tài liệu |

## 5. Definition of Done

- [ ] Web chat hỏi–đáp tiếng Việt từ tài liệu đã ingest
- [ ] `/api/health` → `rag_ready: true`
- [ ] Có `sources` (đường dẫn file)
- [ ] Câu ngoài tài liệu → fallback rõ ràng
- [ ] Deploy được trên EC2 (demo) + có ước tính chi phí AWS

## 6. Stack đã chọn

- **AI:** RAG tự build + Ollama (không Bedrock)
- **Backend:** FastAPI (Python)
- **Frontend:** HTML/CSS/JS
- **AWS:** EC2 + S3 (+ CloudWatch / Budgets)
- **Region:** `ap-southeast-1`
