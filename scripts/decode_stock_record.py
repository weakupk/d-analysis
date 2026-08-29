import argparse
import json
from pathlib import Path


def decode_record(raw_hex: str) -> dict:
    data = bytes.fromhex(raw_hex)
    result = {
        "raw_size": len(data),
        "code_ascii_preview": data[:16].decode("ascii", errors="ignore"),
        "raw_hex_head": data[:64].hex(),
    }
    return result


def load_inputs(input_arg: str) -> list[dict]:
    path = Path(input_arg)
    if path.exists():
        if path.suffix.lower() == ".jsonl":
            records = []
            with path.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as e:
                        raise SystemExit(f"Invalid JSON on line {line_no} in {path}: {e}")
                    records.append(obj)
            return records

        text = path.read_text(encoding="utf-8").strip()
    else:
        text = input_arg.strip()

    if not text:
        return []

    try:
        obj = json.loads(text)
        return [obj]
    except json.JSONDecodeError:
        return [{"hex": text}]


def main():
    parser = argparse.ArgumentParser(description="Decode one or more raw stock records")
    parser.add_argument("--input", required=True, help="JSONL file, JSON object, or hex record input")
    parser.add_argument("--output", default=None, help="Optional JSON or JSONL output path")
    args = parser.parse_args()

    inputs = load_inputs(args.input)
    if not inputs:
        raise SystemExit("No input records found")

    decoded_records = []
    for item in inputs:
        if isinstance(item, dict) and "hex" in item:
            raw_hex = item["hex"]
        else:
            raise SystemExit("Each input record must be a JSON object containing a 'hex' field")
        decoded = decode_record(raw_hex)
        if isinstance(item, dict):
            decoded.update({k: v for k, v in item.items() if k != "hex"})
        decoded_records.append(decoded)

    if len(decoded_records) == 1 and (not args.output or not str(args.output).lower().endswith(".jsonl")):
        out_text = json.dumps(decoded_records[0], ensure_ascii=False, indent=2)
    else:
        out_text = "\n".join(json.dumps(r, ensure_ascii=False) for r in decoded_records)

    print(out_text)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text, encoding="utf-8")
        print(f"Saved decoded record(s) to: {out_path}")


if __name__ == "__main__":
    main()
