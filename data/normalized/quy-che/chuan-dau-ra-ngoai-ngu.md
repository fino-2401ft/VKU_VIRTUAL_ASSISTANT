# DỮ LIỆU CHUẨN HÓA AI RAG - THÔNG BÁO 4513/ĐHĐN-ĐT
**Cơ quan ban hành:** Đại học Đà Nẵng  
**Số văn bản:** 4513/ĐHĐN-ĐT  
**Trích yếu:** Kiểm tra trình độ tiếng Anh đầu vào, xếp lớp và xét miễn học phần tiếng Anh từ khóa 2014.

---

## BẢNG 1: QUY ĐỊNH XẾP LỚP TIẾNG ANH ĐẦU VÀO

### 1. Dạng Markdown Table (Đã phẳng hóa gộp ô)

| Kết quả kiểm tra (Thang điểm 100) | Đăng ký/Xếp vào lớp | Cấp độ cần đạt | Số tín chỉ | Quy định xét miễn & Học phần đăng ký |
| :--- | :--- | :---: | :---: | :--- |
| **0 - 34 điểm** | AV A1 | A1 | 5 | Học tiếng Anh dự bị. |
| **35 - 69 điểm** | AV A2.1 | A2 | 3 | Học học phần AV A2.1. |
| **70 - 84 điểm** | AV A2.2 | A2 | 4 | **Miễn học phần AV A2.1** và được nhận **điểm 10** cho học phần AV A2.1. |
| **85 - 100 điểm** | AV B1.1 | B1 | 7 | **Miễn các học phần AV A2.1 và AV A2.2**, nhận **điểm 10** cho các học phần này; Đăng ký học phần **AV B1.1 (tăng cường)**. |
| **85 - 100 điểm** | AV B1.2 | B1 | 7 | **Miễn các học phần AV A2.1 và AV A2.2**, nhận **điểm 10** cho các học phần này; Đăng ký học phần **AV B1.2 (tăng cường)**. |

---

### 2. Dạng Key-Value Chunks (Cho Vector Search & Semantic Matching)

```yaml
# Chunk 1: Tiếng Anh dự bị (A1)
document_id: "4513/ĐHĐN-ĐT"
category: "Xếp lớp Tiếng Anh đầu vào"
ket_qua_kiem_tra: "0 đến 34 điểm"
lop_duoc_xep: "AV A1"
cap_do_can_dat: "A1"
so_tin_chi: 5
quy_dinh_hoc_tap: "Sinh viên học tiếng Anh dự bị."

---
# Chunk 2: Tiếng Anh A2.1
document_id: "4513/ĐHĐN-ĐT"
category: "Xếp lớp Tiếng Anh đầu vào"
ket_qua_kiem_tra: "35 đến 69 điểm"
lop_duoc_xep: "AV A2.1"
cap_do_can_dat: "A2"
so_tin_chi: 3
quy_dinh_hoc_tap: "Sinh viên đăng ký và học học phần AV A2.1."

---
# Chunk 3: Tiếng Anh A2.2 & Miễn A2.1
document_id: "4513/ĐHĐN-ĐT"
category: "Xếp lớp Tiếng Anh đầu vào"
ket_qua_kiem_tra: "70 đến 84 điểm"
lop_duoc_xep: "AV A2.2"
cap_do_can_dat: "A2"
so_tin_chi: 4
quy_dinh_hoc_tap: "Được miễn học phần AV A2.1 và tự động nhận điểm 10 cho học phần AV A2.1. Sinh viên học học phần AV A2.2."

---
# Chunk 4: Tiếng Anh B1.1 (Miễn A2.1 & A2.2)
document_id: "4513/ĐHĐN-ĐT"
category: "Xếp lớp Tiếng Anh đầu vào"
ket_qua_kiem_tra: "85 đến 100 điểm"
lop_duoc_xep: "AV B1.1"
cap_do_can_dat: "B1"
so_tin_chi: 7
quy_dinh_hoc_tap: "Được miễn cả 2 học phần AV A2.1 và AV A2.2, được nhận điểm 10 cho 2 học phần này. Sinh viên đăng ký học học phần AV B1.1 (tăng cường)."

---
# Chunk 5: Tiếng Anh B1.2 (Miễn A2.1 & A2.2)
document_id: "4513/ĐHĐN-ĐT"
category: "Xếp lớp Tiếng Anh đầu vào"
ket_qua_kiem_tra: "85 đến 100 điểm"
lop_duoc_xep: "AV B1.2"
cap_do_can_dat: "B1"
so_tin_chi: 7
quy_dinh_hoc_tap: "Được miễn cả 2 học phần AV A2.1 và AV A2.2, được nhận điểm 10 cho 2 học phần này. Sinh viên đăng ký học học phần AV B1.2 (tăng cường)."
```

---

## BẢNG 2: PHỤ LỤC THAM CHIẾU CHỨNG CHỈ TIẾNG ANH QUỐC TẾ ĐỂ XÉT MIỄN

### 1. Dạng Markdown Table (Đã phẳng hóa gộp ô)

| KNLNN Việt Nam | Trình độ CEFR | IELTS | TOEFL PBT | TOEFL CBT | TOEFL iBT | TOEIC | Cambridge | Mức độ xét miễn học phần tại ĐH Đà Nẵng |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Bậc 6** | **C2** | $\ge 9.0$ | $\ge 600$ | $\ge 250$ | $\ge 100$ | $\ge 910$ | CPE | Được **miễn học, miễn thi chuẩn đầu ra B1** và **nhận điểm 10** tất cả các học phần tiếng Anh. |
| **Bậc 5** | **C1** | 7.0 / 6.5 / 6.0 | 577 / 550 | 233 / 213 | 95 / 80 | 905 / 850 | CAE | Được **miễn học, miễn thi chuẩn đầu ra B1** và **nhận điểm 10** tất cả các học phần tiếng Anh. |
| **Bậc 4** | **B2** | 5.5 / 5.0 | 527 / 500 | 197 / 173 | 71 / 61 | 845 / 600 | FCE | Được **miễn học, miễn thi chuẩn đầu ra B1** và **nhận điểm 10** tất cả các học phần tiếng Anh. |
| **Bậc 3** | **B1** | 4.5 / 4.0 | 477 / 450 | 153 / 133 | 53 / 45 | 595 / 450 | PET | Được **miễn học, miễn thi chuẩn đầu ra B1** và **nhận điểm 10** tất cả các học phần tiếng Anh. |
| **Bậc 2** | **A2** | 3.5 / 3.0 | < 450 | < 133 | < 45 | 445 / 400 | KET | Được **miễn học các học phần AV A2.1 và AV A2.2** và **nhận điểm 10** cho các học phần này. |
| **Bậc 1** | **A1** | < 3.0 | - | - | - | < 400 | - | **Không được xét miễn.** |

*Ghi chú chung:* Tất cả các chứng chỉ tiếng Anh quốc tế phải có giá trị trong vòng **24 tháng** tính từ ngày cấp đến ngày xét miễn.

---

### 2. Dạng Key-Value Chunks (Cho Vector Search & Semantic Matching)

```yaml
# Chunk 6: Quy định chung về chứng chỉ
document_id: "4513/ĐHĐN-ĐT"
category: "Quy định hạn dùng chứng chỉ"
thoi_han_hieu_luc: "24 tháng kể từ ngày cấp đến ngày xét miễn"
pham_vi_ap_dung: "Tất cả các loại chứng chỉ Tiếng Anh quốc tế (IELTS, TOEIC, TOEFL, Cambridge)"

---
# Chunk 7: Mức xét miễn Bậc 3 đến Bậc 6 (Miễn toàn bộ & nhận điểm 10)
document_id: "4513/ĐHĐN-ĐT"
category: "Quy đổi chứng chỉ quốc tế"
muc_xet_mien: "Được miễn học, miễn thi chuẩn đầu ra B1 và nhận điểm 10 tất cả các học phần tiếng Anh"
khung_nang_luc: ["Bậc 3", "Bậc 4", "Bậc 5", "Bậc 6", "B1", "B2", "C1", "C2"]
dieu_kien_ielts: "Từ 4.0 trở lên (4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 9.0)"
dieu_kien_toeic: "Từ 450 điểm trở lên (450, 595, 600, 845, 850, 905, 910)"
dieu_kien_toefl_ibt: "Từ 45 trở lên (45, 53, 61, 71, 80, 95, 100)"
dieu_kien_toefl_pbt: "Từ 450 trở lên (450, 477, 500, 527, 550, 577, 600)"
dieu_kien_toefl_cbt: "Từ 133 trở lên (133, 153, 173, 197, 213, 233, 250)"
dieu_kien_cambridge: ["PET", "FCE", "CAE", "CPE"]

---
# Chunk 8: Mức xét miễn Bậc 2 / A2 (Miễn học phần A2.1 và A2.2)
document_id: "4513/ĐHĐN-ĐT"
category: "Quy đổi chứng chỉ quốc tế"
muc_xet_mien: "Được miễn học các học phần AV A2.1 và AV A2.2 và nhận điểm 10 cho 2 học phần này"
khung_nang_luc: ["Bậc 2", "A2"]
dieu_kien_ielts: "3.0 hoặc 3.5"
dieu_kien_toeic: "400 đến 445 điểm"
dieu_kien_toefl_ibt: "Dưới 45 điểm (< 45)"
dieu_kien_toefl_pbt: "Dưới 450 điểm (< 450)"
dieu_kien_toefl_cbt: "Dưới 133 điểm (< 133)"
dieu_kien_cambridge: "KET"

---
# Chunk 9: Mức không được miễn (Bậc 1 / A1)
document_id: "4513/ĐHĐN-ĐT"
category: "Quy đổi chứng chỉ quốc tế"
muc_xet_mien: "Không được miễn học phần nào"
khung_nang_luc: ["Bậc 1", "A1"]
dieu_kien_ielts: "Dưới 3.0 (< 3.0)"
dieu_kien_toeic: "Dưới 400 điểm (< 400)"
```