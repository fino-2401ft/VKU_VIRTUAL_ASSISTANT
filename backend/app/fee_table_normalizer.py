from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


EMPTY_MARK = "No data in source"


def _clean_cell(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _normalize_ascii(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    return re.sub(r"\s+", " ", text)


def parse_money(value: str) -> tuple[str | None, int | None, str]:
    """
    Returns (original_display, numeric_value, status).
    Empty -> (None, None, 'no_data'). Never coerce empty to 0.
    """
    raw = _clean_cell(value)
    if not raw:
        return None, None, "no_data"
    # keep original formatting for display
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return raw, None, "no_data"
    try:
        numeric = int(digits)
    except ValueError:
        return raw, None, "invalid"
    if numeric == 0 and raw in {"0", "0.0", "00"}:
        # explicit zero in source is rare for tuition; still keep as explicit value
        return raw, 0, "available"
    return raw, numeric, "available"


def detect_semester_and_year(text: str) -> tuple[str | None, str | None]:
    """Detect semester code and academic year YYYY-YYYY from filename/content."""
    n = _normalize_ascii(text)
    semester = None
    # Prefer explicit roman/arabic semester before broad "hè" heuristics
    if any(
        x in n
        for x in [
            "hoc ky he",
            "hoc ki he",
            "hoc ky he",
            "ky he nam",
            "hoc he nam",
            "hoc-ki-he",
            "hoc-ky-he",
        ]
    ) or re.search(r"\bhoc he\b", n) or re.search(r"\bky he\b", n):
        semester = "he"
    elif any(
        x in n
        for x in ["hoc ky 2", "hoc ki 2", "hoc ky ii", "hoc ki ii", "ky ii", "hoc-ki-2", "hoc-ky-2"]
    ):
        semester = "2"
    elif any(
        x in n
        for x in [
            "hoc ky 1",
            "hoc ki 1",
            "hoc ky i",
            "hoc ki i",
            "hoc-ki-1",
            "hoc-ky-1",
        ]
    ) or re.search(r"\bky i\b", n) or re.search(r"\bki 1\b", n):
        semester = "1"

    m = re.search(r"(20\d{2})\s*[-–—]\s*(20\d{2})", text)
    if not m:
        m = re.search(r"(20\d{2})\s+(20\d{2})", n)
    academic_year = f"{m.group(1)}-{m.group(2)}" if m else None
    return semester, academic_year


def suggest_fee_filename(path: Path, content_hint: str = "") -> str:
    """
    Rename pattern: hoc-phi-hoc-ki-1-2024-2025.docx
    Special tags: -thac-si, -gdqp, -cao-dang when detected.
    """
    # Filename wins over body text for semester/year (body may mention other kỳ)
    semester, year = detect_semester_and_year(path.name)
    if not semester or not year or year == "unknown":
        sem2, year2 = detect_semester_and_year(content_hint)
        semester = semester or sem2
        year = year if year and year != "unknown" else year2
    n = _normalize_ascii(f"{path.name} {content_hint}")
    suffix_bits: list[str] = []
    if "thac si" in n:
        suffix_bits.append("thac-si")
    if any(x in n for x in ["gdqp", "quoc phong", "an ninh"]):
        suffix_bits.append("gdqp")
    if "cao dang" in n:
        suffix_bits.append("cao-dang")

    if not semester:
        semester = "1"
    if not year:
        year = "unknown"

    base = f"hoc-phi-hoc-ki-{semester}-{year}"
    if suffix_bits:
        base += "-" + "-".join(suffix_bits)
    return f"{base}{path.suffix.lower()}"


@dataclass
class FeeRecord:
    record_id: str
    source_file: str
    academic_year: str | None
    semester: str | None
    industry_group: str | None
    training_system: str | None
    admission_cohort: str | None
    tuition_unit: str
    amount_original: str | None
    amount_numeric: int | None
    amount_status: str
    section_title: str | None
    document_type: str
    table_index: int
    row_index: int
    col_index: int
    kv_text: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizationResult:
    source_file: str
    academic_year: str | None
    semester: str | None
    document_type: str
    section_title: str | None
    tuition_unit: str
    records: list[FeeRecord]
    validation: dict[str, Any]
    markdown: str
    paragraphs_text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "document_type": self.document_type,
            "section_title": self.section_title,
            "tuition_unit": self.tuition_unit,
            "records": [r.to_dict() for r in self.records],
            "validation": self.validation,
            "paragraphs_text": self.paragraphs_text,
        }


def _extract_docx_matrix(path: Path) -> tuple[str, str | None, list[list[list[str]]]]:
    from docx import Document

    doc = Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    section_title = paragraphs[0] if paragraphs else path.stem
    tables: list[list[list[str]]] = []
    for table in doc.tables:
        rows: list[list[str]] = []
        for row in table.rows:
            # keep empty cells; dedupe adjacent merged repeats later if needed
            cells = [_clean_cell(c.text) for c in row.cells]
            rows.append(cells)
        # drop fully empty rows
        rows = [r for r in rows if any(c for c in r)]
        if rows:
            tables.append(rows)
    return "\n".join(paragraphs), section_title, tables


def _is_fee_header(header: list[str]) -> bool:
    joined = _normalize_ascii(" ".join(header))
    has_cohort = "khoa" in joined or bool(re.search(r"20\d{2}", joined))
    has_dim = any(k in joined for k in ["he", "nganh", "khoi", "chuong trinh", "dao tao"])
    return has_cohort and (has_dim or "khoa" in joined)


def _cohort_columns(header: list[str]) -> list[tuple[int, str]]:
    cols: list[tuple[int, str]] = []
    for idx, cell in enumerate(header):
        n = _normalize_ascii(cell)
        m = re.search(r"(20\d{2})", cell)
        if "khoa" in n and m:
            cols.append((idx, m.group(1)))
        elif m and (n.strip() == m.group(1) or n.startswith("khoa")):
            cols.append((idx, m.group(1)))
    # unique by index
    seen = set()
    out = []
    for idx, year in cols:
        if idx in seen:
            continue
        seen.add(idx)
        out.append((idx, year))
    return out


def _split_industry_system(label_parts: list[str]) -> tuple[str | None, str | None]:
    industry = None
    system = None
    for part in label_parts:
        n = _normalize_ascii(part)
        if n.startswith("he ") or "cu nhan" in n or "ky su" in n or "cao dang" in n:
            system = part
        elif industry is None:
            industry = part
        else:
            industry = f"{industry} - {part}"
    return industry, system


def _build_kv_text(rec: FeeRecord) -> str:
    lines = [
        "Loại tài liệu: thông báo học phí",
        f"Nguồn: {rec.source_file}",
        f"Năm học: {rec.academic_year or 'unknown'}",
        f"Học kỳ: {rec.semester or 'unknown'}",
        f"Khối ngành / chương trình: {rec.industry_group or EMPTY_MARK}",
        f"Hệ đào tạo: {rec.training_system or EMPTY_MARK}",
        f"Khóa tuyển sinh: {rec.admission_cohort or EMPTY_MARK}",
        f"Đơn vị: {rec.tuition_unit}",
    ]
    if rec.amount_status == "available":
        lines.append(f"Mức học phí (hiển thị): {rec.amount_original} {rec.tuition_unit}")
        lines.append(f"Mức học phí (số): {rec.amount_numeric}")
    else:
        lines.append(f"Mức học phí: {EMPTY_MARK}")
        lines.append("Ghi chú: ô trống trong bảng gốc — không suy diễn giá trị")
    if rec.section_title:
        lines.append(f"Tiêu đề mục: {rec.section_title}")
    return "\n".join(lines)


def normalize_fee_docx(path: Path) -> NormalizationResult:
    paragraphs, section_title, tables = _extract_docx_matrix(path)
    # Prefer filename for semester/year (body can mention other kỳ)
    semester, academic_year = detect_semester_and_year(path.name)
    if not semester or not academic_year:
        sem2, year2 = detect_semester_and_year(paragraphs)
        semester = semester or sem2
        academic_year = academic_year or year2
    unit = "đồng/tín chỉ"
    if re.search(r"đồng\s*/\s*tín chỉ|dvt", paragraphs, flags=re.I):
        unit = "đồng/tín chỉ"

    # Prefer short relative path under data/pdfs when possible
    source_ref = path.name
    try:
        parts = path.resolve().parts
        if "pdfs" in parts:
            i = parts.index("pdfs")
            source_ref = "/".join(parts[i + 1 :])
    except Exception:
        source_ref = path.name

    records: list[FeeRecord] = []
    expected_cells = 0
    non_empty_cells = 0
    extracted_available = 0
    extracted_no_data = 0

    for t_idx, rows in enumerate(tables):
        if not rows or not _is_fee_header(rows[0]):
            continue
        header = rows[0]
        cohort_cols = _cohort_columns(header)
        if not cohort_cols:
            continue
        first_cohort_idx = cohort_cols[0][0]

        for r_idx, row in enumerate(rows[1:], start=1):
            # pad row
            if len(row) < len(header):
                row = row + [""] * (len(header) - len(row))
            label_parts = [c for c in row[:first_cohort_idx] if c]
            # de-duplicate merged repeats while preserving order
            dedup_label: list[str] = []
            for p in label_parts:
                if not dedup_label or dedup_label[-1] != p:
                    dedup_label.append(p)
            industry, system = _split_industry_system(dedup_label)

            for c_idx, cohort in cohort_cols:
                expected_cells += 1
                cell = row[c_idx] if c_idx < len(row) else ""
                if _clean_cell(cell):
                    non_empty_cells += 1
                original, numeric, status = parse_money(cell)
                if status == "available":
                    extracted_available += 1
                else:
                    extracted_no_data += 1

                rid = f"{path.stem}-t{t_idx}-r{r_idx}-c{c_idx}-k{cohort}"
                rec = FeeRecord(
                    record_id=rid,
                    source_file=source_ref,
                    academic_year=academic_year,
                    semester=semester,
                    industry_group=industry,
                    training_system=system,
                    admission_cohort=cohort,
                    tuition_unit=unit,
                    amount_original=original,
                    amount_numeric=numeric,
                    amount_status=status if status != "invalid" else "no_data",
                    section_title=section_title,
                    document_type="tuition_notice",
                    table_index=t_idx,
                    row_index=r_idx,
                    col_index=c_idx,
                    kv_text="",
                )
                if status == "invalid":
                    rec.notes.append("Giá trị ô không parse được thành số — giữ nguyên text, đánh dấu no_data")
                    rec.amount_original = original
                    rec.amount_numeric = None
                    rec.amount_status = "no_data"
                rec.kv_text = _build_kv_text(rec)
                records.append(rec)

    validation = {
        "expected_cohort_cells": expected_cells,
        "non_empty_source_cells": non_empty_cells,
        "records_total": len(records),
        "records_available": extracted_available,
        "records_no_data": extracted_no_data,
        "available_matches_non_empty": extracted_available == non_empty_cells,
        "total_matches_expected": len(records) == expected_cells,
        "empty_never_coerced_to_zero": all(
            not (r.amount_status == "no_data" and r.amount_numeric == 0) for r in records
        ),
        "passed": (
            len(records) == expected_cells
            and extracted_available == non_empty_cells
            and all(not (r.amount_status == "no_data" and r.amount_numeric == 0) for r in records)
        ),
    }

    md_lines = [
        f"# Normalized tuition table — `{path.name}`",
        "",
        f"- Academic year: `{academic_year}`",
        f"- Semester: `{semester}`",
        f"- Document type: `tuition_notice`",
        f"- Unit: `{unit}`",
        f"- Validation passed: `{validation['passed']}`",
        "",
        "## Records",
        "",
        "| Industry group | Training system | Cohort | Amount | Status | Source |",
        "|---|---|---|---|---|---|",
    ]
    for r in records:
        amt = r.amount_original if r.amount_status == "available" else EMPTY_MARK
        md_lines.append(
            f"| {r.industry_group or ''} | {r.training_system or ''} | {r.admission_cohort} | {amt} | {r.amount_status} | `{path.name}` |"
        )
    md_lines.extend(["", "## Key-value chunks", ""])
    for r in records:
        if r.amount_status != "available":
            continue
        md_lines.append(f"### `{r.record_id}`")
        md_lines.append("```text")
        md_lines.append(r.kv_text)
        md_lines.append("```")
        md_lines.append("")

    return NormalizationResult(
        source_file=source_ref,
        academic_year=academic_year,
        semester=semester,
        document_type="tuition_notice",
        section_title=section_title,
        tuition_unit=unit,
        records=records,
        validation=validation,
        markdown="\n".join(md_lines),
        paragraphs_text=paragraphs,
    )


def records_to_chunks(records: list[FeeRecord], only_available: bool = True) -> list[dict[str, Any]]:
    """One retrieval chunk per logical training-system × cohort record."""
    chunks = []
    for r in records:
        if only_available and r.amount_status != "available":
            # still keep no_data records as explicit chunks if needed for audit
            text = r.kv_text
        else:
            text = r.kv_text
        if only_available and r.amount_status != "available":
            continue
        chunks.append(
            {
                "id": r.record_id,
                "text": text,
                "source": r.source_file,
                "metadata": {
                    "academic_year": r.academic_year,
                    "semester": r.semester,
                    "industry_group": r.industry_group,
                    "training_system": r.training_system,
                    "admission_cohort": r.admission_cohort,
                    "tuition_unit": r.tuition_unit,
                    "amount_original": r.amount_original,
                    "amount_numeric": r.amount_numeric,
                    "amount_status": r.amount_status,
                    "document_type": r.document_type,
                    "section_title": r.section_title,
                    "table_index": r.table_index,
                    "row_index": r.row_index,
                    "col_index": r.col_index,
                },
            }
        )
    return chunks


def export_normalization(
    result: NormalizationResult,
    out_dir: Path,
    stem: str | None = None,
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = stem or Path(result.source_file).stem
    paths = {
        "json": out_dir / f"{stem}.normalized.json",
        "md": out_dir / f"{stem}.normalized.md",
        "chunks": out_dir / f"{stem}.chunks.json",
    }
    paths["json"].write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    paths["md"].write_text(result.markdown, encoding="utf-8")
    chunks = records_to_chunks(result.records, only_available=True)
    # also include no_data audit file section inside json already; chunks focus on retrievable fees
    paths["chunks"].write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return paths


def rename_fee_files(folder: Path, dry_run: bool = False) -> list[dict[str, str]]:
    """Rename DOCX tuition files to hoc-phi-hoc-ki-<sem>-<yyyy-yyyy>[...].docx"""
    changes: list[dict[str, str]] = []
    used: set[str] = set()
    for path in sorted(folder.glob("*.docx")):
        try:
            paragraphs, _, _ = _extract_docx_matrix(path)
        except Exception:
            paragraphs = ""
        new_name = suggest_fee_filename(path, paragraphs)
        # avoid collisions
        candidate = new_name
        i = 2
        while candidate.lower() in used or (
            (folder / candidate).exists() and (folder / candidate).resolve() != path.resolve()
        ):
            stem = Path(new_name).stem
            candidate = f"{stem}-{i}.docx"
            i += 1
        used.add(candidate.lower())
        if candidate != path.name:
            changes.append({"from": path.name, "to": candidate})
            if not dry_run:
                path.rename(folder / candidate)
    return changes
