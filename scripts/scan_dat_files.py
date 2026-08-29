import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Scan data directory for candidate DAT files")
    parser.add_argument("--root", required=True, help="Root data directory, e.g. D:\\Program\\dzh365(64)\\data")
    parser.add_argument("--output", default="outputs/dat_profiles/file_index.json", help="Output index file")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Missing root directory: {root}")

    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".dat", ".bin", ".raw"}:
            files.append(str(p))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Found {len(files)} candidate files")
    print(f"Saved index to: {out_path}")


if __name__ == "__main__":
    main()
