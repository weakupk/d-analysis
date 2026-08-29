import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_comparison(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt_pct(num: int, den: int) -> str:
    if den == 0:
        return "0.0%"
    return f"{(num / den) * 100:.1f}%"


def main():
    parser = argparse.ArgumentParser(description="Summarize semantic field comparison output.")
    parser.add_argument(
        "--in-file",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks\semantic_fields_compare.json",
        help="Path to semantic_fields_compare.json",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
        help="Directory for summary output.",
    )
    args = parser.parse_args()

    in_path = Path(args.in_file)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_comparison(in_path)
    codes = data.get("codes", [])
    fields = data.get("fields", [])
    total_codes = len(codes)
    total_fields = len(fields)

    const_u32 = [f for f in fields if f.get("is_constant_u32")]
    const_raw = [f for f in fields if f.get("is_constant_raw")]
    variable_fields = [f for f in fields if not f.get("is_constant_u32")]
    fully_present = [f for f in fields if len(f.get("present_in", [])) == total_codes]
    partially_missing = [f for f in fields if 0 < len(f.get("present_in", [])) < total_codes]
    fully_missing = [f for f in fields if len(f.get("present_in", [])) == 0]

    presence_counter = Counter()
    change_counter = Counter()
    field_value_spread = []

    for field in fields:
        presence_counter[len(field.get("present_in", []))] += 1
        change_counter[field.get("unique_u32_count", 0)] += 1
        field_value_spread.append(
            (
                field.get("unique_u32_count", 0),
                field.get("unique_raw_count", 0),
                field.get("field", ""),
            )
        )

    field_value_spread.sort(key=lambda x: (-x[0], -x[1], x[2]))

    summary_path = out_dir / "semantic_fields_summary.txt"
    summary_json_path = out_dir / "semantic_fields_summary.json"

    summary = {
        "codes": codes,
        "total_fields": total_fields,
        "constant_u32_fields": [f.get("field") for f in const_u32],
        "constant_raw_fields": [f.get("field") for f in const_raw],
        "variable_fields": [f.get("field") for f in variable_fields],
        "fully_present_fields": [f.get("field") for f in fully_present],
        "partially_missing_fields": [f.get("field") for f in partially_missing],
        "fully_missing_fields": [f.get("field") for f in fully_missing],
        "presence_distribution": {str(k): v for k, v in sorted(presence_counter.items())},
        "unique_u32_distribution": {str(k): v for k, v in sorted(change_counter.items())},
        "most_variable_fields": [
            {"field": field, "unique_u32_count": u32c, "unique_raw_count": rawc}
            for u32c, rawc, field in field_value_spread[:20]
        ],
    }

    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Semantic fields summary\n")
        f.write(f"codes: {', '.join(codes)}\n")
        f.write(f"total_fields: {total_fields}\n")
        f.write(f"constant_u32_fields: {len(const_u32)}\n")
        f.write(f"constant_raw_fields: {len(const_raw)}\n")
        f.write(f"variable_fields: {len(variable_fields)}\n")
        f.write(f"fully_present_fields: {len(fully_present)}\n")
        f.write(f"partially_missing_fields: {len(partially_missing)}\n")
        f.write(f"fully_missing_fields: {len(fully_missing)}\n\n")

        f.write("Presence distribution (number of stocks with field present):\n")
        for present_count, count in sorted(presence_counter.items()):
            f.write(f"  {present_count}: {count}\n")
        f.write("\nUnique u32 distribution (field -> unique u32 values):\n")
        for unique_count, count in sorted(change_counter.items()):
            f.write(f"  {unique_count}: {count}\n")
        f.write("\nMost variable fields:\n")
        for unique_u32_count, unique_raw_count, field_name in field_value_spread[:20]:
            f.write(f"  {field_name:<24} u32={unique_u32_count} raw={unique_raw_count}\n")
        f.write("\nConstant u32 fields:\n")
        for field in const_u32:
            f.write(f"  {field.get('field')}\n")
        f.write("\nConstant raw fields:\n")
        for field in const_raw:
            f.write(f"  {field.get('field')}\n")

    print(f"Saved: {summary_json_path}")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()