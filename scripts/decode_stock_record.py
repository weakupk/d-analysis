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


def main():
    parser = argparse.ArgumentParser(description="Decode one raw stock record")
    parser.add_argument("--input", required=True, help="JSON line or hex record input")
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    args = parser.parse_args()

    inp = Path(args.input)
    if inp.exists():
        text = inp.read_text(encoding="utf-8").strip()
    else:
        text = args.input.strip()

    try:
        obj = json.loads(text)
        raw_hex = obj["hex"]
    except Exception:
        raw_hex = text

    decoded = decode_record(raw_hex)
    out_text = json.dumps(decoded, ensure_ascii=False, indent=2)
    print(out_text)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text, encoding="utf-8")
        print(f"Saved decoded record to: {out_path}")


if __name__ == "__main__":
    main()
