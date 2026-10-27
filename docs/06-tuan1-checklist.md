# Checklist Tuần 1 — Khởi động

Đánh dấu `[x]` khi xong. Mục tiêu cuối tuần: **MVP đã chốt + AWS + repo + PDF list + 30 câu test**.

## A. Chốt MVP (Bước 1) — ưu tiên hôm nay

- [x] Tài liệu MVP (`docs/01-MVP.md`) — CÓ / KHÔNG / 8 câu hỏi
- [x] Use case (`docs/03-use-cases.md`)
- [x] Sơ đồ kiến trúc (`docs/05-kien-truc.md`)
- [ ] Điền tên P1–P4 vào `docs/02-phan-cong.md`
- [ ] Tạo group chat + link task board
- [ ] Cả nhóm đọc và “đồng ý MVP” (không mở scope)

## B. Tài liệu PDF

- [ ] Copy PDF vào `data/pdfs/hoc-vu/` và `data/pdfs/tuyen-sinh/`
- [ ] Đổi tên file theo quy ước
- [ ] Điền `docs/04-pdf-checklist.md` (copy được chữ? phủ Q1–Q8?)
- [ ] Loại PDF scan mờ / trùng nếu có thể

## C. Bộ câu hỏi test (30 câu)

- [ ] Hoàn thành `docs/07-bo-cau-hoi-test.md` (P3 + P4)
- [ ] Mỗi nhóm Q1–Q8 có ít nhất 3 câu
- [ ] Có cột đáp án mong đợi / file PDF nguồn

## D. Hạ tầng khởi tạo

- [x] P1 tạo AWS account / Educate / Free Tier *(đã đăng ký Gmail)*
- [ ] Làm hết checklist `docs/08-aws-setup-ngay1.md` (MFA, IAM user, Budget, region, Bedrock)
- [ ] Bật Billing alert 5–10 USD
- [ ] Chọn region `ap-southeast-1`
- [ ] Tạo GitHub repo, nhánh `main` / `dev`
- [ ] Push codebase hiện tại lên remote
- [ ] Mọi thành viên clone được repo + có quyền AWS (ít nhất read)

## E. Bằng chứng cho báo cáo (`docs/evidence/`)

- [ ] Screenshot sơ đồ kiến trúc
- [ ] Screenshot billing alert
- [ ] Ảnh danh sách PDF đã chuẩn hóa

## Kết thúc Tuần 1 → làm gì tuần 2?

Bắt đầu **skeleton AWS SAM**: S3 + DynamoDB + Lambda `GET /health` + API Gateway.
