import struct
from collections import Counter
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\uncompressed_blocks_probe.txt")

def search_blocks():
    lines = []
    lines.append("SCANNING ALL BLOCKS IN DAY_2.DAT.dat FOR COMPRESSION TYPES\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "File missing"

    size = DAY_DATA_PATH.stat().st_size
    num_blocks = size // 8192

    lines.append(f"Total Blocks in File: {num_blocks}")

    magic_byte_counts = Counter()
    uncompressed_blocks = []

    with open(DAY_DATA_PATH, "rb") as f:
        for blk in range(num_blocks):
            f.seek(blk * 8192)
            head = f.read(16)
            if len(head) < 16:
                break
            count, comp_len = struct.unpack("<II", head[:8])
            m_byte = head[8]
            magic_byte_counts[f"0x{m_byte:02x}"] += 1

            # If m_byte is 0xf0 or count > 0 and comp_len == count * 32 (uncompressed record size 32 bytes)
            if m_byte not in (0xf1, 0xf2) and count > 0:
                uncompressed_blocks.append((blk, count, comp_len, m_byte, head.hex()))

    lines.append("\nMagic Byte Distribution at Byte 8 of Block Header:")
    for k, v in magic_byte_counts.most_common():
        lines.append(f"  {k}: {v} blocks ({v/num_blocks*100:.1f}%)")

    lines.append(f"\nNon-standard / Uncompressed Blocks Found: {len(uncompressed_blocks)}")
    for blk, cnt, clen, mb, hhex in uncompressed_blocks[:30]:
        lines.append(f"  Block #{blk}: count={cnt}, comp_len={clen}, m_byte=0x{mb:02x}, head_hex={hhex}")

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = search_blocks()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
