import struct
from pathlib import Path

DAY_INDEX_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT")
DAY_DATA_PATH = Path(r"D:\Program\dzh365(64)\data\sh\DAY_2.DAT.dat")
OUT_FILE = Path(r"D:\Program\dzh365(64)\analysis\outputs\day_blocks_probe.txt")

def probe_blocks():
    lines = []
    lines.append("PROBING DAY_2.DAT INDEX AND DAY_2.DAT.dat DATA BLOCKS\n" + "="*60 + "\n")

    if not DAY_INDEX_PATH.exists() or not DAY_DATA_PATH.exists():
        lines.append("Files missing.")
        return "\n".join(lines)

    index_size = DAY_INDEX_PATH.stat().st_size
    data_size = DAY_DATA_PATH.stat().st_size
    lines.append(f"Index Size: {index_size} bytes")
    lines.append(f"Data Size: {data_size} bytes ({data_size / (1024*1024):.2f} MB)")

    # Read index file entries starting at 0x6000
    with open(DAY_INDEX_PATH, "rb") as f:
        f.seek(0x6000)
        index_data = f.read()

    entries = []
    for offset in range(0, len(index_data), 16):
        chunk = index_data[offset:offset+16]
        if len(chunk) < 16:
            break
        code_bytes = chunk[:6]
        if code_bytes.isdigit():
            code = code_bytes.decode("ascii")
            padding = chunk[6:12]
            block_no = struct.unpack("<I", chunk[12:16])[0]
            entries.append((0x6000 + offset, code, padding.hex(), block_no))

    lines.append(f"\nTotal valid code entries parsed from index (from 0x6000): {len(entries)}")

    # Show first 30 entries
    lines.append("\nFirst 30 index entries:")
    lines.append(f"{'File Offset':<12} | {'Code':<8} | {'Padding (6b)':<14} | {'Block No':<10}")
    lines.append("-" * 55)
    for file_off, code, pad, blk in entries[:30]:
        lines.append(f"0x{file_off:08x}   | {code:<8} | {pad:<14} | {blk:<10}")

    # Find max block_no
    max_blk = max(e[3] for e in entries) if entries else 0
    lines.append(f"\nMax Block No in parsed index: {max_blk}")

    # Estimate block size B
    # data_size / (max_blk + 1)
    if max_blk > 0:
        est_blk_size = data_size / (max_blk + 1)
        lines.append(f"Data Size / (Max Block No + 1) = {data_size} / {max_blk + 1} = {est_blk_size:.2f} bytes")

    # Common candidate block sizes in financial software: 8192, 16384, 32768, 65536, 1024, 2048, 4096...
    # Or 8192 bytes = 8 KB per block
    # Let's check 8192: 132685824 / 8192 = 16197 blocks!
    # Let's check if max_blk is around 16196 or similar.
    lines.append(f"\nCheck data_size / 8192 = {data_size / 8192:.2f}")
    lines.append(f"Check data_size / 16384 = {data_size / 16384:.2f}")
    lines.append(f"Check data_size / 4096 = {data_size / 4096:.2f}")

    # Let's inspect block headers in DAY_2.DAT.dat for candidate block size 8192
    lines.append("\nInspecting DAY_2.DAT.dat at Block No * 8192 for first 5 entries:")
    with open(DAY_DATA_PATH, "rb") as f_dat:
        for file_off, code, pad, blk in entries[:10]:
            dat_offset = blk * 8192
            if dat_offset + 128 <= data_size:
                f_dat.seek(dat_offset)
                block_head = f_dat.read(128)
                lines.append(f"\nStock {code} (Block #{blk} at Offset 0x{dat_offset:08x} / {dat_offset}):")
                lines.append(f"  Hex (first 64 bytes): {block_head[:64].hex(' ')}")
                # Check for float or uint32 interpretations in K-line data
                # E.g., Date YYYYMMDD as uint32 or int32?
                u32s = struct.unpack("<16I", block_head[:64])
                f32s = struct.unpack("<16f", block_head[:64])
                lines.append(f"  As uint32: {u32s[:8]}")
                lines.append(f"  As float32: {[round(x, 2) for x in f32s[:8]]}")

    return "\n".join(lines)

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = probe_blocks()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {OUT_FILE}")

if __name__ == "__main__":
    main()
