import re
from collections import Counter, defaultdict

PATH = r"D:\Program\dzh365(64)\data\SH\INFOEX.DAT"
OUT = r"D:\Program\dzh365(64)\analysis\outputs\INFOEX_context.txt"

CODE_RE = re.compile(rb"\b\d{6}\b")

def read_file(path):
    with open(path, "rb") as f:
        return f.read()

def hexdump(data, width=16):
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        lines.append(f"{i:04x}: {chunk.hex(' ')}")
    return "\n".join(lines)

def context(data, pos, before=64, after=64):
    start = max(0, pos - before)
    end = min(len(data), pos + 6 + after)
    return data[start:end], start

def main():
    data = read_file(PATH)
    size = len(data)

    matches = []
    for m in CODE_RE.finditer(data):
        code = m.group(0).decode("ascii", errors="ignore")
        pos = m.start()
        matches.append((pos, code))

    by_code = defaultdict(list)
    for pos, code in matches:
        by_code[code].append(pos)

    with open(OUT, "w", encoding="utf-8") as out:
        out.write(f"PATH: {PATH}\n")
        out.write(f"SIZE: {size}\n")
        out.write(f"TOTAL_6DIGIT_CODES: {len(matches)}\n")
        out.write(f"UNIQUE_CODES: {len(by_code)}\n\n")

        out.write("TOP 200 CODES BY FIRST OCCURRENCE:\n")
        for code, positions in sorted(by_code.items(), key=lambda kv: kv[1][0])[:200]:
            out.write(f"{code}: count={len(positions)} first={positions[:10]}\n")
        out.write("\n")

        out.write("CODE CONTEXTS:\n")
        for code, positions in sorted(by_code.items(), key=lambda kv: kv[1][0]):
            for idx, pos in enumerate(positions[:3]):
                chunk, start = context(data, pos, before=64, after=96)
                out.write(f"\n=== CODE {code} occurrence {idx+1} at {pos} (context_start={start}) ===\n")
                out.write(hexdump(chunk) + "\n")

        out.write("\nPREFIX PATTERNS (16 bytes before code):\n")
        prefix_counter = Counter()
        suffix_counter = Counter()

        for pos, code in matches:
            pre = data[max(0, pos-16):pos]
            suf = data[pos+6:pos+22]
            prefix_counter[pre.hex()] += 1
            suffix_counter[suf.hex()] += 1

        out.write("TOP PREFIXES:\n")
        for hx, cnt in prefix_counter.most_common(50):
            out.write(f"{cnt}\t{hx}\n")

        out.write("\nTOP SUFFIXES:\n")
        for hx, cnt in suffix_counter.most_common(50):
            out.write(f"{cnt}\t{hx}\n")

    print(f"Saved output to: {OUT}")

if __name__ == "__main__":
    main()