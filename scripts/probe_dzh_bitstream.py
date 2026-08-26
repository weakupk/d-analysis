import struct
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\bitstream_probe.txt")

class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.bit_pos = 0

    def read_bits(self, n: int) -> int:
        val = 0
        for _ in range(n):
            byte_idx = self.bit_pos // 8
            bit_idx = self.bit_pos % 8
            if byte_idx >= len(self.data):
                break
            bit = (self.data[byte_idx] >> (7 - bit_idx)) & 1
            val = (val << 1) | bit
            self.bit_pos += 1
        return val

    def read_bits_le(self, n: int) -> int:
        val = 0
        for i in range(n):
            byte_idx = self.bit_pos // 8
            bit_idx = self.bit_pos % 8
            if byte_idx >= len(self.data):
                break
            bit = (self.data[byte_idx] >> bit_idx) & 1
            val |= (bit << i)
            self.bit_pos += 1
        return val

def probe_block_bitstream(blk_no: int):
    lines = []
    lines.append(f"--- PROBING BLOCK #{blk_no} BITSTREAM ---")
    with open(DAY_DATA_PATH, "rb") as f:
        f.seek(blk_no * 8192)
        data = f.read(8192)

    rec_count, comp_len = struct.unpack("<II", data[:8])
    m_byte = data[8]
    payload = data[16:16+comp_len]

    lines.append(f"Header: count={rec_count}, comp_len={comp_len}, type=0x{m_byte:02x}")
    lines.append(f"Payload hex (first 32b): {payload[:32].hex(' ')}")

    br_be = BitReader(payload)
    br_le = BitReader(payload)

    lines.append("\nFirst 16 bitfields (MSB First):")
    be_vals = [br_be.read_bits(8) for _ in range(16)]
    lines.append(f"  8-bit ints: {be_vals}")

    lines.append("First 16 bitfields (LSB First):")
    le_vals = [br_le.read_bits_le(8) for _ in range(16)]
    lines.append(f"  8-bit ints: {le_vals}")

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = []
    report.append("DZH BITSTREAM ALLOCATION PROBE\n" + "="*60 + "\n")

    for blk in [1, 2, 3, 1850, 1851, 4977, 8433]:
        report.append(probe_block_bitstream(blk))
        report.append("\n" + "-"*50 + "\n")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
