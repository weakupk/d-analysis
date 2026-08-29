"""
export_block_bin.py — Export a raw 8192-byte stock block to outputs/stocks/{code}_block.bin

This is the upstream input step for the semantic analysis pipeline:

    1. export_block_bin.py          → outputs/stocks/{code}_block.bin
    2. extract_block_fields_semantic.py → outputs/stocks/{code}_semantic_fields.json/.txt
    3. compare_semantic_fields.py   → outputs/stocks/semantic_fields_compare.json/.txt
    4. summarize_semantic_comparison.py → outputs/stocks/semantic_fields_compare_summary.*
    5. find_variable_offsets.py     → outputs/stocks/variable_offsets_summary.*

Usage:
    python scripts/export_block_bin.py --code 600519
    python scripts/export_block_bin.py --code 600519 --code 000001 --code 300750
    python scripts/export_block_bin.py --code 600519 \\
        --plan outputs/export_plan.csv \\
        --data-root D:\\Program\\dzh365(64)\\data \\
        --out-dir outputs/stocks
"""

import argparse
import csv
from pathlib import Path

BLOCK_SIZE = 8192


class ExportError(Exception):
    """Raised for recoverable per-code export failures."""


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_block(path: Path, block_offset: int) -> bytes:
    with open(path, "rb") as f:
        f.seek(block_offset)
        data = f.read(BLOCK_SIZE)
    if len(data) != BLOCK_SIZE:
        raise ExportError(
            f"Expected {BLOCK_SIZE} bytes at offset {block_offset} in {path}, "
            f"got {len(data)}"
        )
    return data


def export_one(code: str, plan_rows: list, data_root: Path, out_dir: Path) -> Path:
    """Export the raw block binary for a single stock code.

    Returns the path of the written .bin file.
    Raises ExportError with a clear message if any required input is missing.
    """
    row = next((r for r in plan_rows if r.get("code") == code), None)
    if row is None:
        raise ExportError(f"[{code}] Code not found in export plan")

    index_file = row.get("index_file_name", "")
    if not index_file:
        raise ExportError(f"[{code}] No index_file_name in export plan row")

    block_offset_str = row.get("block_offset", "0") or "0"
    try:
        block_offset = int(block_offset_str)
    except ValueError:
        raise ExportError(f"[{code}] Invalid block_offset value: {block_offset_str!r}")

    candidates = [
        data_root / "sh" / index_file,
        data_root / "sz" / index_file,
        data_root / "SH" / index_file,
        data_root / "SZ" / index_file,
    ]
    source_path = next((p for p in candidates if p.exists()), None)
    if source_path is None:
        searched = ", ".join(str(p) for p in candidates)
        raise ExportError(
            f"[{code}] Source file '{index_file}' not found. Searched:\n  {searched}"
        )

    block = read_block(source_path, block_offset)

    out_dir.mkdir(parents=True, exist_ok=True)
    bin_path = out_dir / f"{code}_block.bin"
    with open(bin_path, "wb") as f:
        f.write(block)

    return bin_path


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Export raw 8192-byte stock block(s) to outputs/stocks/{code}_block.bin. "
            "Required upstream step before running extract_block_fields_semantic.py."
        )
    )
    parser.add_argument(
        "--code",
        required=True,
        action="append",
        dest="codes",
        metavar="CODE",
        help="Stock code to export (e.g. 600519). Repeat for multiple codes.",
    )
    parser.add_argument(
        "--plan",
        default=r"outputs/export_plan.csv",
        help="Path to export_plan.csv (default: outputs/export_plan.csv)",
    )
    parser.add_argument(
        "--data-root",
        default=r"D:\Program\dzh365(64)\data",
        help="Root directory containing sh/ and sz/ data subdirectories",
    )
    parser.add_argument(
        "--out-dir",
        default=r"outputs/stocks",
        help="Output directory for *_block.bin files (default: outputs/stocks)",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        raise SystemExit(f"Export plan not found: {plan_path}")

    plan_rows = load_csv(plan_path)
    data_root = Path(args.data_root)
    out_dir = Path(args.out_dir)

    errors = []
    for code in args.codes:
        try:
            bin_path = export_one(code, plan_rows, data_root, out_dir)
            print(f"Saved: {bin_path}")
        except ExportError as exc:
            errors.append(str(exc))

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  {err}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
