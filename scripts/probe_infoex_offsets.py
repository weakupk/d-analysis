import re
from collections import Counter

PATH = r"D:\Program\dzh365(64)\data\SH\INFOEX.DAT"
OUT = r"D:\Program\dzh365(64)\analysis\outputs\INFOEX_offset_probe.txt"

TARGET_CODES = [
    b"000001", b"000002", b"000003", b"000004", b"000005",
    b"000006", b"000007", b"000008", b"000009", b"000010",
    b"600000", b"600001", b"600002", b"600003", b"600004",
]

def read_file(path):
    with open(path, "rb") as f:
        return f.read()

def find_all(data, needle):
    out = []
    start = 0
    while True:
        idx = data.find(needle, start)
        if idx == -1:
            break
        out.append(idx)
        start = idx + 1
    return out

def main():
    data = read_file(PATH)

    with open(OUT, "w", encoding="utf-8") as out:
        out.write(f"PATH: {PATH}\n")
        out.write(f"SIZE: {len(data)}\n\n")

        out.write("TARGET CODE OFFSETS (all occurrences):\n")
        for code in TARGET_CODES:
            positions = find_all(data, code)
            out.write(f"{code.decode()}: count={len(positions)} first={positions[:20]}\n")
        out.write("\n")

        candidate_lengths = [16, 24, 32, 40, 48, 56, 64, 72, 80, 96, 112, 128, 144, 160, 192, 224, 256]
        for rec_len in candidate_lengths:
            out.write(f"--- RECORD LENGTH {rec_len} ---\n")
            stats = Counter()
            examples = []
            for code in TARGET_CODES:
                positions = find_all(data, code)
                for pos in positions:
                    mod = pos % rec_len
                    stats[mod] += 1
                    if len(examples) < 30:
                        examples.append((code.decode(), pos, mod))
            if stats:
                most_common = stats.most_common(10)
                out.write(f"most_common_mods={most_common}\n")
                out.write("examples (code, pos, pos%len):\n")
                for e in examples[:20]:
                    out.write(f"  {e}\n")
            else:
                out.write("no matches\n")
            out.write("\n")

        head = data[:1024 * 1024]
        codes = sorted(set(re.findall(rb"\b\d{5,6}\b", head)))
        out.write("CODES IN FIRST 1MB:\n")
        for c in codes[:500]:
            out.write(c.decode(errors="ignore") + "\n")

    print(f"Saved output to: {OUT}")

if __name__ == "__main__":
    main()