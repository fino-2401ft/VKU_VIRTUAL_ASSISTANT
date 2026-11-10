from __future__ import annotations

import argparse
import json
from pathlib import Path

from .fee_table_normalizer import (
    export_normalization,
    normalize_fee_docx,
    rename_fee_files,
)

ROOT = Path(__file__).resolve().parents[2]
FEE_DIR = ROOT / "data" / "pdfs" / "hoc-vu" / "hoc-phi"
OUT_DIR = ROOT / "data" / "normalized" / "hoc-phi"


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize VKU tuition fee DOCX tables")
    parser.add_argument("--rename", action="store_true", help="Rename files to hoc-phi-hoc-ki-*-yyyy-yyyy")
    parser.add_argument("--dry-run-rename", action="store_true")
    parser.add_argument("--file", type=str, default="", help="Only one filename")
    args = parser.parse_args()

    if args.rename or args.dry_run_rename:
        changes = rename_fee_files(FEE_DIR, dry_run=args.dry_run_rename)
        print(json.dumps({"rename_changes": changes}, ensure_ascii=False, indent=2))
        if args.dry_run_rename:
            return

    files = sorted(FEE_DIR.glob("*.docx"))
    if args.file:
        files = [FEE_DIR / args.file]
        files = [p for p in files if p.exists()]

    summary = []
    for path in files:
        result = normalize_fee_docx(path)
        paths = export_normalization(result, OUT_DIR)
        summary.append(
            {
                "file": path.name,
                "academic_year": result.academic_year,
                "semester": result.semester,
                "records": len(result.records),
                "available": result.validation["records_available"],
                "no_data": result.validation["records_no_data"],
                "validation_passed": result.validation["passed"],
                "outputs": {k: str(v) for k, v in paths.items()},
            }
        )
        print(
            f"[ok] {path.name}: records={len(result.records)} "
            f"available={result.validation['records_available']} "
            f"passed={result.validation['passed']}"
        )

    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Summary -> {OUT_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
