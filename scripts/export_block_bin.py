"""Export a raw 8192-byte block file for a given stock code.

This is the first step in the semantic-field analysis workflow:

  Step 1 - Export raw block:
      python scripts/export_block_bin.py --code 600519

  Step 2 - Extract semantic fields from the block:
      python scripts/extract_block_fields_semantic.py --code 600519
          --in-file outputs/stocks/600519_block.bin
          --out-dir outputs/stocks

  Step 3 - Compare semantic fields across stocks:
      python scripts/compare_semantic_fields.py

  Step 4 - Summarize the comparison:
      python scripts/summarize_semantic_comparison.py

  Step 5 - Find variable (business) offsets across multiple stocks:
      python scripts/find_variable_offsets.py
          --code 600519 --code 000001 --code 000858

The script reads the export plan at outputs/export_plan.csv to locate the
correct source .DAT file and byte offset, then writes:
  outputs/stocks/{code}_block.bin        - raw 8192-byte block
  outputs/stocks/{code}_block_header.json - provenance metadata
  outputs/stocks/{code}_block_dump.txt   - hex dump for quick inspection
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# Re-use the implementation in dump_stock_block to avoid duplication.
# Both scripts share the same logic; this script provides the clearly-named
# entry point requested by the analysis workflow documentation.
_SCRIPTS_DIR = Path(__file__).parent


def _import_dump_module():
    spec = importlib.util.spec_from_file_location(
        "dump_stock_block", _SCRIPTS_DIR / "dump_stock_block.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Export a raw 8192-byte block file for a stock code.\n"
            "This is the upstream step required before running "
            "extract_block_fields_semantic.py or find_variable_offsets.py."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument(
        "--plan",
        default=r"D:\Program\dzh365(64)\analysis\outputs\export_plan.csv",
        help="Path to export_plan.csv (maps stock codes to source files and offsets).",
    )
    parser.add_argument(
        "--data-root",
        default=r"D:\Program\dzh365(64)\data",
        help="Root directory containing the raw .DAT data files.",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
        help="Output directory for *_block.bin and companion files.",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(
            f"ERROR: Export plan not found: {plan_path}\n"
            "       Generate it first with: python scripts/build_export_plan.py",
            file=sys.stderr,
        )
        sys.exit(1)

    data_root = Path(args.data_root)
    if not data_root.exists():
        print(
            f"ERROR: Data root directory not found: {data_root}\n"
            "       Ensure the DZH365 data path is correct.",
            file=sys.stderr,
        )
        sys.exit(1)

    dump = _import_dump_module()

    plan_rows = dump.load_csv(plan_path)
    row = next((r for r in plan_rows if r.get("code") == args.code), None)
    if not row:
        print(
            f"ERROR: Stock code '{args.code}' not found in export plan: {plan_path}\n"
            "       Check that the code is correct or regenerate the plan.",
            file=sys.stderr,
        )
        sys.exit(1)

    index_file = row.get("index_file_name", "")
    block_offset = int(row.get("block_offset", "0") or 0)
    if not index_file:
        print(
            f"ERROR: No index file mapping for code '{args.code}' in export plan.",
            file=sys.stderr,
        )
        sys.exit(1)

    candidates = [
        data_root / "sh" / index_file,
        data_root / "sz" / index_file,
        data_root / "SH" / index_file,
        data_root / "SZ" / index_file,
    ]
    source_path = next((p for p in candidates if p.exists()), None)
    if source_path is None:
        checked = "\n  ".join(str(p) for p in candidates)
        print(
            f"ERROR: Source file '{index_file}' not found under {data_root}.\n"
            f"  Checked:\n  {checked}",
            file=sys.stderr,
        )
        sys.exit(1)

    block = dump.read_block(source_path, block_offset)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bin_path = out_dir / f"{args.code}_block.bin"
    json_path = out_dir / f"{args.code}_block_header.json"
    txt_path = out_dir / f"{args.code}_block_dump.txt"

    with open(bin_path, "wb") as f:
        f.write(block)

    header = {
        "code": args.code,
        "source_path": str(source_path),
        "index_file_name": index_file,
        "block_offset": block_offset,
        "block_size": len(block),
        "head_hex": block[:64].hex(" "),
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(header, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(dump.hexdump(block))

    print(f"Saved: {bin_path}")
    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")
    print()
    print("Next step: extract semantic fields with")
    print(f"  python scripts/extract_block_fields_semantic.py --code {args.code} "
          f"--in-file {bin_path} --out-dir {out_dir}")


if __name__ == "__main__":
    main()
import sys
from pathlib import Path

# Re-use the implementation in dump_stock_block to avoid duplication.
# Both scripts share the same logic; this script provides the clearly-named
# entry point requested by the analysis workflow documentation.
_SCRIPTS_DIR = Path(__file__).parent


def _import_dump_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "dump_stock_block", _SCRIPTS_DIR / "dump_stock_block.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Export a raw 8192-byte block file for a stock code.\n"
            "This is the upstream step required before running "
            "extract_block_fields_semantic.py or find_variable_offsets.py."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument(
        "--plan",
        default=r"D:\Program\dzh365(64)\analysis\outputs\export_plan.csv",
        help="Path to export_plan.csv (maps stock codes to source files and offsets).",
    )
    parser.add_argument(
        "--data-root",
        default=r"D:\Program\dzh365(64)\data",
        help="Root directory containing the raw .DAT data files.",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
        help="Output directory for *_block.bin and companion files.",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(
            f"ERROR: Export plan not found: {plan_path}\n"
            "       Generate it first with: python scripts/build_export_plan.py",
            file=sys.stderr,
        )
        sys.exit(1)

    data_root = Path(args.data_root)
    if not data_root.exists():
        print(
            f"ERROR: Data root directory not found: {data_root}\n"
            "       Ensure the DZH365 data path is correct.",
            file=sys.stderr,
        )
        sys.exit(1)

    dump = _import_dump_module()

    plan_rows = dump.load_csv(plan_path)
    row = next((r for r in plan_rows if r.get("code") == args.code), None)
    if not row:
        print(
            f"ERROR: Stock code '{args.code}' not found in export plan: {plan_path}\n"
            "       Check that the code is correct or regenerate the plan.",
            file=sys.stderr,
        )
        sys.exit(1)

    index_file = row.get("index_file_name", "")
    block_offset = int(row.get("block_offset", "0") or 0)
    if not index_file:
        print(
            f"ERROR: No index file mapping for code '{args.code}' in export plan.",
            file=sys.stderr,
        )
        sys.exit(1)

    candidates = [
        data_root / "sh" / index_file,
        data_root / "sz" / index_file,
        data_root / "SH" / index_file,
        data_root / "SZ" / index_file,
    ]
    source_path = next((p for p in candidates if p.exists()), None)
    if source_path is None:
        checked = "\n  ".join(str(p) for p in candidates)
        print(
            f"ERROR: Source file '{index_file}' not found under {data_root}.\n"
            f"  Checked:\n  {checked}",
            file=sys.stderr,
        )
        sys.exit(1)

    block = dump.read_block(source_path, block_offset)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bin_path = out_dir / f"{args.code}_block.bin"

    import json

    json_path = out_dir / f"{args.code}_block_header.json"
    txt_path = out_dir / f"{args.code}_block_dump.txt"

    with open(bin_path, "wb") as f:
        f.write(block)

    header = {
        "code": args.code,
        "source_path": str(source_path),
        "index_file_name": index_file,
        "block_offset": block_offset,
        "block_size": len(block),
        "head_hex": block[:64].hex(" "),
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(header, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(dump.hexdump(block))

    print(f"Saved: {bin_path}")
    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")
    print()
    print("Next step: extract semantic fields with")
    print(f"  python scripts/extract_block_fields_semantic.py --code {args.code} "
          f"--in-file {bin_path} --out-dir {out_dir}")


if __name__ == "__main__":
    main()
