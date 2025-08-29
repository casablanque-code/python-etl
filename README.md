# WeStocked Inventory ETL

ETL pipeline for transforming messy **inventory files** (XLSX, CSV, XML) into a clean CSV format, ready to be imported into [Supabase](https://supabase.com/).

This repository was built as part of the **WeStocked** inventory management system.

---

## Features

- ✅ Supports input formats: `.xlsx`, `.xls`, `.csv`, `.xml`
- ✅ Automatically detects headers (Russian / English aliases supported)
- ✅ Cleans and normalizes:
  - Inventory number (must start with `990000******`)
  - Serial numbers → uppercased
  - MAC addresses → normalized to `AA:BB:CC:DD:EE:FF`
- ✅ Filters only valid rows, drops unnecessary columns (e.g. cost, notes)
- ✅ Produces **exact schema required by Supabase**:
инвентарник, имя, локация, серийник, мак

- ✅ Outputs two CSV versions:
- `supabase_items.csv` → UTF-8 (for Supabase import)
- `supabase_items_excel.csv` → UTF-8 with BOM (for Excel on Windows, Cyrillic-safe)
- ✅ GitHub Actions CI:
- Runs ETL automatically on each push to `main`
- Publishes results as an **artifact** (`etl_outputs.zip`)
- Includes debug artifacts (`mapping_report.md`, `chosen_file.txt`, previews)

---

## Repository Structure

├─ input/ # Put your raw XLSX/CSV/XML files here
├─ output/ # ETL results + diagnostics (auto-generated)
├─ scripts/
│ ├─ config.py # Aliases & normalization rules
│ ├─ etl.py # Main ETL script
├─ .github/workflows/
│ └─ etl.yml # CI workflow
├─ requirements.txt # Python dependencies
└─ README.md

---

## Usage

### Local run

# 1. Install dependencies
pip install -r requirements.txt

# 2. Put your file into /input
cp your_inventory.xlsx input/

# 3. Run ETL
python -m scripts.etl
Outputs will appear in /output:

supabase_items.csv

supabase_items_excel.csv

mapping_report.md, preview_before_filter.csv, preview_after_filter.csv, etc.

GitHub Actions (CI/CD)
On each push to main:

Workflow runs the ETL.

Results are packaged into etl_outputs.zip.

Download from Actions → latest workflow run → Artifacts.

Example
Input (inventory number, name, cost, location, serial number, mac address, notes):

inventory number	name	cost	location	serial number	mac address	notes
990000123456	Router RB201	300.00	Office 1	SN12345	00:11:22:33:44:55	old
990000654321	Switch CBS	200.00	Office 2	SN67890	00-16-3E-7D-9A-FF	

Output (supabase_items.csv):

инвентарник	имя	локация	серийник	мак
990000123456	Router RB201	Office 1	SN12345	00:11:22:33:44:55
990000654321	Switch CBS	Office 2	SN67890	00:16:3E:7D:9A:FF
