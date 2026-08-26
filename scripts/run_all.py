import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "extract_infoex_records.py",
    "probe_dfcj_headers.py",
    "probe_header_fields.py",
    "export_dzh_index.py",
]

def main():
    scripts_dir = ROOT / "scripts"
    for script in SCRIPTS:
        path = scripts_dir / script
        print(f"\n=== Running {script} ===")
        result = subprocess.run([sys.executable, str(path)], cwd=str(ROOT))
        if result.returncode != 0:
            print(f"{script} failed with code {result.returncode}")
            sys.exit(result.returncode)

    print("\nAll scripts completed successfully.")

if __name__ == "__main__":
    main()