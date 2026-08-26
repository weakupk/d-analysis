import argparse
import csv
from collections import defaultdict
from pathlib import Path


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description="Merge master stock table with index maps.")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs")
    parser.add_argument("--master", default=r"D:\Program\dzh365(64)\analysis\outputs\master_stocks.csv")
    parser.add_argument("--index-maps", default=r"D:\Program\dzh365(64)\analysis\outputs\index_maps.csv")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    master_rows = load_csv(Path(args.master))
    index_rows = load_csv(Path(args.index_maps))

    by_code = defaultdict(list)
    for row in index_rows:
        by_code[row["code"]].append(row)

    merged = []
    for row in master_rows:
        code = row["code"]
        matches = by_code.get(code, [])
        if not matches:
            merged.append({**row, "index_file_name": "", "index_offset": "", "block_no": "", "block_offset": "", "index_raw_hex": ""})
            continue
        for m in matches:
            merged.append({
                **row,
                "index_file_name": m.get("file_name", ""),
                "index_offset": m.get("index_offset", ""),
                "block_no": m.get("block_no", ""),
                "block_offset": m.get("block_offset", ""),
                "index_raw_hex": m.get("raw_hex", ""),
            })

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "master_index_merged.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = list(merged[0].keys()) if merged else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged)

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
