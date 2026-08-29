import argparse
import json
import struct
from pathlib import Path

BLOCK_SIZE = 8192
FIELDS = [
    (0x0000, "page_ts_1"),
    (0x0004, "page_ts_2"),
    (0x0008, "page_zero"),
    (0x000c, "page_count_a"),
    (0x0010, "page_flag_all_ones"),
    (0x0014, "page_count_b"),
    (0x0018, "page_id"),
    (0x0410, "subpage_header_1"),
    (0x0414, "subpage_zero"),
    (0x0418, "subpage_id"),
    (0x041c, "subpage_type"),
    (0x0420, "subpage_flag"),
    (0x0424, "subpage_magic"),
    (0x04a4, "subtable_count"),
    (0x04a8, "subtable_ts"),
    (0x04ac, "subtable_v1"),
    (0x04b0, "subtable_v2"),
    (0x04b4, "subtable_v3"),
    (0x04b8, "subtable_v4"),
    (0x04bc, "subtable_len"),
    (0x04c0, "subtable_value_1"),
    (0x04c4, "subtable_value_2"),
    (0x1000, "page2_ts_1"),
    (0x1004, "page2_ts_2"),
    (0x1008, "page2_zero"),
    (0x100c, "page2_count_a"),
    (0x1010, "page2_flag_all_ones"),
    (0x1014, "page2_count_b"),
    (0x1018, "page2_id"),
    (0x1410, "subpage2_header_1"),
    (0x1414, "subpage2_zero"),
    (0x1418, "subpage2_id"),
    (0x141c, "subpage2_type"),
    (0x1420, "subpage2_flag"),
    (0x1424, "subpage2_magic"),
    (0x14a4, "subtable2_count"),
    (0x14a8, "subtable2_ts"),
    (0x14ac, "subtable2_v1"),
    (0x14b0, "subtable2_v2"),
    (0x14b4, "subtable2_v3"),
    (0x14b8, "subtable2_v4"),
    (0x14bc, "subtable2_len"),
    (0x14c0, "subtable2_value_1"),
    (0x14c4, "subtable2_value_2"),
]


def load_block(path: Path) -> bytes:
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != BLOCK_SIZE:
        raise SystemExit(f"Expected {BLOCK_SIZE} bytes, got {len(data)} from {path}")
    return data


def unpack_u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def unpack_i32(data: bytes, off: int) -> int:
    return struct.unpack_from("<i", data, off)[0]


def unpack_f32(data: bytes, off: int) -> float:
    return struct.unpack_from("<f", data, off)[0]


def describe(value: int):
    tags = []
    if value == 0:
        tags.append("zero")
    if value == 0xFFFFFFFF:
        tags.append("all_ones")
    if 0 < value < 10000:
        tags.append("small")
    if 20000101 <= value <= 20991231:
        tags.append("yyyymmdd")
    if 0 <= value <= 235959:
        tags.append("hhmmss")
    if value % 8192 == 0 and value != 0:
        tags.append("block_aligned")
    return tags


def fmt(off: int) -> str:
    return f"0x{off:04x}"


def main():
    parser = argparse.ArgumentParser(description="Extract semantically named fields from a stock block.")
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--in-file", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks\600519_block.bin")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks")
    args = parser.parse_args()

    block = load_block(Path(args.in_file))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for off, name in FIELDS:
        if off + 4 > len(block):
            continue
        u32 = unpack_u32(block, off)
        i32 = unpack_i32(block, off)
        f32 = unpack_f32(block, off)
        records.append({
            "field": name,
            "offset": off,
            "offset_hex": fmt(off),
            "raw_hex": block[off:off + 4].hex(" "),
            "u32": u32,
            "i32": i32,
            "f32": f32,
            "tags": describe(u32),
        })

    output = {
        "code": args.code,
        "block_size": len(block),
        "fields": records,
    }

    json_path = out_dir / f"{args.code}_semantic_fields.json"
    txt_path = out_dir / f"{args.code}_semantic_fields.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"code: {args.code}\n")
        f.write(f"block_size: {len(block)}\n\n")
        for row in records:
            tag_str = ",".join(row["tags"]) if row["tags"] else ""
            f.write(
                f"{row['offset_hex']}  {row['field']:<24}  raw={row['raw_hex']}  "
                f"u32={row['u32']:<12}  i32={row['i32']:<12}  f32={row['f32']:<14.6g}  {tag_str}\n"
            )

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
