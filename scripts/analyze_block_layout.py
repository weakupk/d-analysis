import argparse
import json
from collections import Counter
from pathlib import Path

BLOCK_SIZE = 8192


def load_block(path: Path) -> bytes:
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != BLOCK_SIZE:
        raise SystemExit(f"Expected {BLOCK_SIZE} bytes, got {len(data)} from {path}")
    return data


def find_runs(data: bytes):
    runs = []
    start = None
    for i, b in enumerate(data):
        if b != 0 and start is None:
            start = i
        elif b == 0 and start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(data) - 1))
    return runs


def chunk_counter(data: bytes, size: int):
    c = Counter()
    for i in range(0, len(data) - size + 1, size):
        c[data[i:i + size]] += 1
    return c


def fmt_hex(n: int) -> str:
    return f"0x{n:04x}"


def main():
    parser = argparse.ArgumentParser(description="Analyze the layout of a single stock block.")
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--in-file", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks\600519_block.bin")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks")
    args = parser.parse_args()

    block = load_block(Path(args.in_file))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = find_runs(block)
    nonzero_bytes = sum(end - start + 1 for start, end in runs)

    stats = {
        "code": args.code,
        "block_size": len(block),
        "nonzero_bytes": nonzero_bytes,
        "zero_bytes": len(block) - nonzero_bytes,
        "nonzero_runs": [
            {"start": start, "end": end, "start_hex": fmt_hex(start), "end_hex": fmt_hex(end), "length": end - start + 1}
            for start, end in runs
        ],
        "top_8byte_chunks": [
            {"hex": chunk.hex(" "), "count": count}
            for chunk, count in chunk_counter(block, 8).most_common(20)
        ],
        "top_16byte_chunks": [
            {"hex": chunk.hex(" "), "count": count}
            for chunk, count in chunk_counter(block, 16).most_common(20)
        ],
    }

    json_path = out_dir / f"{args.code}_layout.json"
    txt_path = out_dir / f"{args.code}_layout.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"code: {args.code}\n")
        f.write(f"block_size: {len(block)}\n")
        f.write(f"nonzero_bytes: {nonzero_bytes}\n")
        f.write(f"zero_bytes: {len(block) - nonzero_bytes}\n")
        f.write("\nnonzero runs:\n")
        for r in stats["nonzero_runs"]:
            f.write(f"  {r['start_hex']} - {r['end_hex']}  len={r['length']}\n")
        f.write("\ntop 8-byte chunks:\n")
        for item in stats["top_8byte_chunks"]:
            f.write(f"  {item['count']:>4}  {item['hex']}\n")
        f.write("\ntop 16-byte chunks:\n")
        for item in stats["top_16byte_chunks"]:
            f.write(f"  {item['count']:>4}  {item['hex']}\n")

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
