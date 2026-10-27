# Checklist tài liệu PDF

Đặt file thật vào:

- `data/pdfs/hoc-vu/`
- `data/pdfs/tuyen-sinh/`

> File PDF **không** commit lên Git nếu dung lượng lớn / có nội dung nội bộ — chỉ giữ danh sách ở đây; bản dùng cho AWS upload lên S3.

## Quy tắc đặt tên

`loai-noi-dung-nam.pdf` — ví dụ: `quy-che-dao-tao-2024.pdf`, `de-an-tuyen-sinh-2025.pdf`

## Danh sách PDF học vụ (`hoc-vu/`)

| # | Tên file (sau khi đổi tên) | Năm | Copy được chữ? (Có/Không) | Phủ câu hỏi | Đã upload S3? | Đã sync KB? | Ngày sync | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | Q1–Q4 | ☐ | ☐ | | |
| 2 | | | | | ☐ | ☐ | | |
| 3 | | | | | ☐ | ☐ | | |

## Danh sách PDF tuyển sinh (`tuyen-sinh/`)

| # | Tên file (sau khi đổi tên) | Năm | Copy được chữ? (Có/Không) | Phủ câu hỏi | Đã upload S3? | Đã sync KB? | Ngày sync | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | Q5–Q7 | ☐ | ☐ | | |
| 2 | | | | | ☐ | ☐ | | |
| 3 | | | | | ☐ | ☐ | | |

## Kiểm tra nhanh mỗi file

1. Mở PDF → bôi đen 1 đoạn → Copy → Paste Notepad được không?
2. Nếu **Không** (scan ảnh): ưu tiên tìm bản text; nếu buộc dùng thì ghi rủi ro OCR vào cột Ghi chú.
3. Bỏ file trùng / hết hiệu lực khỏi KB (giữ trong thư mục `archive/` local nếu cần).

## Mapping PDF → nhóm câu hỏi

| Nhóm | Cần có trong PDF |
|---|---|
| Q1 Học phí | Mức học phí, miễn giảm |
| Q2 Quy chế / TN | Điều kiện tốt nghiệp, chương trình đào tạo |
| Q3 Thi | Thi lại, đánh giá điểm |
| Q4 Học bổng | Điều kiện, mức xét |
| Q5 Ngành TS | Danh mục ngành |
| Q6 Hồ sơ / phương thức | Phương thức xét, giấy tờ |
| Q7 Thời gian TS | Lịch, hạn nộp, chỉ tiêu |
| Q8 FAQ | Địa chỉ, liên hệ (hoặc seed DynamoDB) |
