from __future__ import annotations

from pathlib import Path

from .fee_table_normalizer import normalize_fee_docx

DOCS_ROOT = Path(__file__).resolve().parents[2] / "data" / "pdfs"
SUPPORTED = {".pdf", ".docx", ".txt", ".md"}


def _is_fee_docx(path: Path) -> bool:
    name_l = path.name.lower()
    return (
        "hoc-phi" in name_l
        or "hoc phi" in name_l
        or "học phí" in path.name.lower()
        or path.parent.name.lower() == "hoc-phi"
    )


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _read_docx(path: Path) -> str:
    """
    Tuition DOCX: narrative paragraphs only (fee cells ingested as one chunk each).
    Other DOCX: paragraphs + flattened tables; empty cells marked explicitly.
    """
    if _is_fee_docx(path):
        result = normalize_fee_docx(path)
        return result.paragraphs_text.strip()

    from docx import Document

    doc = Document(str(path))
    parts: list[str] = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [" ".join(c.text.split()) for c in row.cells]
            cells = [c if c else "No data in source" for c in cells]
            if any(c != "No data in source" for c in cells):
                parts.append(" | ".join(cells))
    return "\n".join(parts)


def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return _read_txt(path)
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".docx":
        return _read_docx(path)
    raise ValueError(f"Không hỗ trợ: {suffix}")


def iter_fee_record_documents(root: Path | None = None) -> list[tuple[Path, str, dict]]:
    """
    One item per tuition fee logical record (training-system × cohort).
    Empty cells are not emitted as available amounts (never coerced to 0).
    """
    root = root or (DOCS_ROOT / "hoc-vu" / "hoc-phi")
    items: list[tuple[Path, str, dict]] = []
    if not root.exists():
        return items
    for path in sorted(root.glob("*.docx")):
        try:
            result = normalize_fee_docx(path)
        except Exception as exc:  # noqa: BLE001
            print(f"[skip-normalize] {path.name}: {exc}")
            continue
        for rec in result.records:
            # Keep no_data rows as explicit chunks (never coerce empty → 0)
            meta = {
                "record_id": rec.record_id,
                "academic_year": rec.academic_year,
                "semester": rec.semester,
                "industry_group": rec.industry_group,
                "training_system": rec.training_system,
                "admission_cohort": rec.admission_cohort,
                "tuition_unit": rec.tuition_unit,
                "amount_original": rec.amount_original,
                "amount_numeric": rec.amount_numeric,
                "amount_status": rec.amount_status,
                "document_type": rec.document_type,
                "section_title": rec.section_title,
                "table_index": rec.table_index,
                "row_index": rec.row_index,
                "col_index": rec.col_index,
                "validation_passed": result.validation.get("passed"),
            }
            items.append((path, rec.kv_text, meta))
    return items


def iter_documents(root: Path | None = None) -> list[tuple[Path, str]]:
    root = root or DOCS_ROOT
    if not root.exists():
        return []
    items: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED:
            continue
        if path.name.lower() == "readme.md":
            continue
        try:
            text = read_file(path).strip()
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] {path.name}: {exc}")
            continue
        # Fee narrative can be short; fee amounts come from iter_fee_record_documents
        min_len = 20 if _is_fee_docx(path) else 40
        if len(text) < min_len:
            print(f"[skip] {path.name}: quá ngắn / không extract được text")
            continue
        items.append((path, text))
    return items
