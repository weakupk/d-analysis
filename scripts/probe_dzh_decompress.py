import struct
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\dzh_decompress_probe.txt")

def analyze_payload_bits(data, max_bytes=64):
    bit_str = []
    for b in data[:max_bytes]:
        bit_str.append(f"{b:08b}")
    return " ".join(bit_str)

def probe_decompress():
    lines = []
    lines.append("DZH DECOMPRESSION BITSTREAM PROBE\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "File missing"

    test_f1 = [4977, 8433] # 0xf1 blocks
    test_f2 = [1850, 1851, 1852, 1853] # 0xf2 blocks

    with open(DAY_DATA_PATH, "rb") as f:
        lines.append("--- TYPE 0xF1 BLOCKS ---")
        for blk in test_f1:
            f.seek(blk * 8192)
            bdata = f.read(8192)
            count, comp_len = struct.unpack("<II", bdata[:8])
            head_bytes = bdata[8:16]
            payload = bdata[16:16+comp_len]
            lines.append(f"Block #{blk}: count={count}, comp_len={comp_len}, head_8_16={head_bytes.hex(' ')}")
            lines.append(f"  First 16b hex: {payload[:16].hex(' ')}")
            lines.append(f"  First 16b bits: {analyze_payload_bits(payload, 16)}")

        lines.append("\n--- TYPE 0xF2 BLOCKS ---")
        for blk in test_f2:
            f.seek(blk * 8192)
            bdata = f.read(8192)
            count, comp_len = struct.unpack("<II", bdata[:8])
            head_bytes = bdata[8:16]
            payload = bdata[16:16+comp_len]
            lines.append(f"Block #{blk}: count={count}, comp_len={comp_len}, head_8_16={head_bytes.hex(' ')}")
            lines.append(f"  First 16b hex: {payload[:16].hex(' ')}")
            lines.append(f"  First 16b bits: {analyze_payload_bits(payload, 16)}")

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = probe_decompress()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
