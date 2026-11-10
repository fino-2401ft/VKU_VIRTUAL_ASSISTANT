# [KHÔNG DÙNG] Hướng dẫn Amazon Bedrock (lưu trữ / so sánh báo cáo)

> **Dự án đã chốt RAG tự build (Ollama + EC2).** File này chỉ giữ để đối chiếu khi viết báo cáo.  
> Làm theo `docs/11-rag-ollama-huong-dan.md` và `docs/09-aws-cau-hinh-du-an.md`.

~~Hướng dẫn cấu hình Amazon Bedrock (từng bước)~~

Dành cho tham khảo — RAG trên tài liệu học vụ/tuyển sinh qua Bedrock (phương án đã bỏ).

---

## Bước 0 — Chuẩn bị (5 phút)

- [ ] Đăng nhập bằng **IAM user** (không dùng root hàng ngày)
- [ ] Region góc phải: ưu tiên **`ap-southeast-1` (Singapore)**  
      Nếu thiếu model → dùng **`us-east-1`** và ghi vào báo cáo
- [ ] Đã có Budget alert ($15 / $40)
- [ ] Chọn sẵn **3–5 file** học phí mới nhất (2025–2027), ưu tiên PDF; DOCX dùng được nếu KB nhận, nếu sync lỗi thì convert PDF

Ghi lại region bạn chọn: `________________`

---

## Bước 1 — Bật Model access (10–15 phút)

1. AWS Console → tìm **Amazon Bedrock** → Enter  
2. Menu trái → **Model access** (hoặc **Model catalog** → xin quyền)  
3. Enable các model sau:

### Bắt buộc

| Vai trò | Model chọn trên UI | Ghi chú |
|---|---|---|
| Embedding (Knowledge Base) | **Cohere Embed Multilingual** (`cohere.embed-multilingual-v3`) | Tài liệu tiếng Việt |
| Chat / trả lời | **Amazon Nova Lite** *hoặc* **Claude Haiku** | Rẻ, đủ Q&A |

### Không cần bật lúc này

- Claude Opus / Sonnet lớn  
- Embed English  
- Multimodal (ảnh/video)

4. Đợi status = **Access granted** / Available  
5. Screenshot → `docs/evidence/bedrock-model-access.png`

Nếu **không thấy** Cohere Multilingual ở Singapore: đổi region `us-east-1`, làm lại Bước 1.

---

## Bước 2 — Tạo S3 chứa tài liệu (10 phút)

1. Vào **S3** → **Create bucket**  
2. Đặt tên (unique): `vku-assistant-docs-<tênviếtliền>-dev`  
   Ví dụ: `vku-assistant-docs-fino2401-dev`  
3. Region: **cùng region** với Bedrock  
4. **Block all public access** = ON  
5. Encryption: SSE-S3  
6. Versioning: Enable (khuyến nghị)  
7. Tag: `Project=vku-virtual-assistant`, `Env=dev`  
8. Create bucket  

### Tạo thư mục & upload

1. Vào bucket → **Create folder**: `hoc-vu/hoc-phi/`  
2. (Tuỳ chọn) `tuyen-sinh/`  
3. Upload **3–5 file** mới nhất vào `hoc-vu/hoc-phi/`  
4. Không public object  

Screenshot: `docs/evidence/s3-docs.png`

---

## Bước 3 — Tạo IAM role cho Knowledge Base (thường AWS tự tạo)

Khi tạo KB, chọn **Create and use a new service role** — để Bedrock tự gắn quyền đọc S3 + ghi vector store.

Nếu tự tạo role sau này, cần quyền tối thiểu: đọc bucket docs, gọi embedding model, dùng vector store.

---

## Bước 4 — Tạo Bedrock Knowledge Base (20–40 phút)

1. Bedrock → **Knowledge bases** → **Create**  
2. Chọn kiểu có **vector store** (Create knowledge base with vector store)  
3. Name: `vku-assistant-kb`  
4. IAM role: **Create and use a new service role**  
5. Next  

### Data source

1. Data source type: **Amazon S3**  
2. Name: `vku-docs-s3`  
3. S3 URI: chọn bucket vừa tạo, browse tới prefix `hoc-vu/` (hoặc cả bucket nếu chỉ chứa docs dự án)  
4. Parsing / chunking: **Default** lần đầu (đừng chỉnh phức tạp)  
5. Next  

### Embeddings model

1. Chọn **Cohere Embed Multilingual**  
2. Embeddings type: **floating-point**  
3. Dimensions: để mặc định (thường 1024)  
4. **Quan trọng:** sau khi tạo **không đổi được** embedding model  

### Vector store

1. Chọn option AWS đề xuất — thường **Quick create a new vector store** (OpenSearch Serverless)  
2. Chỉ tạo **1** KB — đừng tạo nhiều (tốn credit)  
3. Create  

Đợi status Knowledge Base = **Available** / Ready.

Ghi lại:

```text
Knowledge Base ID: ________________
Data source ID:    ________________
Region:            ________________
Embedding model:   cohere.embed-multilingual-v3
```

---

## Bước 5 — Sync dữ liệu & test trên Console (15 phút)

1. Vào KB `vku-assistant-kb` → tab **Data source**  
2. Chọn data source → **Sync**  
3. Đợi Sync status = **Complete** (có thể vài phút)  
4. Nếu **Failed**:
   - File scan/ảnh không có text → đổi PDF text  
   - DOCX không hỗ trợ → convert PDF upload lại → Sync lại  
   - Sai region / sai quyền S3 → kiểm tra role  

### Test hỏi đáp

Trong KB có **Test** / **Explore** (hoặc Bedrock Chat với Knowledge Base):

Chọn **generation model**: Nova Lite hoặc Claude Haiku  

Thử các câu:

1. `Học phí học kỳ 1 năm 2025-2026 đóng như thế nào?`  
2. `Thời gian thu học phí là khi nào?`  
3. `Địa chỉ nộp học phí?` (nếu có trong file)  
4. `Thời tiết Đà Nẵng hôm nay?` → kỳ vọng: không có trong tài liệu / từ chối bịa  

Pass khi: trả lời **bám nội dung file**, có **citation/nguồn** (nếu UI hiện).

Screenshot: `docs/evidence/bedrock-kb-test.png`

---

## Bước 6 — (Sau khi test OK) Nối vào ứng dụng

Khi Bước 5 ổn, làm tiếp (có thể nhờ AI scaffold code):

1. Lambda Python gọi Bedrock **RetrieveAndGenerate** với `knowledgeBaseId` + model ARN  
2. API Gateway `POST /chat`  
3. Sửa frontend trỏ URL API  
4. Host FE bằng S3 + CloudFront  

Local FAQ demo hiện tại chỉ dùng tạm; production = Bedrock KB.

---

## Checklist hoàn thành cấu hình Bedrock

- [ ] Model access: Cohere Embed Multilingual + Nova Lite/Haiku  
- [ ] S3 docs private + 3–5 file đã upload  
- [ ] KB `vku-assistant-kb` Available  
- [ ] Sync Complete  
- [ ] Test Console trả lời đúng ít nhất 2/3 câu học phí  
- [ ] Đã ghi KB ID / region / model  
- [ ] Evidence screenshots trong `docs/evidence/`  

---

## Chi phí — việc nên / không nên

**Nên**
- Ít file lúc đầu, ít lần Sync  
- Tắt/không để test chat liên tục hàng giờ  
- Budget alert đã bật  

**Không nên**
- Tạo nhiều OpenSearch Serverless / nhiều KB  
- Bật Claude Opus  
- Upload cả chục file cũ rồi sync đi sync lại  

---

## Gặp lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| Không thấy model | Đổi region / Enable model access chờ vài phút |
| Sync failed | Đổi PDF text, kiểm tra prefix S3, quyền role |
| Trả lời lung tung | Hỏi đúng nội dung có trong file; thêm file liên quan; chỉnh prompt sau khi có API |
| Sợ cháy tiền | Stop test; xem Cost Explorer; chỉ giữ 1 KB |

---

## Xong Bước 5 thì gửi lại

1. Region đang dùng  
2. KB ID  
3. Model chat đã chọn (Nova Lite / Haiku)  
4. 1 câu test thành công / thất bại  

→ Tiếp theo sẽ làm Lambda + API Gateway nối Bedrock vào web chat.
