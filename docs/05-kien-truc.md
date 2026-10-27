# Sơ đồ kiến trúc AWS (MVP)

## Sơ đồ logic

```text
┌─────────────────────────────────────────────────────────────┐
│                     Người dùng (Browser)                     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Amazon CloudFront + S3 (Frontend)               │
│                     Web Chat UI                              │
└────────────────────────────┬────────────────────────────────┘
                             │ POST /chat
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Amazon API Gateway                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS Lambda (chat)                       │
│         - nhận message, sessionId                            │
│         - gọi Bedrock RetrieveAndGenerate                    │
│         - lưu session vào DynamoDB                           │
│         - fallback FAQ nếu cần                               │
└───────┬─────────────────────┬─────────────────┬─────────────┘
        │                     │                 │
        ▼                     ▼                 ▼
┌───────────────┐   ┌──────────────────┐   ┌────────────┐
│ Bedrock       │   │ DynamoDB         │   │ CloudWatch │
│ Knowledge Base│   │ Sessions + FAQ   │   │ Logs/Alarm │
└───────┬───────┘   └──────────────────┘   └────────────┘
        │ ingest
        ▼
┌───────────────┐
│  Amazon S3    │
│  PDF học vụ / │
│  tuyển sinh   │
└───────────────┘
```

## Thành phần & trách nhiệm

| Dịch vụ | Việc | Ai setup |
|---|---|---|
| S3 (docs) | Lưu PDF nguồn | P1 + P3 |
| Bedrock Knowledge Base | Chunk + embedding + retrieve | P3 + P1 |
| Lambda + API Gateway | API chat | P2 |
| DynamoDB | Session, FAQ nóng | P2 |
| S3 + CloudFront | Host UI | P1 + P4 |
| CloudWatch + Budgets | Giám sát, chi phí | P1 |
| IAM | Least privilege | P1 |

## Region & bảo mật (mặc định)

- Region: `ap-southeast-1`
- S3 docs: Block Public Access = ON
- Frontend: chỉ public qua CloudFront
- API: HTTPS; (tuỳ chọn sau) Cognito
- Billing alert: 5–10 USD

## So sánh sẽ viết trong báo cáo (Tuần 6)

| Tiêu chí | EC2 monolith | Serverless (MVP này) |
|---|---|---|
| Vận hành | Tự patch, scale tay | Managed |
| Chi phí lúc ít user | Trả cả khi idle | Trả theo request |
| Triển khai | Máy ảo | SAM + managed services |
| Phù hợp môn Cloud | Có | Có — nhấn mạnh PaaS/serverless |
