\# dzh365 analysis



This repository contains scripts for analyzing Dazhihui 365 local data files.



\## Goals

\- Inspect file structures

\- Infer record formats

\- Extract security metadata

\- Probe index files and context around codes



\## Data path

Raw data is stored locally at:



`D:\\Program\\dzh365(64)\\data`



The raw data folder is not committed to git.



\## Usage

Run scripts from the `scripts/` directory and save output to `outputs/`.

\## Analysis workflow

The analysis pipeline runs in five steps. Start from the project root.

\### Step 1 – Export a raw block file

Reads the stock's 8 192-byte block from the source `.DAT` file and writes it
to `outputs/stocks/{code}_block.bin`.

```powershell
python .\scripts\export_block_bin.py --code 600519
```

Repeat for every stock you want to analyse:

```powershell
python .\scripts\export_block_bin.py --code 000001
python .\scripts\export_block_bin.py --code 000858
```

The script reads `outputs\export_plan.csv` to locate the correct source file
and byte offset. If the plan file is missing, regenerate it first:

```powershell
python .\scripts\build_export_plan.py
```

\### Step 2 – Extract semantic fields

Parses the named offsets inside a block and writes
`outputs/stocks/{code}_semantic_fields.json` and `*_semantic_fields.txt`.

```powershell
python .\scripts\extract_block_fields_semantic.py --code 600519 `
    --in-file outputs\stocks\600519_block.bin `
    --out-dir outputs\stocks
```

\### Step 3 – Compare semantic fields across stocks

Compares the semantic fields of all stocks found in `outputs/stocks/` and
writes `outputs/stocks/semantic_fields_compare.json`.

```powershell
python .\scripts\compare_semantic_fields.py
```

\### Step 4 – Summarize the comparison

Produces a human-readable summary at `outputs/stocks/semantic_fields_summary.*`.

```powershell
python .\scripts\summarize_semantic_comparison.py
```

\### Step 5 – Find variable (business) offsets

Scans all 4-byte-aligned positions across multiple raw blocks and reports
which offsets differ between stocks – these are the candidate business fields.
Requires the `*_block.bin` files from Step 1.

```powershell
python .\scripts\find_variable_offsets.py `
    --code 600519 --code 000001 --code 000858 `
    --in-dir outputs\stocks `
    --out-dir outputs\stocks
```

