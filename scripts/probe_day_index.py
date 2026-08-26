import os
import re
import struct
from pathlib import Path

SH_DAY = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT")
SZ_DAY = Path(r"D:\Program\dzh365(64)\data\sz\DAY_2.DAT")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\day_index_probe.txt")

CODE_RE = re.compile(rb"\b\d{6}\b")

def analyze_day_index(path: Path):
    lines = []
    lines.append(f"=== ANALYZING INDEX FILE: {path} ===")
    if not path.exists():
        lines.append("File not found.")
        return "\n".join(lines)

    size = path.stat().st_size
    lines.append(f"Size: {size} bytes")

    with open(path, "rb") as f:
        data = f.read()

    # Search for 6-digit stock codes
    matches = list(CODE_RE.finditer(data))
    lines.append(f"Total 6-digit ASCII code matches: {len(matches)}")
    
    unique_codes = set(m.group(0).decode("ascii") for m in matches)
    lines.append(f"Unique 6-digit codes found: {len(unique_codes)}")

    if matches:
        lines.append("First 20 code matches with offset:")
        for m in matches[:20]:
            offset = m.start()
            code = m.group(0).decode("ascii")
            context = data[max(0, offset-16):min(len(data), offset+32)]
            lines.append(f"  Offset 0x{offset:08x} ({offset}): Code {code} | Context hex: {context.hex(' ')}")

    # Check for fixed block / record patterns
    # Read first 1024 bytes hex dump
    lines.append("\nFirst 256 bytes hex dump:")
    for i in range(0, min(256, len(data)), 16):
        chunk = data[i:i+16]
        hex_str = chunk.hex(" ")
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"  {i:04x}: {hex_str:<47}  |{ascii_str}|")

    lines.append("\n")
    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = []
    report.append("DAY_2.DAT INDEX STRUCTURE PROBE\n" + "="*50 + "\n")
    report.append(analyze_day_index(SH_DAY))
    report.append(analyze_day_index(SZ_DAY))

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Report written to: {OUT_FILE}")

if __name__ == "__main__":
    main()
