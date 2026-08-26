import argparse
import json
from collections import Counter
from pathlib import Path

DEFAULT_CODES = ["000001", "000002", "000011", "000012", "000015", "600000", "600001"]


def load_records_csv(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            if "," not in line:
                continue
            parts = line.split(",", len(header) - 1)
            row = dict(zip(header, parts))
            rows.append(row)
    return rows


def parse_hexdump(hexdump_text: str):
    bytes_out = []
    for line in hexdump_text.splitlines():
        if ":" not in line:
            continue
        _, hex_part = line.split(":", 1)
        hex_part = hex_part.strip()
        if not hex_part:
            continue
        for token in hex_part.split():
            if len(token) != 2:
                continue
            try:
                bytes_out.append(int(token, 16))
            except ValueError:
                pass
    return bytes_out


def byte_to_printable(b: int) -> str:
    return chr(b) if 32 <= b <= 126 else "."


def compare_window(rows, codes):
    selected = []
    for code in codes:
        match = next((r for r in rows if r["code"] == code and r.get("occurrence", "1") == "1"), None)
        if match:
            selected.append(match)
    if not selected:
        raise SystemExit("No matching codes found in the CSV.")

    byte_arrays = {r["code"]: parse_hexdump(r["hexdump"]) for r in selected}
    min_len = min(len(b) for b in byte_arrays.values())

    stability = []
    for i in range(min_len):
        values = [byte_arrays[code][i] for code in byte_arrays]
        counter = Counter(values)
        common_val, common_count = counter.most_common(1)[0]
        stability.append({
            "offset": i,
            "values": {code: byte_arrays[code][i] for code in byte_arrays},
            "common_value": common_val,
            "common_count": common_count,
            "all_same": len(counter) == 1,
        })

    return selected, stability


def summarize_stability(stability):
    stable_offsets = [x["offset"] for x in stability if x["all_same"]]
    unstable_offsets = [x["offset"] for x in stability if not x["all_same"]]
    return {
        "compared_offsets": len(stability),
        "stable_offsets": stable_offsets,
        "unstable_offsets": unstable_offsets,
        "stable_count": len(stable_offsets),
        "unstable_count": len(unstable_offsets),
    }


def write_report(out_path: Path, selected, stability, summary):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("INFOEX FIELD COMPARISON REPORT\n")
        f.write(f"CODES: {', '.join(r['code'] for r in selected)}\n")
        f.write(f"COMPARED_OFFSETS: {summary['compared_offsets']}\n")
        f.write(f"STABLE_OFFSETS: {summary['stable_count']}\n")
        f.write(f"UNSTABLE_OFFSETS: {summary['unstable_count']}\n\n")

        f.write("SELECTED RECORDS\n")
        for r in selected:
            f.write(f"- code={r['code']} position={r['position']} context_start={r['context_start']}\n")
            f.write(f"  u32_before_16={r['u32_before_16']} u32_at_0={r['u32_at_0']} u32_after_6={r['u32_after_6']} f32_after_16={r['f32_after_16']}\n")
            f.write(f"  strings={r['strings']}\n")
        f.write("\nSTABLE BYTE OFFSETS (all selected codes identical)\n")
        for offset in summary["stable_offsets"][:200]:
            vals = stability[offset]["values"]
            preview = " ".join(f"{code}:{vals[code]:02x}" for code in vals)
            f.write(f"  +{offset:04d}: {preview}\n")

        f.write("\nFIRST 128 OFFSETS DETAIL\n")
        for item in stability[:128]:
            vals = item["values"]
            ascii_preview = "".join(byte_to_printable(vals[code]) for code in vals)
            f.write(f"  +{item['offset']:04d}: common={item['common_value']:02x} same={item['all_same']} ascii={ascii_preview}\n")


def main():
    parser = argparse.ArgumentParser(description="Compare INFOEX.DAT record windows across selected codes.")
    parser.add_argument("--records-csv", default=r"D:\Program\dzh365(64)\analysis\outputs\INFOEX_records.csv")
    parser.add_argument("--codes", nargs="*", default=DEFAULT_CODES)
    parser.add_argument("--out", default=r"D:\Program\dzh365(64)\analysis\outputs\INFOEX_field_compare.txt")
    args = parser.parse_args()

    rows = load_records_csv(Path(args.records_csv))
    selected, stability = compare_window(rows, args.codes)
    summary = summarize_stability(stability)
    write_report(Path(args.out), selected, stability, summary)
    print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
