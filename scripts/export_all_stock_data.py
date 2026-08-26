import argparse
import csv
import json
import re
import struct
from collections import defaultdict
from pathlib import Path

CODE_RE = re.compile(rb"\b\d{6}\b")


def read_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def extract_strings(data: bytes, min_len: int = 3):
    out = []
    buf = []
    for b in data:
        if 32 <= b <= 126:
            buf.append(chr(b))
        else:
            if len(buf) >= min_len:
                out.append("".join(buf))
            buf = []
    if len(buf) >= min_len:
        out.append("".join(buf))
    return out


def hexdump(data: bytes, width: int = 16) -> str:
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        lines.append(f"{i:04x}: {chunk.hex(' ')}")
    return "\n".join(lines)


def read_u32_le(data: bytes, offset: int):
    if offset < 0 or offset + 4 > len(data):
        return None
    return struct.unpack_from("<I", data, offset)[0]


def read_f32_le(data: bytes, offset: int):
    if offset < 0 or offset + 4 > len(data):
        return None
    return struct.unpack_from("<f", data, offset)[0]


def find_codes(data: bytes):
    return [(m.start(), m.group(0).decode("ascii")) for m in CODE_RE.finditer(data)]


def market_from_path(path: Path) -> str:
    s = str(path).lower()
    if "\\sh\\" in s or "/sh/" in s:
        return "SH"
    if "\\sz\\" in s or "/sz/" in s:
        return "SZ"
    return "UNK"


def build_master_infoex(infoex_path: Path, before: int = 64, after: int = 128):
    data = read_bytes(infoex_path)
    codes = find_codes(data)
    by_code = defaultdict(list)
    for pos, code in codes:
        by_code[code].append(pos)

    records = []
    for code in sorted(by_code):
        pos = by_code[code][0]
        start = max(0, pos - before)
        end = min(len(data), pos + 6 + after)
        chunk = data[start:end]
        records.append({
            "code": code,
            "market": market_from_path(infoex_path),
            "infoex_path": str(infoex_path),
            "infoex_offset": pos,
            "infoex_context_start": start,
            "u32_before_16": read_u32_le(data, pos - 16),
            "u32_at_0": read_u32_le(data, pos),
            "u32_after_6": read_u32_le(data, pos + 6),
            "f32_after_16": read_f32_le(data, pos + 16),
            "strings": " | ".join(extract_strings(chunk)[:10]),
            "hexdump": hexdump(chunk),
        })
    return records


def write_master_files(records, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "master_stocks.csv"
    json_path = out_dir / "master_stocks.json"

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "code", "market", "infoex_path", "infoex_offset",
            "infoex_context_start", "u32_before_16", "u32_at_0",
            "u32_after_6", "f32_after_16", "strings", "hexdump"
        ])
        writer.writeheader()
        writer.writerows(records)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")


def export_placeholders(records, out_dir: Path):
    export_dir = out_dir / "exported"
    export_dir.mkdir(parents=True, exist_ok=True)
    for r in records:
        code = r["code"]
        day_path = export_dir / f"{code}_day.csv"
        with open(day_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["code", "status", "note"])
            writer.writerow([code, "pending", "block/index decoder not yet wired"])
    print(f"Saved placeholder exports under: {export_dir}")


def main():
    parser = argparse.ArgumentParser(description="Master pipeline for Dazhihui stock data reconstruction.")
    parser.add_argument("--data-root", default=r"D:\Program\dzh365(64)\data")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    out_dir = Path(args.out_dir)

    infoex_candidates = [
        data_root / "sh" / "INFOEX.DAT",
        data_root / "sz" / "INFOEX.DAT",
        data_root / "SH" / "INFOEX.DAT",
        data_root / "SZ" / "INFOEX.DAT",
    ]

    records = []
    for p in infoex_candidates:
        if p.exists():
            records.extend(build_master_infoex(p))

    if not records:
        raise SystemExit("No INFOEX.DAT found under data-root.")

    write_master_files(records, out_dir)
    export_placeholders(records[:20], out_dir)


if __name__ == "__main__":
    main()
