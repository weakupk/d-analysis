import struct
from pathlib import Path

DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\lzo_pure_probe.txt")

def lzo1x_decompress_pure_python(data: bytes, expected_len: int) -> bytes:
    """
    Pure Python LZO1X-1 Decompressor Implementation.
    """
    out = bytearray()
    ip = 0
    in_len = len(data)

    if in_len == 0:
        return bytes()

    # First byte processing
    b = data[ip]
    ip += 1

    if b > 17:
        t = b - 17
        out.extend(data[ip:ip+t])
        ip += t
        if ip >= in_len:
            return bytes(out)
        b = data[ip]
        ip += 1

    while ip < in_len:
        t = b
        m_len = 0
        m_off = 0
        if t < 16:
            if t == 0:
                while ip < in_len and data[ip] == 0:
                    t += 255
                    ip += 1
                if ip < in_len:
                    t += 15 + data[ip]
                    ip += 1
            t += 3
            if ip + t > in_len:
                break
            out.extend(data[ip:ip+t])
            ip += t
            if ip >= in_len:
                break
            b = data[ip]
            ip += 1
            if b < 16:
                # m_off
                m_off = 1 + 0x0800 + (b >> 2) + (data[ip] << 4)
                ip += 1
                m_len = 3
                # copy
                for _ in range(m_len):
                    if len(out) >= m_off:
                        out.append(out[-m_off])
                b = data[ip-1] & 3
                if b == 0:
                    b = data[ip]
                    ip += 1
                continue

        if t >= 64:
            m_len = (t >> 5) + 1
            m_off = 1 + ((t >> 2) & 7) + (data[ip] << 3)
            ip += 1
        elif t >= 32:
            m_len = t & 31
            if m_len == 0:
                while ip < in_len and data[ip] == 0:
                    m_len += 255
                    ip += 1
                if ip < in_len:
                    m_len += 31 + data[ip]
                    ip += 1
            m_len += 2
            m_off = 1 + (struct.unpack_from("<H", data, ip)[0] >> 2)
            ip += 2
        elif t >= 16:
            m_off = (t & 8) << 11
            m_len = t & 7
            if m_len == 0:
                while ip < in_len and data[ip] == 0:
                    m_len += 255
                    ip += 1
                if ip < in_len:
                    m_len += 7 + data[ip]
                    ip += 1
            m_len += 2
            m_off += (struct.unpack_from("<H", data, ip)[0] >> 2) + 1
            ip += 2
            if m_off == 1:
                # EOF
                break

        # Copy match
        for _ in range(m_len):
            if len(out) >= m_off:
                out.append(out[-m_off])

        b = data[ip-1] & 3
        if b == 0:
            if ip < in_len:
                b = data[ip]
                ip += 1
            else:
                break

    return bytes(out)

def test_lzo():
    lines = []
    lines.append("TESTING PURE PYTHON LZO1X-1 DECOMPRESSION\n" + "="*60 + "\n")

    if not DAY_DATA_PATH.exists():
        return "File missing"

    test_blocks = [1, 2, 3, 4, 1850, 1851, 4977, 8433]

    with open(DAY_DATA_PATH, "rb") as f:
        for blk in test_blocks:
            offset = blk * 8192
            f.seek(offset)
            bdata = f.read(8192)

            rec_count, comp_size = struct.unpack("<II", bdata[:8])
            comp_type = bdata[8]
            uncomp_size = bdata[9] | (bdata[10] << 8) | (bdata[11] << 16)
            payload = bdata[16:16+comp_size]

            lines.append(f"Block #{blk} (Type 0x{comp_type:02x}): rec_count={rec_count}, comp_size={comp_size}, uncomp_size={uncomp_size}")

            decomp = lzo1x_decompress_pure_python(payload, uncomp_size)
            lines.append(f"  Decompressed length: {len(decomp)} (Expected: {uncomp_size})")
            if len(decomp) > 0:
                lines.append(f"  Decompressed hex (first 64b): {decomp[:64].hex(' ')}")
                # Check for rec_count * 32 or similar record structure
                rec_len = len(decomp) / rec_count if rec_count > 0 else 0
                lines.append(f"  Bytes per record if uncompressed: {rec_len:.2f}")

                # Test parsing decompressed records
                if rec_len >= 16:
                    lines.append("  First 2 decompressed record uint32s:")
                    lines.append(f"    Rec 1: {struct.unpack_from('<8I', decomp, 0)}")
                    if len(decomp) >= 64:
                        lines.append(f"    Rec 2: {struct.unpack_from('<8I', decomp, 32)}")
            lines.append("-" * 50)

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = test_lzo()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
