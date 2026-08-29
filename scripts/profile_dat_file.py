import argparse
import json
import math
from pathlib import Path


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    ent = 0.0
    n = len(data)
    for c in freq.values():
        p = c / n
        ent -= p * math.log2(p)
    return ent


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    printable = sum(1 for b in data if 32 <= b <= 126 or b in (9, 10, 13))
    return printable / len(data)


def main():
    parser = argparse.ArgumentParser(description="Profile a DAT file")
    parser.add_argument("--file", required=True, help="Input file path")
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    data = path.read_bytes()
    profile = {
        "file": str(path),
        "size": len(data),
        "entropy": round(shannon_entropy(data), 4),
        "printable_ratio": round(printable_ratio(data), 4),
        "head_hex": data[:256].hex(),
        "tail_hex": data[-256:].hex() if len(data) >= 256 else data.hex(),
    }

    text = json.dumps(profile, ensure_ascii=False, indent=2)
    print(text)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Saved profile to: {out_path}")


if __name__ == "__main__":
    main()
