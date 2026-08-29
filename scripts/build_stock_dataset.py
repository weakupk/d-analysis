import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build structured stock dataset from decoded records")
    parser.add_argument("--input", required=True, help="Decoded JSONL file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Missing input file: {inp}")

    records = []
    with inp.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(records)} records to: {out_path}")


if __name__ == "__main__":
    main()
