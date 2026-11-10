"""Load retrieval chunks from data/normalized/{hoc-phi,quy-che} markdown only."""

from __future__ import annotations

import re
from pathlib import Path

from .rag_store import chunk_text

ROOT = Path(__file__).resolve().parents[2] / "data" / "normalized"
COLLECTIONS = ("hoc-phi", "quy-che")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _meta_line(text: str, label: str) -> str | None:
    m = re.search(rf"^- {re.escape(label)}:\s*`?([^`\n]+)`?", text, flags=re.M)
    return m.group(1).strip() if m else None


def _fee_kv_from_row(
    *,
    source_name: str,
    academic_year: str | None,
    semester: str | None,
    unit: str | None,
    industry: str,
    system: str,
    cohort: str,
    amount: str,
    status: str,
) -> str:
    unit = unit or "đồng/tín chỉ"
    lines = [
        "Loại tài liệu: thông báo học phí",
        f"Nguồn: {source_name}",
        f"Năm học: {academic_year or 'unknown'}",
        f"Học kỳ: {semester or 'unknown'}",
        f"Khối ngành / chương trình: {industry or 'No data in source'}",
        f"Hệ đào tạo: {system or 'No data in source'}",
        f"Khóa tuyển sinh: {cohort or 'No data in source'}",
        f"Đơn vị: {unit}",
    ]
    status_l = status.strip().lower()
    amount_l = amount.strip().lower()
    if status_l == "available" and amount_l and "no data" not in amount_l:
        lines.append(f"Mức học phí (hiển thị): {amount} {unit}")
    else:
        lines.append("Mức học phí (hiển thị): No data in source")
        lines.append("Ghi chú: ô trống trong bảng gốc — không suy diễn giá trị")
    return "\n".join(lines)


def _parse_fee_markdown(path: Path) -> list[dict]:
    text = _read(path)
    rel = f"hoc-phi/{path.name}"
    year = _meta_line(text, "Academic year")
    semester = _meta_line(text, "Semester")
    unit = _meta_line(text, "Unit")
    docx_name = path.name.replace(".normalized.md", ".docx")
    m = re.search(r"`([^`]+\.docx)`", text)
    if m:
        docx_name = m.group(1)

    rows: list[dict] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        if cells[0].lower() in {"industry group", "---"} or set(cells[0]) <= {"-", ":"}:
            continue
        if cells[2].lower() == "cohort":
            continue
        industry, system, cohort, amount, status = cells[0], cells[1], cells[2], cells[3], cells[4]
        if not cohort or not cohort[0].isdigit():
            continue
        kv = _fee_kv_from_row(
            source_name=docx_name,
            academic_year=year,
            semester=semester,
            unit=unit,
            industry=industry,
            system=system,
            cohort=cohort,
            amount=amount,
            status=status,
        )
        rows.append(
            {
                "id": f"{path.stem}-{cohort}-{len(rows)}",
                "text": kv,
                "source": rel,
                "kind": "hoc-phi",
                "metadata": {
                    "academic_year": year,
                    "semester": semester,
                    "industry_group": industry,
                    "training_system": system,
                    "admission_cohort": cohort,
                    "amount_status": status,
                    "document_type": "tuition_notice",
                },
            }
        )
    if rows:
        return rows

    # Narrative notices that have no fee table: keep the markdown body.
    body = text.strip()
    if len(body) < 40:
        return []
    out = []
    for i, piece in enumerate(chunk_text(body, chunk_size=900, overlap=100)):
        out.append(
            {
                "id": f"{path.stem}-n{i}",
                "text": piece,
                "source": rel,
                "kind": "hoc-phi",
                "metadata": {"document_type": "tuition_notice"},
            }
        )
    return out


def _parse_quy_che(path: Path) -> list[dict]:
    text = _read(path)
    rel = f"quy-che/{path.name}"
    chapter = ""
    title = "Phần mở đầu"
    buf: list[str] = []
    sections: list[tuple[str, str, str]] = []

    def flush() -> None:
        body = "\n".join(buf).strip()
        if len(body) >= 40:
            sections.append((chapter, title, body))

    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            flush()
            buf = []
            chapter = line[3:].strip()
            title = chapter
            continue
        if line.startswith("### "):
            flush()
            buf = []
            title = line[4:].strip()
            continue
        buf.append(line)
    flush()

    out: list[dict] = []
    for idx, (chap, heading, body) in enumerate(sections):
        pieces = chunk_text(body, chunk_size=900, overlap=80) if len(body) > 900 else [body]
        for j, piece in enumerate(pieces):
            header = [f"Tài liệu: {rel}"]
            if chap:
                header.append(f"Chương: {chap}")
            header.append(f"Mục: {heading}")
            out.append(
                {
                    "id": f"{path.stem}-s{idx}-{j}",
                    "text": "\n".join(header) + "\n" + piece,
                    "source": rel,
                    "kind": "quy-che",
                    "metadata": {
                        "document_type": "regulation",
                        "chapter": chap,
                        "section": heading,
                    },
                }
            )
    return out


def iter_normalized_chunks() -> list[dict]:
    items: list[dict] = []
    for name, parser in (("hoc-phi", _parse_fee_markdown), ("quy-che", _parse_quy_che)):
        folder = ROOT / name
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            items.extend(parser(path))
    return items
