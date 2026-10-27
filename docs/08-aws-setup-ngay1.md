# AWS Setup — Ngày 1 (sau khi đăng ký)

Làm **theo đúng thứ tự**. Chưa tạo EC2 / Bedrock / Lambda cho đến khi xong mục A–D.

Region mặc định dự án: **Asia Pacific (Singapore) `ap-southeast-1`**.

---

## A. Bảo mật tài khoản root (10 phút)

1. Đăng nhập [AWS Console](https://console.aws.amazon.com/) bằng email vừa đăng ký.
2. Click tên account (góc trên phải) → **Security credentials**.
3. Bật **MFA** cho root (Authenticator app trên điện thoại) — bắt buộc với đồ án.
4. **Không** dùng root để làm hàng ngày. Tạo user IAM:
   - Vào **IAM** → **Users** → **Create user**
   - Tên gợi ý: `vku-assistant-admin`
   - Access: **AWS Console access**
   - Attach policy tạm (học tập): `AdministratorAccess` *(sau này thu hẹp)*
   - Bật MFA cho user này luôn
5. Đăng xuất root → đăng nhập lại bằng user IAM vừa tạo.

## B. Cảnh báo chi phí — Billing alert (10 phút)

1. Đăng nhập bằng **root** một lần (chỉ để bật billing):
   - **Billing and Cost Management** → **Billing preferences**
   - Bật **Receive Billing Alerts** (nếu thấy)
2. Vào **CloudWatch** (region `us-east-1` thường dùng cho billing metric) **hoặc** dùng **AWS Budgets** (dễ hơn):
   - **Billing** → **Budgets** → **Create budget**
   - Template: **Zero spend budget** hoặc **Monthly cost budget**
   - Amount: **5 USD** (hoặc 10 USD)
   - Email nhận cảnh báo: Gmail của nhóm / P1
3. Chụp screenshot budget → lưu `docs/evidence/billing-alert.png`

> Đồ án Bedrock có thể tốn tiền nhanh nếu test nhiều. Budget $5–10 là an toàn.

## C. Chọn region làm việc

1. Góc trên phải Console → chọn **Asia Pacific (Singapore) ap-southeast-1**.
2. Mọi resource (S3, Lambda, API Gateway, DynamoDB, Bedrock KB…) tạo ở region này.
3. Ghi vào README / phân công: region = `ap-southeast-1`.

## D. Kiểm tra Bedrock có dùng được không (5 phút)

1. Vẫn ở `ap-southeast-1` → tìm **Amazon Bedrock**.
2. Vào **Model access** / **Model catalog** → xin quyền dùng model (ví dụ Claude hoặc Titan Embeddings — tùy console hiện tại).
3. Nếu region chưa có model cần dùng: ghi lại; nhóm có thể cân nhắc `us-east-1` cho Bedrock **nhưng** ưu tiên Singapore trước.
4. **Chưa** tạo Knowledge Base hôm nay nếu chưa có PDF lên S3.

## E. Việc làm ngay sau setup (cùng ngày / hôm sau)

| # | Việc | Ai |
|---|---|---|
| 1 | Điền tên P1–P4 trong `docs/02-phan-cong.md` | Cả nhóm |
| 2 | Copy PDF vào `data/pdfs/...` + checklist | P3 + P4 |
| 3 | Tạo GitHub repo, push project | P1 + P2 |
| 4 | (Tuần 2) Scaffold SAM: S3 + DynamoDB + `/health` | P1 + P2 |

## F. Những thứ CHƯA làm hôm nay

- Không bật EC2 “cho vui”
- Không để Access Key của root
- Không mở Security Group `0.0.0.0/0` cho SSH
- Không upload hết PDF lên S3 public

## Checklist tick nhanh

- [ ] MFA root
- [ ] User IAM + MFA
- [ ] Budget / billing alert $5–10 + email
- [ ] Region = `ap-southeast-1`
- [ ] Đã mở thử Bedrock console
- [ ] Screenshot evidence trong `docs/evidence/`
