import struct
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\kline_struct_probe.txt")

F0_BLOCKS = [6095, 6106, 6138, 6168, 6552, 6573, 6584, 13541]

def analyze_kline_struct():
    lines = []
    lines.append("ANALYZING UNCOMPRESSED K-LINE BLOCK STRUCTURE (0xF0 BLOCKS)\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "File missing"

    with open(DAY_DATA_PATH, "rb") as f:
        for blk in F0_BLOCKS:
            offset = blk * 8192
            f.seek(offset)
            block_data = f.read(8192)

            rec_count, comp_len = struct.unpack("<II", block_data[:8])
            m_byte = block_data[8]
            payload = block_data[16:16+comp_len]

            lines.append(f"Block #{blk} at 0x{offset:08x}: count={rec_count}, comp_len={comp_len}")

            # Try candidate record sizes: 24, 32, 40, 48, 64
            for rsize in [24, 32, 36, 40, 44, 48]:
                lines.append(f"\n--- Testing Candidate Record Size: {rsize} bytes ---")
                records = []
                for idx in range(min(5, rec_count)):
                    rec_bytes = payload[idx*rsize : (idx+1)*rsize]
                    if len(rec_bytes) < rsize:
                        break
                    
                    # Try unpacking uint32s and floats
                    u32s = struct.unpack(f"<{rsize//4}I", rec_bytes)
                    f32s = [round(x, 2) for x in struct.unpack(f"<{rsize//4}f", rec_bytes)]
                    lines.append(f"  Rec #{idx+1} ({idx*rsize:04x}):")
                    lines.append(f"    Hex: {rec_bytes.hex(' ')}")
                    lines.append(f"    u32: {u32s}")
                    lines.append(f"    f32: {f32s}")

            lines.append("="*60 + "\n")

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = analyze_kline_struct()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
