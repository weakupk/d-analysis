import argparse
import json
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


def fmt(off: int) -> str:
    return f"0x{off:04x}"


def u32_at(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def describe_u32(value: int):
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


def parse_codes(values):
    codes = []
    for value in values:
        if value is None:
            continue
        for part in str(value).split(","):
            part = part.strip()
            if part:
                codes.append(part)
    return codes


def main():
    parser = argparse.ArgumentParser(description="Find variable offsets across multiple stock blocks.")
    parser.add_argument("--code", action="append", required=True, help="Repeatable stock code, e.g. --code 600519 --code 000001")
    parser.add_argument(
        "--in-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
        help="Directory containing *_block.bin files.",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
        help="Directory for output files.",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=4,
        help="Byte step for scanning offsets. Default: 4",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for number of variable offsets to report. 0 means no limit.",
    )
    args = parser.parse_args()

    codes = parse_codes(args.code)
    if len(codes) < 2:
        raise SystemExit("Need at least 2 codes to compare.")

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    blocks = {}
    for code in codes:
        path = in_dir / f"{code}_block.bin"
        if not path.exists():
            raise SystemExit(f"Missing input file: {path}")
        blocks[code] = load_block(path)

    block_lengths = {len(data) for data in blocks.values()}
    if len(block_lengths) != 1:
        raise SystemExit(f"Block sizes differ: {sorted(block_lengths)}")
    block_size = next(iter(block_lengths))

    variable_offsets = []
    stable_offsets = []

    for off in range(0, block_size - 3, args.step):
        values = {code: u32_at(blocks[code], off) for code in codes}
        unique_values = set(values.values())
        if len(unique_values) > 1:
            counts = Counter(values.values())
            variable_offsets.append(
                {
                    "offset": off,
                    "offset_hex": fmt(off),
                    "values": values,
                    "unique_count": len(unique_values),
                    "most_common_count": counts.most_common(1)[0][1],
                    "raw_hex": {code: blocks[code][off:off + 4].hex(" ") for code in codes},
                    "tags": {code: describe_u32(val) for code, val in values.items()},
                }
            )
        else:
            stable_offsets.append(
                {
                    "offset": off,
                    "offset_hex": fmt(off),
                    "value": next(iter(unique_values)),
                }
            )

    variable_offsets.sort(key=lambda x: (-x["unique_count"], x["offset"]))
    if args.limit and args.limit > 0:
        variable_offsets = variable_offsets[: args.limit]

    summary = {
        "codes": codes,
        "block_size": block_size,
        "step": args.step,
        "variable_offset_count": len(variable_offsets),
        "stable_offset_count": len(stable_offsets),
        "top_variable_offsets": variable_offsets[:100],
    }

    json_path = out_dir / "variable_offsets_summary.json"
    txt_path = out_dir / "variable_offsets_summary.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Variable offsets summary\n")
        f.write(f"codes: {', '.join(codes)}\n")
        f.write(f"block_size: {block_size}\n")
        f.write(f"step: {args.step}\n")
        f.write(f"variable_offset_count: {len(variable_offsets)}\n")
        f.write(f"stable_offset_count: {len(stable_offsets)}\n\n")
        for item in variable_offsets[:200]:
            f.write(f"{item['offset_hex']} unique={item['unique_count']} common={item['most_common_count']}\n")
            for code in codes:
                tags = ",".join(item["tags"][code])
                f.write(
                    f"  {code}: raw={item['raw_hex'][code]} u32={item['values'][code]} {tags}\n"
                )
            f.write("\n")

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
