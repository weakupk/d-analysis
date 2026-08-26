import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = ["code", "market", "index_file_name", "block_no", "block_offset"]


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description="Generate a compact per-stock export plan.")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs")
    parser.add_argument("--summary", default=r"D:\Program\dzh365(64)\analysis\outputs\master_index_summary.csv")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    rows = load_csv(Path(args.summary))

    out_path = out_dir / "export_plan.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in REQUIRED_COLUMNS})

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
