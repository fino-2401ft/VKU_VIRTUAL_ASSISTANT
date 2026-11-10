# AWS Setup — Ngày 1 (RAG tự build)

Region: **`ap-southeast-1`**.  
Stack AI: **Ollama trên EC2** — **không** cấu hình Bedrock.

## A. Bảo mật root

1. MFA cho root  
2. Tạo IAM user `vku-assistant-admin` + MFA  
3. Dùng IAM user hàng ngày  

## B. Budget alert

1. Billing → Budgets  
2. Tạo budget **$15** và **$40** / tháng + email  
3. Screenshot → `docs/evidence/`

## C. Region

Console → **Asia Pacific (Singapore) ap-southeast-1**

## D. Chuẩn bị dịch vụ sẽ dùng

- [ ] S3 (lưu DOCX/PDF)  
- [ ] EC2 (chạy FastAPI + Ollama) — tạo sau khi local RAG ổn  
- [ ] Không cần Bedrock / OpenSearch Serverless  

## E. Việc tiếp

1. Local RAG OK (`DEMO.md`)  
2. Upload docs lên S3  
3. Deploy EC2 theo `docs/09-aws-cau-hinh-du-an.md`  
4. Stop EC2 khi không demo  

## Checklist

- [ ] MFA root + IAM  
- [ ] Budget $15/$40  
- [ ] Region `ap-southeast-1`  
- [ ] Evidence screenshots  
