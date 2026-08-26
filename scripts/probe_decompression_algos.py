import struct
import zlib
import bz2
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\decompression_algos_probe.txt")

TEST_BLOCKS = [1850, 1851, 1852, 1853, 4977, 8433]

def test_algos():
    lines = []
    lines.append("TESTING DECOMPRESSION ALGORITHMS ON DAY_2.DAT.dat\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "DAY_2.DAT.dat missing"

    with open(DAY_DATA_PATH, "rb") as f:
        for blk in TEST_BLOCKS:
            offset = blk * 8192
            f.seek(offset)
            data = f.read(8192)

            count, compressed_len = struct.unpack("<II", data[:8])
            lines.append(f"Block #{blk} at 0x{offset:08x}: count={count}, compressed_len={compressed_len}")

            # Try raw deflate (wbits = -15)
            for p_off in range(8, 32):
                payload = data[p_off:]
                try:
                    decomp = zlib.decompress(payload, -zlib.MAX_WBITS)
                    lines.append(f"  [RAW DEFLATE SUCCESS] offset={p_off}, decomp_len={len(decomp)}")
                    lines.append(f"  Hex (first 64b): {decomp[:64].hex(' ')}")
                    break
                except Exception:
                    pass

                try:
                    decomp = zlib.decompress(payload, zlib.MAX_WBITS)
                    lines.append(f"  [ZLIB SUCCESS] offset={p_off}, decomp_len={len(decomp)}")
                    break
                except Exception:
                    pass

                try:
                    decomp = bz2.decompress(payload)
                    lines.append(f"  [BZ2 SUCCESS] offset={p_off}, decomp_len={len(decomp)}")
                    break
                except Exception:
                    pass

            lines.append("")

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = test_algos()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
