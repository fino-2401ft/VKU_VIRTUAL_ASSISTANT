# Use case MVP (08 kịch bản)

Actor chính: **Sinh viên / Thí sinh / Khách** dùng Web chat.

## UC01 — Hỏi học phí / miễn giảm (Q1)

- **Tác nhân:** Sinh viên / thí sinh
- **Tiền điều kiện:** PDF học vụ đã có trong Knowledge Base
- **Luồng chính:**
  1. User mở web chat
  2. Gõ: “Học phí một tín chỉ là bao nhiêu?” / “Có miễn giảm học phí không?”
  3. Hệ thống retrieve đoạn PDF liên quan → sinh câu trả lời
  4. Hiển thị câu trả lời + nguồn PDF
- **Ngoại lệ:** Không tìm thấy → fallback gợi ý câu hỏi khác

## UC02 — Hỏi quy chế đào tạo / tốt nghiệp (Q2)

- **Ví dụ hỏi:** “Điều kiện xét tốt nghiệp là gì?”
- **Kết quả mong đợi:** Tóm tắt điều kiện theo đúng quy chế trong PDF, kèm nguồn

## UC03 — Hỏi quy định thi / đánh giá (Q3)

- **Ví dụ hỏi:** “Thi lại được quy định thế nào?” / “Điểm danh ảnh hưởng gì?”
- **Kết quả mong đợi:** Trả lời đúng mục trong quy chế; không bịa thêm

## UC04 — Hỏi học bổng / chế độ (Q4)

- **Ví dụ hỏi:** “Điều kiện xét học bổng khuyến khích học tập?”
- **Kết quả mong đợi:** Liệt kê điều kiện chính theo tài liệu

## UC05 — Hỏi danh sách ngành tuyển sinh (Q5)

- **Ví dụ hỏi:** “VKU tuyển những ngành nào năm nay?”
- **Kết quả mong đợi:** Liệt kê ngành / nhóm ngành theo PDF tuyển sinh

## UC06 — Hỏi phương thức & hồ sơ xét tuyển (Q6)

- **Ví dụ hỏi:** “Xét học bạ cần những giấy tờ gì?”
- **Kết quả mong đợi:** Các phương thức + thành phần hồ sơ theo tài liệu

## UC07 — Hỏi thời gian / chỉ tiêu / hạn nộp (Q7)

- **Ví dụ hỏi:** “Hạn nộp hồ sơ đợt 1 là khi nào?”
- **Kết quả mong đợi:** Mốc thời gian / chỉ tiêu nếu có trong PDF; nếu PDF cũ phải ghi rõ theo tài liệu đang dùng

## UC08 — FAQ chung + câu ngoài phạm vi (Q8)

- **Ví dụ hỏi trong phạm vi:** “Địa chỉ VKU?” / “Liên hệ phòng Đào tạo?”
- **Ví dụ ngoài phạm vi:** “Thời tiết Đà Nẵng hôm nay?” / “Điểm của tôi là bao nhiêu?”
- **Kết quả mong đợi:**
  - Trong phạm vi → trả lời từ FAQ/PDF
  - Ngoài phạm vi → “Hiện không có trong tài liệu học vụ/tuyển sinh VKU…” + gợi ý 2–3 câu hỏi mẫu

## User flow tổng quát

```text
[Mở Web] → [Gõ câu hỏi / bấm gợi ý] → [API POST /chat]
       → [Bedrock KB retrieve + generate]
       → [Hiển thị answer + sources]
       → [Tiếp tục hỏi trong cùng session]
```
