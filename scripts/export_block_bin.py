import argparse
from pathlib import Path

BLOCK_SIZE = 8192


def load_source_bytes(path: Path) -> bytes:
    """
    Load the upstream raw bytes that contain one or more 8192-byte blocks.

    This implementation assumes the source file already contains a raw block
    stream or a file that starts with the target block. If your upstream source
    has a different format, replace this function with the actual extractor.
    """
    with open(path, "rb") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(
        description="Export a raw 8192-byte stock block to outputs/stocks/{code}_block.bin"
    )
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument(
        "--in-file",
        required=True,
        help="Upstream raw input file that contains the block data",
    )
    parser.add_argument(
        "--block-index",
        type=int,
        default=0,
        help="Block index inside the input stream. Default: 0",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\\Program\\dzh365(64)\\analysis\\outputs\\stocks",
        help="Output directory for *_block.bin files",
    )
    args = parser.parse_args()

    in_path = Path(args.in_file)
    if not in_path.exists():
        raise SystemExit(f"Missing input file: {in_path}")

    data = load_source_bytes(in_path)
    start = args.block_index * BLOCK_SIZE
    end = start + BLOCK_SIZE

    if len(data) < end:
        raise SystemExit(
            f"Input file too small for block_index={args.block_index}. "
            f"Need at least {end} bytes, got {len(data)} bytes."
        )

    block = data[start:end]
    if len(block) != BLOCK_SIZE:
        raise SystemExit(
            f"Expected {BLOCK_SIZE} bytes for one block, got {len(block)} bytes."
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.code}_block.bin"

    with open(out_path, "wb") as f:
        f.write(block)

    print(f"Saved: {out_path}")
    print(f"Block size: {len(block)} bytes")
    print(f"Source: {in_path}")
    print(f"Block index: {args.block_index}")


if __name__ == "__main__":
    main()