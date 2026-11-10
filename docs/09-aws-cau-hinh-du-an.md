# Cấu hình dự án trên AWS — RAG tự build (EC2 + S3)

> **Không dùng Bedrock.** AI chạy bằng Ollama trên EC2; tài liệu trên S3.  
> Credit $120 dùng trả EC2/EBS/S3.

## Pha A — Khóa tài khoản (bắt buộc)

1. MFA root + IAM user làm việc hàng ngày  
2. Budget alert **$15** và **$40**  
3. Region: `ap-southeast-1`  
4. Screenshot evidence → `docs/evidence/`

## Pha B — S3 tài liệu

1. Tạo bucket: `vku-assistant-docs-team1-dev` (hoặc tên unique của nhóm)  
2. Block all public access = ON  
3. Upload DOCX/PDF text vào:
   - `hoc-vu/hoc-phi/`
   - `hoc-vu/quy-che/` (chỉ file extract được chữ)
   - `tuyen-sinh/`
4. Tag: `Project=vku-virtual-assistant`

## Pha C — EC2 chạy RAG + Ollama

1. Launch EC2 Ubuntu, gợi ý: **t3.large** hoặc **t3.xlarge** (RAM ≥ 8GB)  
2. Security Group:
   - SSH 22 từ IP của bạn  
   - HTTP 80 (hoặc 8000) từ IP demo  
   - **Không** mở public port Ollama `11434`
3. Cài đặt trên EC2:

```bash
# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b
ollama pull nomic-embed-text

# App
sudo apt update && sudo apt install -y python3-venv git
git clone <repo-url> VKU_VIRTUAL_ASSISTANT
cd VKU_VIRTUAL_ASSISTANT/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# sync docs từ S3 vào ../data/pdfs rồi:
python -m app.ingest
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. Demo: `http://<EC2-public-IP>:8000`  
5. **Stop instance** khi không dùng (tiết kiệm credit)

## Pha D — Frontend & vận hành

- FE có thể serve sẵn qua FastAPI (như hiện tại)  
- (Tuỳ chọn) tách FE lên S3 + CloudFront  
- CloudWatch: theo dõi CPU/EC2  
- Cost Explorer: lọc EC2 + EBS + S3  

## Checklist

- [ ] MFA + Budget  
- [ ] S3 docs private + đã upload  
- [ ] EC2 chạy Ollama + ingest + web  
- [ ] `/api/health` → `rag_ready: true` trên EC2  
- [ ] Stop EC2 sau demo  

## Tài liệu liên quan

- Local RAG: `docs/11-rag-ollama-huong-dan.md`  
- Bedrock (không dùng): `docs/10-bedrock-huong-dan-cau-hinh.md` — chỉ giữ để so sánh báo cáo  
