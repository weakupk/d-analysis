import csv
import random
import struct
from pathlib import Path

OUT_DIR = Path(r"D:\Program\dzh365(64)\analysis\outputs")
INDEX_CSV_PATH = OUT_DIR

SH_DAY_CSV = OUT_DIR / "SH_DAY_2_index_map.csv"
SZ_DAY_CSV = OUT_DIR / "SZ_DAY_2_index_map.csv"

SH_INFOEX = Path(r"D:\Program\dzh365(64)\data\sh\INFOEX.DAT")
SZ_INFOEX = Path(r"D:\Program\dzh365(64)\data\sz\INFOEX.DAT")

SH_DAY_DAT = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
SZ_DAY_DAT = Path(r"D:\Program\dzh365(64)\data\sz\DAY_2.DAT.dat")

def load_index_map(csv_path: Path):
    mapping = {}
    if not csv_path.exists():
        return mapping
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["code"]] = {
                "block_no": int(row["block_no"]),
                "block_offset_hex": row["block_offset_hex"],
                "block_offset_bytes": int(row["block_offset_bytes"]),
            }
    return mapping

def read_block_header(dat_path: Path, block_no: int):
    if not dat_path.exists():
        return None
    offset = block_no * 8192
    with open(dat_path, "rb") as f:
        f.seek(offset)
        head = f.read(16)
        if len(head) < 16:
            return None
        rec_count, comp_size = struct.unpack("<II", head[:8])
        comp_type = hex(head[8])
        uncomp_size = head[9] | (head[10] << 8) | (head[11] << 16)
        return {
            "rec_count": rec_count,
            "comp_size": comp_size,
            "comp_type": comp_type,
            "uncomp_size": uncomp_size,
        }

def find_infoex_strings(infoex_path: Path, code: str):
    if not infoex_path.exists():
        return ""
    with open(infoex_path, "rb") as f:
        data = f.read()

    code_bytes = code.encode("ascii")
    pos = data.find(code_bytes)
    if pos == -1:
        return ""

    # Extract ascii / gbk strings near code_bytes
    chunk = data[max(0, pos-16):min(len(data), pos+64)]
    # Filter printable GBK / ASCII strings
    try:
        # split by null bytes
        parts = [p.decode("gbk", errors="ignore").strip() for p in chunk.split(b"\x00") if p.strip()]
        return " | ".join(parts[:5])
    except Exception:
        return ""

def main():
    random.seed(2026) # Fixed seed for reproducible sample

    sh_day_map = load_index_map(SH_DAY_CSV)
    sz_day_map = load_index_map(SZ_DAY_CSV)

    sh_min1_map = load_index_map(OUT_DIR / "SH_MIN1_2_index_map.csv")
    sz_min1_map = load_index_map(OUT_DIR / "SZ_MIN1_2_index_map.csv")

    sh_min_map = load_index_map(OUT_DIR / "SH_MIN_2_index_map.csv")
    sz_min_map = load_index_map(OUT_DIR / "SZ_MIN_2_index_map.csv")

    sh_rpt_map = load_index_map(OUT_DIR / "SH_ReportCps_2_index_map.csv")
    sz_rpt_map = load_index_map(OUT_DIR / "SZ_ReportCps_2_index_map.csv")

    # Select 10 common/random stocks from SH (prefer 600xxx, 601xxx, 603xxx, 688xxx)
    sh_codes_all = sorted(list(sh_day_map.keys()))
    # Select a mix of famous A-shares in SH
    sh_famous = ["600000", "600036", "600519", "601318", "600016", "600028", "600030", "600887", "601398", "688981"]
    sh_selected = [c for c in sh_famous if c in sh_day_map]
    if len(sh_selected) < 10:
        remaining = [c for c in sh_codes_all if c not in sh_selected and c.startswith(("60", "68"))]
        sh_selected.extend(random.sample(remaining, 10 - len(sh_selected)))

    # Select 10 common/random stocks from SZ (prefer 000xxx, 002xxx, 300xxx)
    sz_codes_all = sorted(list(sz_day_map.keys()))
    sz_famous = ["000001", "000002", "000651", "000858", "002415", "002594", "300015", "300059", "300750", "002230"]
    sz_selected = [c for c in sz_famous if c in sz_day_map]
    if len(sz_selected) < 10:
        remaining = [c for c in sz_codes_all if c not in sz_selected and c.startswith(("00", "30"))]
        sz_selected.extend(random.sample(remaining, 10 - len(sz_selected)))

    output_rows = []

    # Process SH
    for code in sh_selected:
        day_info = sh_day_map.get(code, {})
        min1_info = sh_min1_map.get(code, {})
        min_info = sh_min_map.get(code, {})
        rpt_info = sh_rpt_map.get(code, {})

        blk_no = day_info.get("block_no", -1)
        header_info = read_block_header(SH_DAY_DAT, blk_no) if blk_no >= 0 else None
        infoex_str = find_infoex_strings(SH_INFOEX, code)

        output_rows.append({
            "market": "SH (沪市)",
            "stock_code": code,
            "infoex_context_preview": infoex_str,
            "day_block_no": day_info.get("block_no", ""),
            "day_block_offset_hex": day_info.get("block_offset_hex", ""),
            "day_record_count": header_info["rec_count"] if header_info else "",
            "day_comp_type": header_info["comp_type"] if header_info else "",
            "day_comp_size": header_info["comp_size"] if header_info else "",
            "day_uncomp_size": header_info["uncomp_size"] if header_info else "",
            "min1_block_no": min1_info.get("block_no", ""),
            "min1_block_offset_hex": min1_info.get("block_offset_hex", ""),
            "min5_block_no": min_info.get("block_no", ""),
            "min5_block_offset_hex": min_info.get("block_offset_hex", ""),
            "tick_report_block_no": rpt_info.get("block_no", ""),
            "tick_report_offset_hex": rpt_info.get("block_offset_hex", ""),
        })

    # Process SZ
    for code in sz_selected:
        day_info = sz_day_map.get(code, {})
        min1_info = sz_min1_map.get(code, {})
        min_info = sz_min_map.get(code, {})
        rpt_info = sz_rpt_map.get(code, {})

        blk_no = day_info.get("block_no", -1)
        header_info = read_block_header(SZ_DAY_DAT, blk_no) if blk_no >= 0 else None
        infoex_str = find_infoex_strings(SZ_INFOEX, code)

        output_rows.append({
            "market": "SZ (深市)",
            "stock_code": code,
            "infoex_context_preview": infoex_str,
            "day_block_no": day_info.get("block_no", ""),
            "day_block_offset_hex": day_info.get("block_offset_hex", ""),
            "day_record_count": header_info["rec_count"] if header_info else "",
            "day_comp_type": header_info["comp_type"] if header_info else "",
            "day_comp_size": header_info["comp_size"] if header_info else "",
            "day_uncomp_size": header_info["uncomp_size"] if header_info else "",
            "min1_block_no": min1_info.get("block_no", ""),
            "min1_block_offset_hex": min1_info.get("block_offset_hex", ""),
            "min5_block_no": min_info.get("block_no", ""),
            "min5_block_offset_hex": min_info.get("block_offset_hex", ""),
            "tick_report_block_no": rpt_info.get("block_no", ""),
            "tick_report_offset_hex": rpt_info.get("block_offset_hex", ""),
        })

    out_csv = OUT_DIR / "sample_20_stocks_integrated.csv"
    fieldnames = [
        "market", "stock_code", "infoex_context_preview",
        "day_block_no", "day_block_offset_hex", "day_record_count",
        "day_comp_type", "day_comp_size", "day_uncomp_size",
        "min1_block_no", "min1_block_offset_hex",
        "min5_block_no", "min5_block_offset_hex",
        "tick_report_block_no", "tick_report_offset_hex"
    ]

    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Successfully generated integrated verification CSV: {out_csv}")

if __name__ == "__main__":
    main()
