import argparse
from pathlib import Path

BLOCK_SIZE = 8192


def find_input_file(code: str, in_file: str | None, in_dir: str | None) -> Path:
    if in_file:
        path = Path(in_file)
        if not path.exists():
            raise SystemExit(f"Missing input file: {path}")
        return path

    if not in_dir:
        raise SystemExit("You must provide either --in-file or --in-dir")

    base = Path(in_dir)
    if not base.exists():
        raise SystemExit(f"Missing input directory: {base}")

    patterns = [
        f"{code}*.bin",
        f"{code}*.dat",
        f"{code}*.raw",
        f"*{code}*.bin",
        f"*{code}*.dat",
        f"*{code}*.raw",
    ]

    candidates = []
    for pattern in patterns:
        candidates.extend(p for p in base.rglob(pattern) if p.is_file())

    candidates = sorted(set(candidates))
    if not candidates:
        raise SystemExit(
            f"No matching input files found under {base} for code={code}. "
            f"Try --in-file with an explicit file path."
        )

    return candidates[0]


def load_source_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(
        description="Export a raw 8192-byte stock block to outputs/stocks/{code}_block.bin"
    )
    parser.add_argument("--code", required=True, help="Stock code, e.g. 600519")
    parser.add_argument("--in-file", default=None, help="Explicit upstream input file")
    parser.add_argument("--in-dir", default=None, help="Search directory for upstream input files")
    parser.add_argument("--block-index", type=int, default=0, help="Block index inside the input stream")
    parser.add_argument(
        "--out-dir",
        default=r"D:\\Program\\dzh365(64)\\analysis\\outputs\\stocks",
        help="Output directory for *_block.bin files",
    )
    args = parser.parse_args()

    input_path = find_input_file(args.code, args.in_file, args.in_dir)
    data = load_source_bytes(input_path)

    start = args.block_index * BLOCK_SIZE
    end = start + BLOCK_SIZE
    if len(data) < end:
        raise SystemExit(
            f"Input file too small for block_index={args.block_index}. "
            f"Need at least {end} bytes, got {len(data)} bytes."
        )

    block = data[start:end]
    if len(block) != BLOCK_SIZE:
        raise SystemExit(f"Expected {BLOCK_SIZE} bytes for one block, got {len(block)} bytes.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.code}_block.bin"

    with open(out_path, "wb") as f:
        f.write(block)

    print(f"Saved: {out_path}")
    print(f"Source: {input_path}")
    print(f"Block index: {args.block_index}")
    print(f"Block size: {len(block)} bytes")


if __name__ == "__main__":
    main()
