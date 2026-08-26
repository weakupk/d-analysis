import struct
import zlib
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\kline_compression_probe.txt")

# Test block offsets from previous probe
TEST_BLOCKS = [
    ("603995", 1850),
    ("603996", 1851),
    ("603997", 1852),
    ("603998", 1853),
    ("240354", 4977),
    ("516200", 8433),
]

def probe_decompression():
    lines = []
    lines.append("PROBING K-LINE BLOCK COMPRESSION / PAYLOAD\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        lines.append("DAY_2.DAT.dat missing.")
        return "\n".join(lines)

    with open(DAY_DATA_PATH, "rb") as f:
        for code, blk_no in TEST_BLOCKS:
            offset = blk_no * 8192
            f.seek(offset)
            block_data = f.read(8192)

            count, val2, magic1, magic2 = struct.unpack("<4I", block_data[:16])
            lines.append(f"Stock {code} | Block #{blk_no} | Offset 0x{offset:08x}:")
            lines.append(f"  Header: count={count}, val2={val2}, magic1=0x{magic1:08x}, magic2=0x{magic2:08x}")
            lines.append(f"  Header hex: {block_data[:32].hex(' ')}")

            payload = block_data[12:] # payload starting at offset 12 or 16
            payload16 = block_data[16:]

            # Try zlib at various offsets
            zlib_success = False
            for p_off in [8, 12, 16, 20, 24]:
                try:
                    decomp = zlib.decompress(block_data[p_off:])
                    lines.append(f"  [SUCCESS] Zlib decompressed from offset {p_off}! Decompressed size: {len(decomp)} bytes")
                    lines.append(f"  Decompressed hex (first 64b): {decomp[:64].hex(' ')}")
                    zlib_success = True
                    break
                except Exception:
                    pass

            if not zlib_success:
                lines.append("  [INFO] Standard zlib did not match at offsets 8..24.")

            # Check raw byte patterns in payload
            lines.append(f"  Payload[16:80] hex: {payload16[:64].hex(' ')}")
            lines.append("-" * 50)

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = probe_decompression()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
