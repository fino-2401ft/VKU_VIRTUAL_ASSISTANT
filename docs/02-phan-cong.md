# Phân công nhóm (P1–P4)

> Role giữ cố định. Stack chính thức: **RAG tự build (Ollama) + AWS EC2/S3** — không dùng Bedrock.

| Role | Ký hiệu | Thành viên | Trách nhiệm chính | Phụ trách báo cáo |
|---|---|---|---|---|
| Architect / DevOps | **P1** | Quốc Anh | AWS account, IAM, EC2, S3, Budget, bảo mật SG, chi phí | Kiến trúc Cloud, so sánh self-host vs Bedrock, cost |
| Backend / Integration | **P2** | Quang Huy | FastAPI, API `/chat`, ingest pipeline, deploy app trên EC2 | API, data/vector store, sequence diagram |
| AI / Knowledge | **P3** | Văn Hội | Chuẩn hóa DOCX/PDF text, Ollama prompt, đánh giá độ chính xác RAG | RAG, tài liệu, bộ câu test |
| Frontend / BA / Docs | **P4** | Thùy Dương | Use case, UI chat, UAT, slide, video demo | Nghiệp vụ, HĐSD, kết quả UAT |

## Liên hệ & công cụ

| Hạng mục | Giá trị |
|---|---|
| Group chat | _Telegram / Zalo nhóm: …_ |
| Task board | _Google Sheet / Notion / GitHub Projects: …_ |
| GitHub repo | https://github.com/fino-2401ft/VKU_VIRTUAL_ASSISTANT |
| AWS Account (owner) | **P1** |
| Họp sync hàng tuần | _Ngày … lúc … (60–90 phút)_ |

## Quy ước làm việc

1. Mỗi PR nhỏ; merge `dev` trước, `main` bản ổn định.
2. Không mở scope ngoài `docs/01-MVP.md` nếu chưa thống nhất.
3. Thêm/sửa tài liệu → P3 chạy lại `python -m app.ingest` và ghi ngày vào `docs/04-pdf-checklist.md`.
4. EC2: **Stop** khi không demo để tiết kiệm credit.
