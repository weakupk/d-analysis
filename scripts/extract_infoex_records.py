import argparse
import csv
import json
import re
import struct
from collections import defaultdict
from pathlib import Path

CODE_RE = re.compile(rb"\b\d{6}\b")


def read_file(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def decode_ascii(data: bytes) -> str:
    return data.decode("ascii", errors="ignore")


def hexdump(data: bytes, width: int = 16) -> str:
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        lines.append(f"{i:04x}: {chunk.hex(' ')}")
    return "\n".join(lines)


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


def read_u32_le(data: bytes, offset: int):
    if offset + 4 > len(data):
        return None
    return struct.unpack_from("<I", data, offset)[0]


def read_f32_le(data: bytes, offset: int):
    if offset + 4 > len(data):
        return None
    return struct.unpack_from("<f", data, offset)[0]


def find_codes(data: bytes):
    matches = []
    for m in CODE_RE.finditer(data):
        matches.append((m.start(), m.group(0).decode("ascii")))
    return matches


def context_bytes(data: bytes, pos: int, before: int, after: int):
    start = max(0, pos - before)
    end = min(len(data), pos + 6 + after)
    return data[start:end], start


def analyze(path: Path, out_dir: Path, before: int, after: int):
    data = read_file(path)
    codes = find_codes(data)
    by_code = defaultdict(list)
    for pos, code in codes:
        by_code[code].append(pos)

    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / "INFOEX_records_summary.json"
    csv_path = out_dir / "INFOEX_records.csv"
    txt_path = out_dir / "INFOEX_records_context.txt"

    rows = []
    summary = {
        "path": str(path),
        "size": len(data),
        "total_codes": len(codes),
        "unique_codes": len(by_code),
        "codes": [],
    }

    for code, positions in sorted(by_code.items(), key=lambda kv: (kv[0])):
        summary["codes"].append({
            "code": code,
            "count": len(positions),
            "first": positions[0],
            "positions": positions[:20],
        })
        for idx, pos in enumerate(positions[:5], start=1):
            chunk, start = context_bytes(data, pos, before, after)
            strings = extract_strings(chunk)
            rows.append({
                "code": code,
                "occurrence": idx,
                "position": pos,
                "context_start": start,
                "u32_before_16": read_u32_le(data, max(0, pos - 16)),
                "u32_at_0": read_u32_le(data, pos),
                "u32_after_6": read_u32_le(data, pos + 6),
                "f32_after_16": read_f32_le(data, pos + 16),
                "strings": " | ".join(strings[:10]),
                "hexdump": hexdump(chunk),
            })

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "code", "occurrence", "position", "context_start",
            "u32_before_16", "u32_at_0", "u32_after_6", "f32_after_16",
            "strings", "hexdump"
        ])
        writer.writeheader()
        writer.writerows(rows)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"PATH: {path}\n")
        f.write(f"SIZE: {len(data)}\n")
        f.write(f"TOTAL_CODES: {len(codes)}\n")
        f.write(f"UNIQUE_CODES: {len(by_code)}\n\n")
        for row in rows[:200]:
            f.write(f"=== {row['code']} #{row['occurrence']} at {row['position']} ===\n")
            f.write(f"u32_before_16={row['u32_before_16']} u32_at_0={row['u32_at_0']} u32_after_6={row['u32_after_6']} f32_after_16={row['f32_after_16']}\n")
            if row["strings"]:
                f.write(f"strings: {row['strings']}\n")
            f.write(row["hexdump"] + "\n\n")

    print(f"Saved: {summary_path}")
    print(f"Saved: {csv_path}")
    print(f"Saved: {txt_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract and summarize INFOEX.DAT code-centered records.")
    parser.add_argument("--input", default=r"D:\Program\dzh365(64)\data\SH\INFOEX.DAT")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs")
    parser.add_argument("--before", type=int, default=64)
    parser.add_argument("--after", type=int, default=128)
    args = parser.parse_args()

    analyze(Path(args.input), Path(args.out_dir), args.before, args.after)


if __name__ == "__main__":
    main()
