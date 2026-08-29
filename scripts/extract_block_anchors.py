import argparse
import json
import struct
from pathlib import Path

BLOCK_SIZE = 8192
ANCHORS = [0x0000, 0x0410, 0x04a0, 0x1000, 0x1410, 0x14a0]
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


def decode_triplet(data: bytes, off: int):
    raw = data[off:off + 4]
    return {
        "offset": off,
        "offset_hex": fmt(off),
        "raw_hex": raw.hex(" "),
        "u32": u32(data, off),
        "i32": i32(data, off),
        "f32": f32(data, off),
    }


def anchor_window(data: bytes, anchor: int, window: int):
    start = max(0, anchor - window)
    end = min(len(data), anchor + window)
    items = []
    for off in range(start, end, 4):
        if off + 4 <= len(data):
            items.append(decode_triplet(data, off))
    return {"anchor": anchor, "anchor_hex": fmt(anchor), "start": start, "end": end, "rows": items}


def main():
    parser = argparse.ArgumentParser(description="Extract candidate structure around known block anchors.")
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--in-file", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks\600519_block.bin")
    parser.add_argument("--out-dir", default=r"D:\Program\dzh365(64)\analysis\outputs\stocks")
    args = parser.parse_args()

    block = load_block(Path(args.in_file))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "code": args.code,
        "block_size": len(block),
        "anchors": [anchor_window(block, anchor, WINDOW) for anchor in ANCHORS],
    }

    json_path = out_dir / f"{args.code}_anchor_extract.json"
    txt_path = out_dir / f"{args.code}_anchor_extract.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"code: {args.code}\n")
        f.write(f"block_size: {len(block)}\n\n")
        for item in result["anchors"]:
            f.write(f"anchor {item['anchor_hex']} (window {WINDOW})\n")
            for row in item["rows"]:
                f.write(
                    f"  {row['offset_hex']}  raw={row['raw_hex']}  "
                    f"u32={row['u32']:<12}  i32={row['i32']:<12}  f32={row['f32']:<14.6g}\n"
                )
            f.write("\n")

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()
