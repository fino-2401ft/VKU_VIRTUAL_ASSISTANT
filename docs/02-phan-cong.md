# Phân công nhóm (P1–P4)

> Điền **họ tên** vào cột Thành viên. Role giữ cố định suốt dự án.

| Role                  | Ký hiệu | Thành viên (điền tên) | Trách nhiệm chính                                                        | Phụ trách tài liệu báo cáo                       |
| --------------------- | ------- | --------------------- | ------------------------------------------------------------------------ | ------------------------------------------------ |
| Architect / DevOps    | **P1**  | Quốc Anh              | AWS account, IAM, SAM/IaC, S3/CloudFront, CloudWatch, chi phí, bảo mật   | Kiến trúc Cloud, so sánh EC2 vs serverless, cost |
| Backend / Integration | **P2**  | Quang Huy             | API Gateway, Lambda, DynamoDB, contract `POST /chat`, nối Bedrock        | API, data model, sequence diagram                |
| AI / Knowledge        | **P3**  | Văn Hội               | Chuẩn hóa PDF, Bedrock Knowledge Base, prompt, bộ câu test, độ chính xác | RAG, PDF, đánh giá trả lời                       |
| Frontend / BA / Docs  | **P4**  | Thùy Dương            | Use case, UI chat, UAT, slide, video demo                                | Nghiệp vụ, HĐSD, kết quả UAT                     |

## Liên hệ & công cụ

| Hạng mục | Giá trị |
|---|---|
| Group chat | _Telegram / Zalo nhóm: …_ |
| Task board | _Google Sheet / Notion / GitHub Projects: …_ |
| GitHub repo | _URL: …_ |
| AWS Account (owner) | **P1** |
| Họp sync hàng tuần | _Ngày … lúc … (60–90 phút)_ |

## Quy ước làm việc

1. Mỗi người chỉ mở PR nhỏ; merge vào `dev` trước, `main` là bản ổn định.
2. Không thêm tính năng ngoài `docs/01-MVP.md` trừ khi cả nhóm đồng ý sau mốc M3.
3. Đổi PDF → P3 re-sync Knowledge Base và ghi ngày sync vào `docs/04-pdf-checklist.md`.
