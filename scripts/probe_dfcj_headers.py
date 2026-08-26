import os
import struct
from pathlib import Path

DATA_DIRS = [
    Path(r"D:\Program\dzh365(64)\data\sh"),
    Path(r"D:\Program\dzh365(64)\data\sz"),
]

OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\dfcj_headers_probe.txt")

def read_bytes(path: Path, length: int = 512) -> bytes:
    if not path.exists():
        return b""
    with open(path, "rb") as f:
        return f.read(length)

def inspect_dfcj(path: Path):
    data = read_bytes(path, 256)
    if not data:
        return f"FILE NOT FOUND: {path}"
    
    size = path.stat().st_size
    magic = data[:4]
    
    lines = []
    lines.append(f"=== {path.name} ({path.parent.name.upper()}) ===")
    lines.append(f"Path: {path}")
    lines.append(f"Size: {size} bytes ({size / (1024*1024):.2f} MB)")
    lines.append(f"Magic: {magic.hex()} ({magic})")
    
    if len(data) >= 64:
        # Interpret first 16 uint32s
        u32s = struct.unpack("<16I", data[:64])
        lines.append("First 16 uint32_le:")
        for idx in range(0, 16, 4):
            chunk = u32s[idx:idx+4]
            lines.append(f"  [{idx:02d}-{idx+3:02d}]: {chunk}")
            
    lines.append("Hex Header (first 128 bytes):")
    for i in range(0, min(128, len(data)), 16):
        chunk = data[i:i+16]
        hex_str = chunk.hex(" ")
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"  {i:04x}: {hex_str:<47}  |{ascii_str}|")
    
    # Check corresponding .dat file if available
    dat_dat_path = Path(str(path) + ".dat")
    if dat_dat_path.exists():
        dat_size = dat_dat_path.stat().st_size
        lines.append(f"Paired Data File: {dat_dat_path.name} | Size: {dat_size} bytes ({dat_size / (1024*1024):.2f} MB)")
        dat_head = read_bytes(dat_dat_path, 64)
        lines.append(f"  Paired Data Magic/Head (16b hex): {dat_head[:16].hex(' ')}")
    
    lines.append("\n")
    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = []
    report.append("DFCJ HEADERS AND FILE PAIRS PROBE REPORT\n" + "=" * 60 + "\n")
    
    for d in DATA_DIRS:
        if not d.exists():
            continue
        for dat_file in sorted(d.glob("*.DAT")):
            report.append(inspect_dfcj(dat_file))
            
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"Probe saved to: {OUT_FILE}")

if __name__ == "__main__":
    main()
