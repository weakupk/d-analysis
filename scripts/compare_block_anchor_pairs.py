import argparse
import json
import struct
from pathlib import Path

BLOCK_SIZE = 8192
PAIRS = [
    (0x0000, 0x1000),
    (0x0410, 0x1410),
    (0x04a4, 0x14a4),
]
WINDOW = 64


def load_block(path: Path) -> bytes:
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != BLOCK_SIZE:
        raise SystemExit(f"Expected {BLOCK_SIZE} bytes, got {len(data)} from {path}")
    return data


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def i32(data: bytes, off: int) -> int:
    return struct.unpack_from("<i", data, off)[0]


def f32(data: bytes, off: int) -> float:
    return struct.unpack_from("<f", data, off)[0]


def fmt(off: int) -> str:
    return f"0x{off:04x}"


def decode_window(data: bytes, anchor: int, window: int):
    start = max(0, anchor - window)
    end = min(len(data), anchor + window)
    rows = []
    for off in range(start, end, 4):
        if off + 4 > len(data):
            break
        raw = data[off:off + 4]
        rows.append({
            "offset": off,
            "offset_hex": fmt(off),
            "raw_hex": raw.hex(" "),
            "u32": u32(data, off),
            "i32": i32(data, off),
            "f32": f32(data, off),
        })
    return {"anchor": anchor, "anchor_hex": fmt(anchor), "start": start, "end": end, "rows": rows}


def compare_rows(left, right):
    matches = []
    for l, r in zip(left["rows"], right["rows"]):
        matches.append({
            "left_offset_hex": l["offset_hex"],
            "right_offset_hex": r["offset_hex"],
            "left_raw": l["raw_hex"],
            "right_raw": r["raw_hex"],
            "same_raw": l["raw_hex"] == r["raw_hex"],
            "left_u32": l["u32"],
            "right_u32": r["u32"],
            "same_u32": l["u32"] == r["u32"],
            "left_i32": l["i32"],
            "right_i32": r["i32"],
            "same_i32": l["i32"] == r["i32"],
            "left_f32": l["f32"],
            "right_f32": r["f32"],
        })
    return matches


def main():
    parser = argparse.ArgumentParser(description="Compare paired anchor regions inside a block.")
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--in-file", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks\600519_block.bin")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks")
    args = parser.parse_args()

    block = load_block(Path(args.in_file))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "code": args.code,
        "block_size": len(block),
        "window": WINDOW,
        "pairs": [],
    }

    for left_anchor, right_anchor in PAIRS:
        left = decode_window(block, left_anchor, WINDOW)
        right = decode_window(block, right_anchor, WINDOW)
        report["pairs"].append({
            "left_anchor": left_anchor,
            "right_anchor": right_anchor,
            "left_anchor_hex": fmt(left_anchor),
            "right_anchor_hex": fmt(right_anchor),
            "left": left,
            "right": right,
            "comparison": compare_rows(left, right),
        })

    json_path = out_dir / f"{args.code}_anchor_compare.json"
    txt_path = out_dir / f"{args.code}_anchor_compare.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"code: {args.code}\n")
        f.write(f"block_size: {len(block)}\n")
        f.write(f"window: {WINDOW}\n\n")
        for pair in report["pairs"]:
            f.write(f"pair {pair['left_anchor_hex']} <-> {pair['right_anchor_hex']}\n")
            for row in pair["comparison"]:
                tag = "MATCH" if row["same_raw"] else "DIFF"
                f.write(
                    f"  {row['left_offset_hex']} <-> {row['right_offset_hex']}  {tag}  "
                    f"left={row['left_raw']}  right={row['right_raw']}  "
                    f"u32={row['left_u32']}|{row['right_u32']}\n"
                )
            f.write("\n")

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
