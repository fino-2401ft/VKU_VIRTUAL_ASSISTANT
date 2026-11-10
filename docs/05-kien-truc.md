# Sơ đồ kiến trúc AWS (MVP) — RAG tự build

> **Chính thức:** Self-hosted RAG (Ollama) trên EC2 + tài liệu S3.  
> **Không dùng** Amazon Bedrock.

## Sơ đồ logic

```text
┌─────────────────────────────────────────┐
│         Người dùng (Web Chat)           │
└──────────────────┬──────────────────────┘
                   │ HTTPS / HTTP
                   ▼
┌─────────────────────────────────────────┐
│  Frontend (static)                      │
│  local / S3+CloudFront / serve trên EC2 │
└──────────────────┬──────────────────────┘
                   │ POST /api/chat
                   ▼
┌─────────────────────────────────────────┐
│           EC2 (Ubuntu)                  │
│  ┌───────────────────────────────────┐  │
│  │ FastAPI                           │  │
│  │  - embed câu hỏi                  │  │
│  │  - retrieve top-k                 │  │
│  │  - gọi LLM sinh trả lời           │  │
│  │  - trả sources                    │  │
│  └───────────┬───────────┬───────────┘  │
│              │           │              │
│              ▼           ▼              │
│     Vector store     Ollama             │
│     (chunks+emb)   embed + chat         │
└──────────────────────▲──────────────────┘
                       │ sync / download
                       ▼
              ┌─────────────────┐
              │  Amazon S3      │
              │  DOCX/PDF docs  │
              └─────────────────┘
```

## Thành phần & trách nhiệm

| Thành phần | Việc | Ai |
|---|---|---|
| Ollama + prompt RAG | Model chat/embed, chất lượng trả lời | P3 |
| Ingest / vector store | Chuẩn hóa tài liệu, `python -m app.ingest` | P3 + P2 |
| FastAPI + FE | API chat, UI | P2 + P4 |
| EC2 + S3 + Budget | Deploy Cloud, chi phí, bảo mật SG | P1 |
| Tài liệu nghiệp vụ | Thu thập DOCX/PDF text | P3 + P4 |

## So sánh đưa vào báo cáo

| Tiêu chí | Bedrock managed | RAG tự build trên EC2 (đã chọn) |
|---|---|---|
| Kiểm soát | Ít | Cao (tự pipeline) |
| Phí | Theo token + KB | Theo giờ EC2 (credit $120) |
| Ops | Managed | Tự cài Ollama, Stop máy khi không dùng |
| Phù hợp đồ án | Có | Có — nhấn mạnh tự xây RAG + IaaS AWS |

## Region & chi phí

- Region: `ap-southeast-1`
- EC2: bật khi demo/dev, **Stop** khi xong
- S3 docs: private
- Budget alert: $15 / $40
