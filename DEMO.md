# Chạy demo nhanh (báo cáo tiến độ)

Bản **local FE + BE** — chưa cần AWS. Dùng FAQ demo theo 8 nhóm câu hỏi MVP.

## Yêu cầu

- Python 3.10+

## Chạy

```powershell
cd "C:\Users\HP VICTUS\Documents\VKU_Subjects\HK7\CloudComputing\VKU_Virtual_Assistant\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở trình duyệt: **http://127.0.0.1:8000**

## API

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/suggestions` | Câu hỏi gợi ý |
| POST | `/api/chat` | `{ "message": "...", "session_id": null }` |

## Câu demo nên hỏi khi báo cáo

1. Học phí một tín chỉ bao nhiêu?
2. Điều kiện tốt nghiệp là gì?
3. VKU tuyển những ngành nào?
4. Địa chỉ VKU ở đâu?
5. Thời tiết Đà Nẵng hôm nay? → fallback ngoài phạm vi

## Ghi chú bảo vệ / báo cáo tiến độ

- Đây là **MVP local** (keyword FAQ), chứng minh giao diện + luồng chat + phân nhóm câu hỏi.
- Roadmap Cloud: thay `knowledge.py` bằng gọi **Bedrock Knowledge Bases** + PDF trên S3; FE host CloudFront.
