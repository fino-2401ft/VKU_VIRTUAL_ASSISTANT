# Phạm vi MVP — VKU Virtual Assistant

> Đã chốt để nhóm 4 người triển khai trên AWS (Serverless + Bedrock Knowledge Bases / RAG).
> Mọi tính năng ngoài danh sách **CÓ** phải chờ sau mốc M3 (web E2E chạy được).

## 1. Mục tiêu MVP

Xây trợ lý ảo web chat giúp sinh viên / thí sinh tra cứu thông tin **học vụ** và **tuyển sinh** VKU từ tài liệu PDF, triển khai theo mô hình Cloud Computing trên AWS.

## 2. CÓ làm trong MVP

| # | Hạng mục | Mô tả |
|---|---|---|
| 1 | Web chat | Giao diện hỏi–đáp trên trình duyệt |
| 2 | Host frontend | Amazon S3 + CloudFront (HTTPS) |
| 3 | API | Amazon API Gateway + AWS Lambda |
| 4 | Tri thức PDF | Upload PDF → S3 → Amazon Bedrock Knowledge Bases (RAG) |
| 5 | Session / FAQ nóng | Amazon DynamoDB |
| 6 | 8 nhóm câu hỏi | Xem mục 4 bên dưới |
| 7 | Nguồn trích dẫn | Hiển thị file/đoạn PDF liên quan (nếu có) |
| 8 | Vận hành Cloud | CloudWatch logs/dashboard/alarm + bảng chi phí |
| 9 | IaC | AWS SAM (hoặc CDK) |

## 3. KHÔNG làm trong MVP (phase sau)

- Zalo / Facebook Messenger / app mobile native
- Đăng nhập hệ thống điểm / học vụ thật của trường
- Fine-tune / train lại model trên PDF
- Admin CMS phức tạp
- Đa ngôn ngữ (chỉ tiếng Việt)
- Multi-region / high availability nâng cao

## 4. Tám nhóm câu hỏi ưu tiên (đã khóa)

| ID | Nhóm câu hỏi | Ví dụ người dùng hỏi | Nguồn dữ liệu |
|---|---|---|---|
| Q1 | Học phí / miễn giảm | “Học phí ngành KTPM bao nhiêu?” | PDF học vụ |
| Q2 | Quy chế đào tạo | “Điều kiện tốt nghiệp là gì?” | PDF học vụ |
| Q3 | Thi / đánh giá | “Quy định thi lại như thế nào?” | PDF học vụ |
| Q4 | Học bổng / chế độ | “Điều kiện xét học bổng?” | PDF học vụ |
| Q5 | Ngành tuyển sinh | “VKU tuyển những ngành nào?” | PDF tuyển sinh |
| Q6 | Phương thức & hồ sơ TS | “Xét tuyển học bạ cần giấy tờ gì?” | PDF tuyển sinh |
| Q7 | Thời gian / chỉ tiêu TS | “Hạn nộp hồ sơ đợt 1?” | PDF tuyển sinh |
| Q8 | FAQ chung | “Địa chỉ / liên hệ phòng đào tạo?” | PDF hoặc FAQ DynamoDB |

## 5. Tiêu chí chấp nhận MVP (Definition of Done)

- [ ] User mở URL CloudFront, gửi câu hỏi, nhận câu trả lời tiếng Việt
- [ ] Ít nhất **5/8** nhóm câu hỏi trả lời đúng trên bộ test nội bộ
- [ ] Câu ngoài tài liệu → trả lời fallback (“Không tìm thấy trong tài liệu…”)
- [ ] Có `sources` (tên PDF) khi trả lời từ Knowledge Base
- [ ] Có screenshot CloudWatch + ước tính chi phí AWS trong báo cáo

## 6. Stack đã chọn

- **Region:** `ap-southeast-1` (Singapore) — ưu tiên gần VN
- **AI:** Amazon Bedrock Knowledge Bases (RAG), không fine-tune
- **Frontend:** Web đơn giản (HTML/JS hoặc React)
- **IaC:** AWS SAM
