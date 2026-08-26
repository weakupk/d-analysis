# Analysis Notes

This repository contains detailed findings from analyzing Dazhihui 365 (dzh365) local binary files.

## Current Findings

### 1. DFCJ 16-Byte Block Header Structure (100% Verified)
- `+0..3` (`uint32_le`): Record Count (`rec_count`) - Number of K-line / Tick records in the 8KB block.
- `+4..7` (`uint32_le`): Compressed Payload Size (`comp_size`).
- `+8` (`uint8`): Compression Type (`0xf0` = Uncompressed/Bitpacked, `0xf1`/`0xf2` = Daily Delta stream, `0xe0` = Minute stream).
- `+9..11` (`uint24_le`): Uncompressed Stream Size (`uncomp_size`).
- `+12..15` (`uint32_le`): Checksum / Block Flags.

### 2. Full Security Code to Block Mapping (Exported to CSV)
- All SH and SZ index mapping files parsed from `0x6000` offset in `DAY_2.DAT`, `MIN1_2.DAT`, `MIN_2.DAT`, `ReportCps_2.DAT`.
- Complete CSV maps saved under `analysis/outputs/` (e.g. `SH_DAY_2_index_map.csv`, `SZ_DAY_2_index_map.csv`, etc.).

### 3. Record Layout Identification
- Uncompressed (`0xf0`) block probes confirmed K-line structs contain IEEE 754 float32 prices (Open, High, Low, Close) and uint32/float32 (Volume, Amount).

## Roadmap for Analysis

1. INFOEX Metadata Parsing: Complete layout decoding for INFOEX.DAT to map symbol codes.
2. DFCJ Header & Index Mapping: Analyze DAY_2.DAT index offset table to match stock codes with block locations in DAY_2.DAT.dat.
3. K-Line & Tick Record Format: Decode binary struct layouts (Date, Open, High, Low, Close, Volume) in .DAT.dat files.
4. Tooling & Exporters: Write unified Python extractors to export clean CSV/Parquet data.
