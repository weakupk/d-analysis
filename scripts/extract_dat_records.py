import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extract candidate records from a DAT file")
    parser.add_argument("--file", required=True, help="Input file path")
    parser.add_argument("--record-size", type=int, default=8192, help="Candidate record size")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    data = path.read_bytes()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for offset in range(0, len(data), args.record_size):
            chunk = data[offset:offset + args.record_size]
            if len(chunk) < args.record_size:
                break
            row = {
                "source_file": str(path),
                "offset": offset,
                "size": len(chunk),
                "hex": chunk.hex(),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1

    print(f"Extracted {count} candidate records to: {out_path}")


if __name__ == "__main__":
    main()
