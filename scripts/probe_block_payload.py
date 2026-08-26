import struct
import math
from collections import Counter
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\block_payload_probe.txt")

def entropy(data):
    if not data:
        return 0
    counts = Counter(data)
    ent = 0
    for count in counts.values():
        p = count / len(data)
        ent -= p * math.log2(p)
    return ent

def probe_payloads():
    lines = []
    lines.append("DEEP PAYLOAD PROBE FOR DAY_2.DAT.dat\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "File missing"

    blocks = [1850, 1851, 1852, 1853, 4977, 8433]

    with open(DAY_DATA_PATH, "rb") as f:
        for blk in blocks:
            offset = blk * 8192
            f.seek(offset)
            data = f.read(8192)

            count, comp_len, m1, m2 = struct.unpack("<4I", data[:16])
            payload = data[16:16+comp_len]

            ent = entropy(payload)
            lines.append(f"Block #{blk} (0x{offset:08x}):")
            lines.append(f"  Header: count={count}, comp_len={comp_len}, m1=0x{m1:08x}, m2=0x{m2:08x}")
            lines.append(f"  Payload entropy: {ent:.3f} / 8.000 bits/byte")
            lines.append(f"  First 32 bytes hex: {payload[:32].hex(' ')}")
            lines.append(f"  First 32 bytes uint16: {struct.unpack('<16H', payload[:32])}")
            lines.append(f"  First 32 bytes uint32: {struct.unpack('<8I', payload[:32])}")
            lines.append("-" * 50)

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = probe_payloads()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
