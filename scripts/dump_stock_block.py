import argparse
import csv
import json
import struct
from pathlib import Path

BLOCK_SIZE = 8192


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_block(path: Path, block_offset: int) -> bytes:
    with open(path, "rb") as f:
        f.seek(block_offset)
        return f.read(BLOCK_SIZE)


def hexdump(data: bytes, width: int = 16) -> str:
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        lines.append(f"{i:04x}: {chunk.hex(' ')}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Dump a single stock block for reverse engineering.")
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--plan", default=r"D:\Program\dzh365(64)\analysis\outputs\export_plan.csv")
    parser.add_argument("--data-root", default=r"D:\Program\dzh365(64)\data")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks")
    args = parser.parse_args()

    plan_rows = load_csv(Path(args.plan))
    row = next((r for r in plan_rows if r.get("code") == args.code), None)
    if not row:
        raise SystemExit(f"Code {args.code} not found in export plan")

    index_file = row.get("index_file_name", "")
    block_offset = int(row.get("block_offset", "0") or 0)
    if not index_file:
        raise SystemExit(f"Code {args.code} has no index file mapping")

    data_root = Path(args.data_root)
    candidates = [data_root / "sh" / index_file, data_root / "sz" / index_file, data_root / "SH" / index_file, data_root / "SZ" / index_file]
    source_path = next((p for p in candidates if p.exists()), None)
    if source_path is None:
        raise SystemExit(f"Could not find source file {index_file} under {data_root}")

    block = read_block(source_path, block_offset)
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
        f.write(hexdump(block))

    print(f"Saved: {bin_path}")
    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
