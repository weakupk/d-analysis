import struct
from pathlib import Path

SH_DAY_DAT = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
SZ_DAY_DAT = Path(r"D:\Program\dzh365(64)\data\sz\DAY_2.DAT.dat")
SH_MIN_DAT = Path(r"D:\Program\dzh365(64)\data\sh\MIN_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\header_fields_verify.txt")

def parse_header_16(head: bytes):
    if len(head) < 16:
        return None
    rec_count, comp_size = struct.unpack("<II", head[:8])
    comp_type = head[8]
    uncomp_size = head[9] | (head[10] << 8) | (head[11] << 16)
    checksum = struct.unpack("<I", head[12:16])[0]
    return {
        "rec_count": rec_count,
        "comp_size": comp_size,
        "comp_type": hex(comp_type),
        "uncomp_size": uncomp_size,
        "checksum": hex(checksum),
    }

def verify_file(path: Path):
    lines = []
    lines.append(f"=== VERIFYING HEADERS IN {path.name} ===")
    if not path.exists():
        lines.append("File not found.")
        return "\n".join(lines)

    size = path.stat().st_size
    num_blocks = size // 8192
    lines.append(f"Size: {size} bytes | Blocks: {num_blocks}")

    valid_headers = 0
    invalid_headers = 0
    type_counts = {}

    with open(path, "rb") as f:
        for blk in range(num_blocks):
            f.seek(blk * 8192)
            head = f.read(16)
            parsed = parse_header_16(head)
            if not parsed:
                invalid_headers += 1
                continue

            # Validation heuristics
            ctype = parsed["comp_type"]
            type_counts[ctype] = type_counts.get(ctype, 0) + 1

            if parsed["rec_count"] < 10000 and parsed["comp_size"] <= 8176:
                valid_headers += 1
            else:
                invalid_headers += 1

    lines.append(f"Valid Headers: {valid_headers} / {num_blocks} ({valid_headers/num_blocks*100:.1f}%)")
    lines.append(f"Compression Type Distribution: {type_counts}")

    # Print first 10 sample headers
    lines.append("\nSample First 10 Block Headers:")
    lines.append(f"{'Blk':<5} | {'RecCount':<8} | {'CompSize':<8} | {'Type':<6} | {'UncompSize':<10} | {'Checksum':<10}")
    lines.append("-" * 65)

    with open(path, "rb") as f:
        for blk in range(min(10, num_blocks)):
            f.seek(blk * 8192)
            head = f.read(16)
            p = parse_header_16(head)
            lines.append(f"{blk:<5} | {p['rec_count']:<8} | {p['comp_size']:<8} | {p['comp_type']:<6} | {p['uncomp_size']:<10} | {p['checksum']:<10}")

    lines.append("\n")
    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = []
    report.append("BLOCK HEADER STRUCTURE VERIFICATION\n" + "="*60 + "\n")
    report.append(verify_file(SH_DAY_DAT))
    report.append(verify_file(SZ_DAY_DAT))
    report.append(verify_file(SH_MIN_DAT))

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
