import os
import re
import struct
from pathlib import Path

PATH = r"D:\Program\dzh365(64)\data\SH\INFOEX.DAT"
OUT = r"D:\Program\dzh365(64)\analysis\outputs\SH_INFOEX_probe_output.txt"

STRING_RE = re.compile(rb"[ -~]{4,}")

def read_head(path, n=1024):
    with open(path, "rb") as f:
        return f.read(n)

def extract_strings(data):
    out = []
    for s in STRING_RE.findall(data):
        try:
            out.append(s.decode("ascii", errors="ignore"))
        except Exception:
            pass
    return out

def parse_u32s(data, limit=32):
    vals = []
    for i in range(0, min(len(data), limit * 4), 4):
        if i + 4 <= len(data):
            vals.append(struct.unpack("<I", data[i:i+4])[0])
    return vals

def classify_file(name, data):
    upper = name.upper()
    strings = extract_strings(data[:4096])
    joined = " ".join(strings)

    if upper.endswith((".TXT", ".INI", ".XML")):
        return "text/config"
    if data[:4] == b"DFCJ":
        return "dzh-container-or-index-header"
    if re.search(r"\b(SH|SZ|HK)\d{6}\b", joined):
        return "security-code-containing"
    if len(data) >= 16 and data[:16].count(b"\x00") >= 8:
        return "sparse-or-index-like"
    if len(strings) >= 3:
        return "string-rich-binary"
    return "unknown-binary"

def analyze_file(path, out):
    p = Path(path)
    size = p.stat().st_size
    head = read_head(path, 1024)

    out.write("=" * 100 + "\n")
    out.write(f"FILE: {path}\n")
    out.write(f"SIZE: {size} bytes ({size / 1024:.2f} KB)\n")
    out.write(f"CLASS: {classify_file(p.name, head)}\n")
    out.write(f"MAGIC(4): {head[:4].hex()}  ASCII={head[:4].decode('latin1', errors='ignore')!r}\n")

    strings = extract_strings(head)
    out.write("\nSTRINGS:\n")
    if strings:
        for s in strings[:50]:
            out.write(f"  {s}\n")
    else:
        out.write("  <none>\n")

    out.write("\nU32 LE (first 32):\n")
    out.write(f"  {parse_u32s(head, 32)}\n")

    out.write("\nHEX PREVIEW (first 256 bytes):\n")
    for i in range(0, min(256, len(head)), 16):
        chunk = head[i:i+16]
        out.write(f"{i:04x}: {chunk.hex(' ')}\n")

    if head[:4] == b"DFCJ":
        out.write("\nHINT: starts with DFCJ, likely a Dazhihui custom file header/container/index.\n")
    if re.search(rb"\b(SH|SZ|HK)\d{6}\b", head):
        out.write("HINT: contains security code pattern like SH600xxx/SZ000xxx/HKxxxxx.\n")
    if size % 32 == 0:
        out.write("HINT: file size divisible by 32 -> maybe fixed-length records with 32-byte entries.\n")
    if size % 64 == 0:
        out.write("HINT: file size divisible by 64 -> maybe 64-byte blocks/records.\n")
    if size % 24 == 0:
        out.write("HINT: file size divisible by 24 -> maybe 24-byte records.\n")
    if size % 16 == 0:
        out.write("HINT: file size divisible by 16 -> maybe 16-byte records.\n")

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as out:
        analyze_file(PATH, out)
    print(f"Saved output to: {OUT}")

if __name__ == "__main__":
    main()