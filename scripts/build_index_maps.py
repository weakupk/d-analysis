import argparse
import csv
import struct
from pathlib import Path

INDEX_START = 0x6000
RECORD_SIZE = 16
DEFAULT_FILES = ["DAY_2.DAT", "MIN1_2.DAT", "MIN_2.DAT", "ReportCps_2.DAT"]


def read_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def market_from_path(path: Path) -> str:
    s = str(path).lower()
    if "\\sh\\" in s or "/sh/" in s:
        return "SH"
    if "\\sz\\" in s or "/sz/" in s:
        return "SZ"
    return "UNK"


def parse_index_file(path: Path):
    data = read_bytes(path)
    rows = []
    if len(data) <= INDEX_START:
        return rows

    for offset in range(INDEX_START, len(data) - RECORD_SIZE + 1, RECORD_SIZE):
        rec = data[offset:offset + RECORD_SIZE]
        code_bytes = rec[0:6]
        if not all(48 <= b <= 57 for b in code_bytes):
            continue
        code = code_bytes.decode("ascii", errors="ignore")
        if len(code) != 6:
            continue

        block_no = struct.unpack_from("<I", rec, 12)[0]
        rows.append({
            "file_name": path.name,
            "market": market_from_path(path),
            "code": code,
            "index_offset": offset,
            "block_no": block_no,
            "block_offset": block_no * 8192,
            "raw_hex": rec.hex(" "),
        })
    return rows


def write_outputs(rows, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "index_maps.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "file_name", "market", "code", "index_offset", "block_no", "block_offset", "raw_hex"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Build stock index maps from Dazhihui index files.")
    parser.add_argument("--data-root", default=r"D:\Program\dzh365(64)\data")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    out_dir = Path(args.out_dir)

    rows = []
    for sub in ["sh", "sz", "SH", "SZ"]:
        base = data_root / sub
        if not base.exists():
            continue
        for name in DEFAULT_FILES:
            path = base / name
            if path.exists():
                rows.extend(parse_index_file(path))

    if not rows:
        raise SystemExit("No index files found.")

    write_outputs(rows, out_dir)


if __name__ == "__main__":
    main()
