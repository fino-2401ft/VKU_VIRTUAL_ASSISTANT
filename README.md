# VKU Virtual Assistant

Trợ lý ảo tra cứu **học vụ** và **tuyển sinh** VKU — triển khai mô hình Cloud Computing trên **AWS** (Serverless + Bedrock Knowledge Bases / RAG).

Môn: Điện toán đám mây · Nhóm 4 người

## Trạng thái hiện tại

**Có bản demo FE + BE local để báo cáo tiến độ** — xem [DEMO.md](DEMO.md).  
Tuần 1 tài liệu MVP đã chốt; AWS Bedrock sẽ nối sau.

### Chạy demo nhanh

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000

## Tài liệu nhanh

| File | Nội dung |
|---|---|
| [docs/01-MVP.md](docs/01-MVP.md) | Phạm vi CÓ / KHÔNG + 8 nhóm câu hỏi |
| [docs/02-phan-cong.md](docs/02-phan-cong.md) | Phân công P1–P4 |
| [docs/03-use-cases.md](docs/03-use-cases.md) | 8 use case |
| [docs/04-pdf-checklist.md](docs/04-pdf-checklist.md) | Checklist PDF |
| [docs/05-kien-truc.md](docs/05-kien-truc.md) | Sơ đồ kiến trúc AWS |
| [docs/06-tuan1-checklist.md](docs/06-tuan1-checklist.md) | Checklist Tuần 1 |
| [docs/07-bo-cau-hoi-test.md](docs/07-bo-cau-hoi-test.md) | 30 câu test |
| [Ke_hoach_thuc_hien_du_an_VKU_Virtual_Assistant.docx](Ke_hoach_thuc_hien_du_an_VKU_Virtual_Assistant.docx) | Kế hoạch 8 tuần (Word) |

## Việc làm tiếp theo (theo thứ tự)

1. **Cả nhóm:** Điền tên vào `docs/02-phan-cong.md`, tạo group chat.
2. **P3 + P4:** Copy PDF vào `data/pdfs/hoc-vu/` và `data/pdfs/tuyen-sinh/`, điền `docs/04-pdf-checklist.md`.
3. **P3 + P4:** Bổ sung đáp án mong đợi trong `docs/07-bo-cau-hoi-test.md` theo PDF thật.
4. **P1:** Làm `docs/08-aws-setup-ngay1.md` (MFA, IAM, Budget $5–10, region `ap-southeast-1`, mở Bedrock).
5. **P1 + P2:** Tạo GitHub repo, push code, nhánh `main` / `dev`.
6. **Hết Tuần 1 → Tuần 2:** Scaffold AWS SAM (`GET /health`).

## Kiến trúc (rút gọn)

```text
Web (S3 + CloudFront) → API Gateway → Lambda
   → Bedrock Knowledge Base (PDF trên S3)
   → DynamoDB (session / FAQ)
   → CloudWatch
```

## Cấu trúc thư mục

```text
├── README.md
├── docs/                 # Tài liệu dự án & evidence
├── data/pdfs/            # PDF local (học vụ / tuyển sinh)
├── frontend/             # (Tuần 5) Web chat
├── backend/              # (Tuần 2–4) Lambda / SAM
└── infra/                # (Tuần 2) Infrastructure as Code
```
