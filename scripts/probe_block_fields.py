import argparse
import struct
from collections import Counter
from pathlib import Path

BLOCK_SIZE = 8192


def load_block(path: Path) -> bytes:
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != BLOCK_SIZE:
        raise SystemExit(f"Expected {BLOCK_SIZE} bytes, got {len(data)} from {path}")
    return data


def as_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def as_i32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


def as_f32(data: bytes, offset: int) -> float:
    return struct.unpack_from("<f", data, offset)[0]


def score_float(v: float) -> bool:
    return v == v and abs(v) < 1e9


def score_int(v: int) -> bool:
    return -2_147_483_648 < v < 2_147_483_647


def classify_u32(v: int):
    tags = []
    if v == 0:
        tags.append("zero")
    if v in (0xFFFFFFFF,):
        tags.append("all_ones")
    if 0 < v < BLOCK_SIZE:
        tags.append("small_offset")
    if v % 8192 == 0 and v != 0:
        tags.append("block_aligned")
    if 20000101 <= v <= 20991231:
        tags.append("yyyymmdd")
    if 0 <= v <= 235959:
        tags.append("hhmmss")
    return tags


def scan(data: bytes, start: int, end: int, step: int):
    rows = []
    for off in range(start, end, step):
        if off + 4 > len(data):
            break
        u32 = as_u32(data, off)
        i32 = as_i32(data, off)
        f32 = as_f32(data, off)
        tags = classify_u32(u32)
        if tags or abs(i32) > 100000 or (score_float(f32) and abs(f32) >= 0.1):
            rows.append((off, u32, i32, f32, tags))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Probe a block for likely fields.")
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--in-file", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks\600519_block.bin")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks")
    args = parser.parse_args()

    block = load_block(Path(args.in_file))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ranges = [(0x0000, 0x0800), (0x1000, 0x1800)]
    txt_path = out_dir / f"{args.code}_field_probe.txt"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"code: {args.code}\n")
        f.write(f"block_size: {len(block)}\n\n")
        for start, end in ranges:
            f.write(f"range {start:#06x} - {end:#06x}\n")
            rows = scan(block, start, end, 4)
            for off, u32, i32, f32, tags in rows[:400]:
                tag_str = ",".join(tags) if tags else ""
                f.write(f"{off:#06x}  u32={u32:<12}  i32={i32:<12}  f32={f32:<14.6g}  {tag_str}\n")
            f.write("\n")

    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
