from __future__ import annotations

import re
import unicodedata
from typing import Any

from . import ollama_client
from .rag_store import load_chunks, search, store_exists

SYSTEM_PROMPT = """Bạn là trợ lý ảo học vụ/tuyển sinh của trường VKU.
Chỉ dùng thông tin trong tài liệu được cung cấp.
Nếu thiếu thông tin: trả đúng câu "Không tìm thấy trong tài liệu hiện có."
BẮT BUỘC:
- Chỉ viết câu trả lời bằng tiếng Việt.
- Không viết suy nghĩ, không viết tiếng Anh.
- Trả lời đầy đủ, chi tiết. Không tóm tắt, không bỏ ý, không gộp nhiều điều kiện thành một câu.
- Liệt kê từng mục, từng điểm a), b), c) đúng như tài liệu, giữ nguyên con số, tỷ lệ, mốc thời gian và ngoại lệ.
- Nếu một điều có nhiều khoản, viết hết các khoản liên quan đến câu hỏi.
- Nêu tên điều, chương và file nguồn ở cuối. Số điều phải chép từ dòng "Mục:" trong tài liệu, không tự đặt số khác.
- Không bịa thêm quy định không có trong đoạn tài liệu."""


def rag_ready() -> bool:
    return ollama_client.is_available() and store_exists()


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _keyword_boost(question: str, hit: dict[str, Any]) -> float:
    """Cộng điểm nếu tên file/nội dung khớp năm học, học kỳ, ngành..."""
    q = _normalize(question)
    blob = _normalize(f"{hit.get('source', '')} {hit.get('text', '')}")
    boost = 0.0

    years = re.findall(r"20\d{2}", q)
    src = _normalize(hit.get("source", ""))
    if len(years) >= 2:
        y1, y2 = years[0], years[1]
        # Ưu tiên khớp cặp năm trên TÊN FILE (tránh nhầm cột khóa trong bảng)
        if re.search(rf"{y1}\s*-?\s*{y2}", src):
            boost += 0.28
        else:
            wrong = re.search(r"(20\d{2})\s*-?\s*(20\d{2})", src)
            if wrong and (wrong.group(1), wrong.group(2)) != (y1, y2):
                boost -= 0.30
            elif y1 in src or y2 in src:
                boost += 0.04
    elif len(years) == 1 and years[0] in src:
        boost += 0.05

    semester_patterns = [
        ("hoc ky 1", ["hoc ky 1", "hoc ki 1", "ky i ", "ki 1"]),
        ("hoc ky 2", ["hoc ky 2", "hoc ki 2", "ky ii", "ki 2"]),
        ("hoc ky he", ["hoc ky he", "hoc he", "he nam"]),
    ]
    for needle, aliases in semester_patterns:
        if needle in q or any(a in q for a in aliases):
            if any(a in blob for a in aliases):
                boost += 0.08
            # phạt nếu hỏi HK1 mà chunk/file là HK2 hoặc hè
            if "hoc ky 1" in needle and any(x in blob for x in ["hoc ky 2", "hoc ki 2", "hoc ky he", "hoc he"]):
                if "hoc ky 1" not in blob and "hoc ki 1" not in blob:
                    boost -= 0.08
            break

    for kw, aliases in [
        ("ky su", ["ky su", "he ky su"]),
        ("cu nhan", ["cu nhan", "he cu nhan"]),
        ("cong nghe thong tin", ["cong nghe thong tin", "cntt", "may tinh va cong nghe"]),
        ("thac si", ["thac si"]),
        ("khoi nganh v", ["khoi nganh v", "nganh v"]),
        ("khoi nganh iii", ["khoi nganh iii", "nganh iii"]),
    ]:
        if kw in q or any(a in q for a in aliases):
            if any(a in blob for a in aliases):
                boost += 0.10

    # khớp đúng khóa (vd Khóa 2023)
    for m in re.finditer(r"khoa\s*(20\d{2})", q):
        token = f"khoa {m.group(1)}"
        if token in blob:
            boost += 0.14

    # có bảng mức thu / bản ghi KV → ưu tiên khi hỏi học phí/ngành
    if any(k in q for k in ["hoc phi", "nganh", "ky su", "cu nhan", "tin chi"]):
        if any(
            x in blob
            for x in [
                "bang du lieu",
                "dong/tin chi",
                "dvt",
                "muc hoc phi",
                "he dao tao",
                "khoa tuyen sinh",
                "thong bao hoc phi",
            ]
        ):
            boost += 0.12

    # phạt thạc sĩ nếu câu hỏi không nhắc thạc sĩ
    if "thac si" not in q and "thac si" in blob:
        boost -= 0.15

    if "2025" in q and "2025" not in blob and re.search(r"202[0-4]", blob):
        boost -= 0.06
    return boost


def _rerank(question: str, hits: list[dict[str, Any]], keep: int = 4) -> list[dict[str, Any]]:
    ranked: list[tuple[float, dict[str, Any]]] = []
    for h in hits:
        score = float(h.get("score") or 0) + _keyword_boost(question, h)
        ranked.append((score, h))
    ranked.sort(key=lambda x: x[0], reverse=True)

    # Ép lấy chunk BẢNG từ file đúng năm + học kỳ (không phụ thuộc semantic top)
    qn = _normalize(question)
    need_table = any(k in qn for k in ["hoc phi", "nganh", "ky su", "cu nhan", "tin chi"])
    years = re.findall(r"20\d{2}", qn)
    ask_hk1 = any(x in qn for x in ["hoc ky 1", "hoc ki 1"])
    ask_hk2 = any(x in qn for x in ["hoc ky 2", "hoc ki 2"])
    if need_table and len(years) >= 2:
        y1, y2 = years[0], years[1]
        preferred: list[tuple[float, dict[str, Any]]] = []
        for ch in load_chunks():
            src_n = _normalize(ch.get("source", ""))
            text_n = _normalize(ch.get("text", ""))
            if not re.search(rf"{y1}\s*-?\s*{y2}", src_n):
                continue
            if ask_hk1 and any(x in src_n for x in ["hoc ky 2", "hoc ki 2", "hoc ky he", "hoc ki he"]):
                continue
            if ask_hk1 and not any(x in src_n for x in ["hoc ky 1", "hoc ki 1"]):
                continue
            if ask_hk2 and any(x in src_n for x in ["hoc ky 1", "hoc ki 1", "hoc ky he", "hoc ki he"]):
                continue
            if any(
                x in text_n
                for x in ["bang du lieu", "he ky su", "he dao tao", "muc hoc phi", "khoa tuyen sinh"]
            ):
                score = 0.5 + _keyword_boost(question, ch) + 0.5
                preferred.append((score, ch))
        if preferred:
            preferred.sort(key=lambda x: x[0], reverse=True)
            pref_ids = {id(h) for _, h in preferred}
            ranked = preferred[:2] + [(s, h) for s, h in ranked if id(h) not in pref_ids]

    # Quy chế: ưu tiên mục có tiêu đề khớp câu hỏi (Điều 2, Điều 17, ...)
    if "hoc phi" not in qn:
        q_tokens = {t for t in qn.split() if len(t) > 3}
        reg: list[tuple[float, dict[str, Any]]] = []
        for ch in load_chunks():
            src = ch.get("source", "")
            if not str(src).startswith("quy-che/"):
                continue
            head = "\n".join(ch.get("text", "").splitlines()[:8])
            hn = _normalize(head)
            overlap = sum(1 for t in q_tokens if t in hn)
            bonus = overlap * 0.08
            if "quy che dao tao" in qn and "quy che dao tao" in _normalize(src):
                bonus += 0.25
            if "tot nghiep" in qn and "tot nghiep" in hn:
                bonus += 0.35
            if "thoi gian" in qn and "thoi gian dao tao" in hn:
                bonus += 0.35
            if bonus < 0.3:
                continue
            reg.append((1.1 + bonus, ch))
        if reg:
            reg.sort(key=lambda x: x[0], reverse=True)
            pref_ids = {id(h) for _, h in reg[:3]}
            ranked = reg[:3] + [(s, h) for s, h in ranked if id(h) not in pref_ids]

    out: list[dict[str, Any]] = []
    seen_sources: list[str] = []
    for score, h in ranked:
        src = h.get("source", "")
        if seen_sources.count(src) >= 4:
            continue
        item = dict(h)
        item["score"] = round(score, 4)
        out.append(item)
        seen_sources.append(src)
        if len(out) >= keep:
            break
    return out


def _parse_fee_kv_block(text: str) -> dict[str, str] | None:
    """Parse self-contained key-value fee chunk produced by fee_table_normalizer."""
    if "loại tài liệu: thông báo học phí" not in text.lower() and "muc hoc phi" not in _normalize(text):
        # still allow if key fields present
        if "hệ đào tạo:" not in text.lower() and "he dao tao:" not in _normalize(text):
            return None
    fields: dict[str, str] = {}
    for raw in text.splitlines():
        if ":" not in raw:
            continue
        key, val = raw.split(":", 1)
        kn = _normalize(key)
        v = val.strip()
        if kn.startswith("nguon") or kn.startswith("tai lieu"):
            fields["source"] = v
        elif kn.startswith("nam hoc"):
            fields["academic_year"] = v
        elif kn.startswith("hoc ky"):
            fields["semester"] = v
        elif "khoi nganh" in kn or "chuong trinh" in kn:
            fields["industry_group"] = v
        elif "he dao tao" in kn:
            fields["training_system"] = v
        elif "khoa tuyen sinh" in kn:
            fields["admission_cohort"] = v
        elif kn.startswith("don vi"):
            fields["unit"] = v
        elif "muc hoc phi" in kn and "so" not in kn:
            fields["amount_display"] = v
        elif "muc hoc phi" in kn and "so" in kn:
            fields["amount_numeric"] = v
    if not fields.get("admission_cohort") and not fields.get("amount_display"):
        return None
    return fields


def _try_structured_fee_answer(
    question: str, hits: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """
    Tra cứu trực tiếp bản ghi KV đã chuẩn hóa (fee_table_normalizer),
    kèm fallback regex dòng cũ nếu còn trong store.
    Không suy diễn ô trống / giá trị thiếu.
    """
    q = _normalize(question)
    if "hoc phi" not in q:
        return None
    khoa_m = re.search(r"khoa\s*(20\d{2})", q)
    if not khoa_m:
        return None
    khoa = khoa_m.group(1)

    want_ky_su = "ky su" in q
    want_cu_nhan = "cu nhan" in q
    if want_ky_su and want_cu_nhan:
        return None
    if not want_ky_su and not want_cu_nhan:
        return None

    he = "ky su" if want_ky_su else "cu nhan"
    want_v = "khoi nganh v" in q or re.search(r"\bnganh v\b", q) is not None or "cong nghe thong tin" in q
    want_iii = "khoi nganh iii" in q or "nganh iii" in q or "kinh doanh" in q
    ask_block = want_v or want_iii

    years = re.findall(r"20\d{2}", q)
    # academic year pair excludes the cohort year when possible
    year_pair = None
    if len(years) >= 2:
        # prefer consecutive academic-year pair near "nam hoc"
        m_ay = re.search(r"(20\d{2})\s*-?\s*(20\d{2})", q)
        if m_ay:
            year_pair = (m_ay.group(1), m_ay.group(2))
        else:
            # drop cohort year if present
            cands = [y for y in years if y != khoa]
            if len(cands) >= 2:
                year_pair = (cands[0], cands[1])
            elif len(years) >= 2:
                year_pair = (years[0], years[1])

    ask_hk1 = any(x in q for x in ["hoc ky 1", "hoc ki 1", "hoc-ki-1"])
    ask_hk2 = any(x in q for x in ["hoc ky 2", "hoc ki 2", "hoc-ki-2"])
    ask_he = any(x in q for x in ["hoc ky he", "hoc he", "ky he"])

    corpus = list(hits)
    for ch in load_chunks():
        src_n = _normalize(ch.get("source", ""))
        text_n = _normalize(ch.get("text", ""))
        if year_pair:
            y1, y2 = year_pair
            year_ok = re.search(rf"{y1}\s*-?\s*{y2}", src_n) or re.search(
                rf"nam hoc:\s*{y1}-{y2}", text_n
            )
            if not year_ok:
                continue
        # NOTE: _normalize strips hyphens → "hoc-ki-1" becomes "hoc ki 1"
        if ask_hk1 and any(
            x in src_n for x in ["hoc ki 2", "hoc ky 2", "hoc ki he", "hoc ky he"]
        ):
            continue
        if ask_hk1 and not any(x in src_n for x in ["hoc ki 1", "hoc ky 1"]):
            if "hoc ky 1" not in text_n and "hoc ky: 1" not in text_n:
                continue
        if ask_hk2 and any(
            x in src_n for x in ["hoc ki 1", "hoc ky 1", "hoc ki he", "hoc ky he"]
        ):
            continue
        if ask_he and not any(x in src_n for x in ["hoc ki he", "hoc ky he"]) and "hoc ky he" not in text_n:
            continue
        corpus.append(ch)

    def _sem_ok(sem: str, src: str) -> bool:
        sn = _normalize(sem)
        srcn = _normalize(src)
        if ask_hk1:
            return sn == "1" or "hoc ki 1" in srcn or "hoc ky 1" in srcn
        if ask_hk2:
            return sn == "2" or "hoc ki 2" in srcn or "hoc ky 2" in srcn
        if ask_he:
            return sn == "he" or "hoc ki he" in srcn or "hoc ky he" in srcn
        return True

    def _year_ok(ay: str, src: str) -> bool:
        if not year_pair:
            return True
        y1, y2 = year_pair
        blob = _normalize(f"{ay} {src}")
        return bool(re.search(rf"{y1}\s*-?\s*{y2}", blob))

    def collect_kv(strict_block: bool, include_no_data: bool = False) -> list[tuple[str, str, str, str, str]]:
        found: list[tuple[str, str, str, str, str]] = []
        for h in corpus:
            parsed = _parse_fee_kv_block(h.get("text", ""))
            if not parsed:
                continue
            cohort = re.sub(r"\D", "", parsed.get("admission_cohort", ""))
            if cohort != khoa:
                continue
            if not _year_ok(parsed.get("academic_year", ""), h.get("source", "")):
                continue
            if not _sem_ok(parsed.get("semester", ""), h.get("source", "")):
                continue
            sys_n = _normalize(parsed.get("training_system", ""))
            if he not in sys_n:
                continue
            ind_n = _normalize(parsed.get("industry_group", ""))
            if strict_block:
                if want_v and "khoi nganh v" not in ind_n and "cong nghe thong tin" not in ind_n:
                    continue
                if want_iii and "khoi nganh iii" not in ind_n and "kinh doanh" not in ind_n:
                    continue
            amount = parsed.get("amount_display") or ""
            is_empty = "no data" in amount.lower() or not amount.strip()
            if is_empty and not include_no_data:
                continue
            if is_empty:
                amount_clean = "No data in source"
            else:
                amount_clean = re.sub(r"\s*đồng.*$", "", amount, flags=re.I).strip()
            label = " - ".join(
                x for x in [parsed.get("industry_group", ""), parsed.get("training_system", "")] if x
            )
            year = parsed.get("academic_year", "")
            sem = parsed.get("semester", "")
            found.append((label, khoa, amount_clean, h.get("source", ""), f"{year}|{sem}"))
        return found

    # legacy pipe format fallback
    line_re = re.compile(
        r"(?P<label>Khối ngành.+?Hệ\s+(?:kỹ sư|cử nhân)[^|]*)\|\s*Khóa\s+(?P<khoa>20\d{2})\s*:\s*(?P<fee>[\d.]+)\s*đồng",
        re.IGNORECASE,
    )

    def collect_legacy(strict_block: bool) -> list[tuple[str, str, str, str, str]]:
        found: list[tuple[str, str, str, str, str]] = []
        for h in corpus:
            if not _year_ok("", h.get("source", "")):
                continue
            if not _sem_ok("", h.get("source", "")):
                continue
            for raw in h.get("text", "").splitlines():
                m = line_re.search(raw)
                if not m or m.group("khoa") != khoa:
                    continue
                label_n = _normalize(m.group("label"))
                if he not in label_n:
                    continue
                if strict_block:
                    if want_v and "khoi nganh v" not in label_n and "cong nghe thong tin" not in label_n:
                        continue
                    if want_iii and "khoi nganh iii" not in label_n and "kinh doanh" not in label_n:
                        continue
                found.append(
                    (m.group("label").strip(" -"), khoa, m.group("fee"), h.get("source", ""), "")
                )
        return found

    # Never broaden industry when user named a specific block — avoids inventing from other rows
    matches = collect_kv(strict_block=True) or collect_legacy(strict_block=True)
    if not matches and not ask_block:
        matches = collect_kv(strict_block=False) or collect_legacy(strict_block=False)
    if not matches and ask_block:
        # Explicit empty cell in source for that block/cohort
        empty_hits = collect_kv(strict_block=True, include_no_data=True)
        if empty_hits:
            label, khoa_v, _, src, meta = empty_hits[0]
            year_sem = ""
            if meta and "|" in meta:
                y, s = meta.split("|", 1)
                if y and y != "unknown":
                    year_sem = f" năm học {y}"
                if s and s != "unknown":
                    year_sem += f", học kỳ {s}"
            return {
                "answer": (
                    f"Theo tài liệu{year_sem}, {label}, Khóa {khoa_v}: "
                    f"No data in source (ô trống trong bảng gốc — không suy diễn)."
                ),
                "sources": [
                    {
                        "id": src,
                        "title": src,
                        "category": "Tài liệu",
                        "file": src,
                        "score": 1.0,
                    }
                ],
                "category": "RAG",
                "confidence": 0.9,
                "mode": "rag-structured",
            }

    if not matches:
        return None

    unique = []
    seen = set()
    for item in matches:
        key = (item[0], item[1], item[2], item[4])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    def _fmt_fee(fee: str) -> str:
        if "no data" in fee.lower():
            return "No data in source (ô trống trong bảng gốc — không suy diễn)"
        return f"{fee} đồng/tín chỉ"

    if len(unique) == 1:
        label, khoa_v, fee, src, meta = unique[0]
        year_sem = ""
        if meta and "|" in meta:
            y, s = meta.split("|", 1)
            if y and y != "unknown":
                year_sem = f" năm học {y}"
            if s and s != "unknown":
                year_sem += f", học kỳ {s}"
        answer = (
            f"Theo tài liệu{year_sem}:\n"
            f"- Khối ngành / hệ: {label}\n"
            f"- Khóa tuyển sinh: {khoa_v}\n"
            f"- Mức học phí: {_fmt_fee(fee)}\n"
            f"- Nguồn: {src}"
        )
    else:
        lines = ["Theo tài liệu, các mức học phí khớp câu hỏi:"]
        for label, khoa_v, fee, src, meta in unique:
            extra = ""
            if meta and "|" in meta:
                y, s = meta.split("|", 1)
                bits = [b for b in [f"năm học {y}" if y and y != "unknown" else "", f"học kỳ {s}" if s not in {"", "unknown"} else ""] if b]
                if bits:
                    extra = " (" + ", ".join(bits) + ")"
            lines.append(
                f"- {label}{extra}\n"
                f"  Khóa tuyển sinh: {khoa_v}\n"
                f"  Mức học phí: {_fmt_fee(fee)}\n"
                f"  Nguồn: {src}"
            )
        answer = "\n".join(lines)

    sources = []
    for _, _, _, src, _ in unique:
        if not any(s.get("file") == src for s in sources):
            sources.append(
                {
                    "id": src,
                    "title": src,
                    "category": "Tài liệu",
                    "file": src,
                    "score": 1.0,
                }
            )
    return {
        "answer": answer,
        "sources": sources,
        "category": "RAG",
        "confidence": 0.95,
        "mode": "rag-structured",
    }


def _regulation_candidates(question: str) -> list[tuple[float, dict[str, Any]]]:
    """Xếp các mục quy chế có tiêu đề khớp câu hỏi."""
    qn = _normalize(question)
    if "hoc phi" in qn:
        return []
    q_tokens = {t for t in qn.split() if len(t) > 3}
    found: list[tuple[float, dict[str, Any]]] = []
    for ch in load_chunks():
        src = str(ch.get("source", ""))
        if not src.startswith("quy-che/"):
            continue
        head = "\n".join(ch.get("text", "").splitlines()[:8])
        hn = _normalize(head)
        overlap = sum(1 for t in q_tokens if t in hn)
        bonus = overlap * 0.08
        if "quy che dao tao" in qn and "quy che dao tao" in _normalize(src):
            bonus += 0.25
        if "tot nghiep" in qn and "tot nghiep" in hn:
            bonus += 0.35
        if "thoi gian" in qn and "thoi gian dao tao" in hn:
            bonus += 0.35
        if bonus < 0.45:
            continue
        found.append((bonus, ch))
    found.sort(key=lambda x: x[0], reverse=True)
    return found


def _section_body(text: str) -> str:
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("Mục:") or line.startswith("Chương:"):
            start = i
            break
    body = "\n".join(lines[start:]).strip()
    return body


def _section_key(ch: dict[str, Any]) -> tuple[str, str]:
    src = str(ch.get("source", ""))
    for line in ch.get("text", "").splitlines():
        if line.startswith("Mục:"):
            return src, line.strip()
    return src, ""


def _try_detailed_regulation_answer(
    question: str, hits: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Trả nguyên văn cả mục quy chế khớp nhất, gồm mọi đoạn đã cắt."""
    ranked = _regulation_candidates(question)
    if not ranked:
        return None
    best_src, best_muc = _section_key(ranked[0][1])
    if not best_muc:
        return None
    parts_ch = [
        ch
        for ch in load_chunks()
        if _section_key(ch) == (best_src, best_muc)
    ]
    parts_ch.sort(key=lambda ch: int(ch.get("chunk_index") or 0))
    if not parts_ch:
        return None
    bodies = [_section_body(ch.get("text", "")) for ch in parts_ch]
    # Đoạn sau của cùng một mục không lặp lại dòng Chương/Mục
    merged = [bodies[0]]
    for body in bodies[1:]:
        kept = [
            ln
            for ln in body.splitlines()
            if not ln.startswith("Chương:") and not ln.startswith("Mục:")
        ]
        extra = "\n".join(kept).strip()
        if extra:
            merged.append(extra)
    answer = "Theo tài liệu, nội dung liên quan được ghi như sau:\n\n" + "\n".join(merged)
    cleaned: list[str] = []
    prev = ""
    for line in answer.splitlines():
        if line.strip() and line.strip() == prev:
            continue
        cleaned.append(line)
        if line.strip():
            prev = line.strip()
    answer = "\n".join(cleaned)
    return {
        "answer": answer,
        "sources": [
            {
                "id": parts_ch[0].get("id", best_src),
                "title": best_src,
                "category": "Tài liệu",
                "file": best_src,
                "score": 1.0,
            }
        ],
        "category": "RAG",
        "confidence": 0.95,
        "mode": "rag-section",
    }


def answer_with_rag(question: str, top_k: int = 4) -> dict[str, Any]:
    if not ollama_client.is_available():
        raise RuntimeError("Ollama không khả dụng")
    if not store_exists():
        raise RuntimeError("Chưa ingest tài liệu (chạy: python -m app.ingest)")

    q_emb = ollama_client.embed(question)
    hits = search(q_emb, top_k=max(12, top_k * 3))
    hits = [h for h in hits if h.get("score", 0) >= 0.20]
    hits = _rerank(question, hits, keep=max(top_k, 6))

    if not hits:
        return {
            "answer": (
                "Không tìm thấy trong tài liệu hiện có. "
                "Bạn thử hỏi về học phí, thời gian thu học phí, hoặc quy định liên quan."
            ),
            "sources": [],
            "category": "RAG",
            "confidence": 0.0,
            "mode": "rag-ollama",
        }

    structured = _try_structured_fee_answer(question, hits)
    if structured:
        return structured

    detailed = _try_detailed_regulation_answer(question, hits)
    if detailed:
        return detailed

    context_blocks = []
    sources = []
    for i, h in enumerate(hits, 1):
        context_blocks.append(f"[{i}] Nguồn: {h['source']}\n{h['text']}")
        sources.append(
            {
                "id": h["id"],
                "title": h["source"],
                "category": "Tài liệu",
                "file": h["source"],
                "score": h.get("score"),
            }
        )

    context = "\n\n".join(context_blocks)
    prompt = (
        f"Câu hỏi: {question}\n\n"
        f"Tài liệu:\n{context}\n\n"
        "Hãy trả lời đầy đủ bằng tiếng Việt: liệt kê từng ý trong mục liên quan, không rút gọn, không kèm suy nghĩ."
    )
    answer = ollama_client.chat(prompt, SYSTEM_PROMPT).strip()
    avg_score = sum(h.get("score", 0) for h in hits) / len(hits)

    return {
        "answer": answer or "Không tạo được câu trả lời.",
        "sources": sources,
        "category": "RAG",
        "confidence": round(min(0.95, 0.4 + avg_score), 2),
        "mode": "rag-ollama",
    }
