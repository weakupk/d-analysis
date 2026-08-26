import csv
import struct
from pathlib import Path

SH_DIR = Path(r"D:\Program\dzh365(64)\data\sh")
SZ_DIR = Path(r"D:\Program\dzh365(64)\data\sz")
OUT_DIR = Path(r"D:\Program\dzh365(64)\analysis\outputs")

INDEX_FILES = [
    "DAY_2.DAT",
    "MIN1_2.DAT",
    "MIN_2.DAT",
    "ReportCps_2.DAT",
]

def parse_dzh_index(index_path: Path):
    if not index_path.exists():
        return []

    with open(index_path, "rb") as f:
        f.seek(0x6000) # Index entries start at 0x6000 in DFCJ container
        data = f.read()

    entries = []
    for offset in range(0, len(data), 16):
        chunk = data[offset:offset+16]
        if len(chunk) < 16:
            break
        code_bytes = chunk[:6]
        if code_bytes.isdigit():
            code = code_bytes.decode("ascii")
            block_no = struct.unpack("<I", chunk[12:16])[0]
            entries.append({
                "code": code,
                "file_offset_hex": f"0x{0x6000 + offset:08x}",
                "block_no": block_no,
                "block_offset_hex": f"0x{block_no * 8192:08x}",
                "block_offset_bytes": block_no * 8192,
            })

    return entries

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_summary = []

    for market_dir, market_name in [(SH_DIR, "SH"), (SZ_DIR, "SZ")]:
        for idx_filename in INDEX_FILES:
            idx_path = market_dir / idx_filename
            entries = parse_dzh_index(idx_path)
            if entries:
                csv_filename = f"{market_name}_{idx_filename.replace('.DAT', '')}_index_map.csv"
                csv_path = OUT_DIR / csv_filename

                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "code", "file_offset_hex", "block_no", "block_offset_hex", "block_offset_bytes"
                    ])
                    writer.writeheader()
                    writer.writerows(entries)

                data_path = Path(str(idx_path) + ".dat")
                data_size = data_path.stat().st_size if data_path.exists() else 0

                summary_item = {
                    "market": market_name,
                    "index_file": idx_filename,
                    "total_securities": len(entries),
                    "csv_exported": str(csv_path),
                    "data_file": data_path.name,
                    "data_file_size_mb": round(data_size / (1024*1024), 2),
                }
                all_summary.append(summary_item)
                print(f"[{market_name}] Parsed {len(entries):>5} codes from {idx_filename:<15} -> Saved: {csv_path.name}")

    print("\n--- INDEX PARSING SUMMARY ---")
    for item in all_summary:
        print(f"Market: {item['market']} | File: {item['index_file']:<15} | Securities: {item['total_securities']:<5} | DataSize: {item['data_file_size_mb']} MB")

if __name__ == "__main__":
    main()
