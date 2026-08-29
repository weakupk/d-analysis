import argparse
import json
from pathlib import Path

DEFAULT_FIELDS = [
    "page_ts_1",
    "page_ts_2",
    "page_zero",
    "page_count_a",
    "page_flag_all_ones",
    "page_count_b",
    "page_id",
    "subpage_header_1",
    "subpage_zero",
    "subpage_id",
    "subpage_type",
    "subpage_flag",
    "subpage_magic",
    "subtable_count",
    "subtable_ts",
    "subtable_v1",
    "subtable_v2",
    "subtable_v3",
    "subtable_v4",
    "subtable_len",
    "subtable_value_1",
    "subtable_value_2",
    "page2_ts_1",
    "page2_ts_2",
    "page2_zero",
    "page2_count_a",
    "page2_flag_all_ones",
    "page2_count_b",
    "page2_id",
    "subpage2_header_1",
    "subpage2_zero",
    "subpage2_id",
    "subpage2_type",
    "subpage2_flag",
    "subpage2_magic",
    "subtable2_count",
    "subtable2_ts",
    "subtable2_v1",
    "subtable2_v2",
    "subtable2_v3",
    "subtable2_v4",
    "subtable2_len",
    "subtable2_value_1",
    "subtable2_value_2",
]


def load_semantic_fields(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {row["field"]: row for row in data.get("fields", [])}


def pick_value(row: dict):
    if row is None:
        return None
    return {
        "offset_hex": row.get("offset_hex"),
        "raw_hex": row.get("raw_hex"),
        "u32": row.get("u32"),
        "i32": row.get("i32"),
        "f32": row.get("f32"),
        "tags": row.get("tags", []),
    }


def main():
    parser = argparse.ArgumentParser(description="Compare semantic fields across multiple stocks.")
    parser.add_argument("--codes", required=True, help="Comma-separated stock codes")
    parser.add_argument(
        "--in-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\Program\dzh365(64)\analysis\outputs\stocks",
    )
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    print("codes:", codes)

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stock_data = {}
    for code in codes:
        path = in_dir / f"{code}_semantic_fields.json"
        if not path.exists():
            raise SystemExit(f"Missing input file: {path}")
        stock_data[code] = load_semantic_fields(path)

    all_fields = list(DEFAULT_FIELDS)
    for fields in stock_data.values():
        for field in fields.keys():
            if field not in all_fields:
                all_fields.append(field)

    comparison = {"codes": codes, "fields": []}

    for field in all_fields:
        per_stock = {code: pick_value(stock_data[code].get(field)) for code in codes}
        values = [v for v in per_stock.values() if v is not None]
        unique_u32 = sorted({v["u32"] for v in values if v["u32"] is not None})
        unique_raw = sorted({v["raw_hex"] for v in values if v["raw_hex"] is not None})
        comparison["fields"].append(
            {
                "field": field,
                "present_in": [code for code in codes if per_stock[code] is not None],
                "missing_in": [code for code in codes if per_stock[code] is None],
                "per_stock": per_stock,
                "unique_u32_count": len(unique_u32),
                "unique_raw_count": len(unique_raw),
                "is_constant_u32": len(unique_u32) == 1 and len(values) == len(codes),
                "is_constant_raw": len(unique_raw) == 1 and len(values) == len(codes),
            }
        )

    json_path = out_dir / "semantic_fields_compare.json"
    txt_path = out_dir / "semantic_fields_compare.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Semantic field comparison\n")
        f.write(f"codes: {', '.join(codes)}\n\n")
        for field in comparison["fields"]:
            status = "CONST" if field["is_constant_u32"] else "VAR"
            f.write(f"{field['field']:<24} {status} present={','.join(field['present_in'])}\n")
            for code in codes:
                row = field["per_stock"][code]
                if row is None:
                    f.write(f"  {code}: missing\n")
                else:
                    tags = ",".join(row.get("tags", []))
                    f.write(
                        f"  {code}: off={row['offset_hex']} raw={row['raw_hex']} "
                        f"u32={row['u32']} i32={row['i32']} f32={row['f32']:.6g} {tags}\n"
                    )
            f.write("\n")

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    main()