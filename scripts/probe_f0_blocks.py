import struct
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\f0_blocks_probe.txt")

F0_BLOCKS = [0, 48, 6095, 6106, 6138, 6168, 6552, 6573, 6584, 13541]

def inspect_f0():
    lines = []
    lines.append("INSPECTING 0xF0 BLOCKS IN DAY_2.DAT.dat\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "File missing"

    with open(DAY_DATA_PATH, "rb") as f:
        for blk in F0_BLOCKS:
            offset = blk * 8192
            f.seek(offset)
            block_data = f.read(8192)

            count, comp_len = struct.unpack("<II", block_data[:8])
            m_byte = block_data[8]
            lines.append(f"Block #{blk} at 0x{offset:08x}: count={count}, comp_len={comp_len}, m_byte=0x{m_byte:02x}")
            lines.append(f"  Header hex (32b): {block_data[:32].hex(' ')}")

            payload = block_data[16:16+comp_len]
            lines.append(f"  Payload hex (first 128b): {payload[:128].hex(' ')}")

            # Check if there are dates like 2020xxxx, 2021xxxx, 2022xxxx, 2023xxxx, 2024xxxx, 2025xxxx, 2026xxxx in payload!
            # Search uint32 in payload
            lines.append("  Interpretation as uint32s (first 32):")
            u32s = struct.unpack("<32I", payload[:128])
            lines.append(f"    {u32s}")

            lines.append("  Interpretation as float32s (first 32):")
            f32s = struct.unpack("<32f", payload[:128])
            lines.append(f"    {[round(x, 2) for x in f32s]}")

            lines.append("-" * 50)

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = inspect_f0()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
