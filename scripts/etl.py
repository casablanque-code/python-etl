import sys
from pathlib import Path
import pandas as pd
from lxml import etree

from scripts.config import COLUMN_ALIASES, TARGET_HEADERS_RU, REQUIRED_FIELDS, norm, clean_text, clean_serial, clean_mac

IN_DIR = Path("input")
OUT_DIR = Path("output")

def map_columns(df: pd.DataFrame):
    cols = [norm(c) for c in df.columns]
    mapping = {}
    for key, aliases in COLUMN_ALIASES.items():
        found = None
        for idx, c in enumerate(cols):
            if c in aliases or c == key:
                found = df.columns[idx]
                break
        if found is not None:
            mapping[key] = found
    return mapping

def to_target_df(df: pd.DataFrame) -> pd.DataFrame:
    mapping = map_columns(df)
    out = pd.DataFrame()
    out["инвентарник"] = df[mapping["inv"]].map(clean_text) if "inv" in mapping else ""
    out["имя"] = df[mapping["name"]].map(clean_text) if "name" in mapping else ""
    out["локация"] = df[mapping["location"]].map(clean_text) if "location" in mapping else ""
    out["серийник"] = df[mapping["serial"]].map(clean_serial) if "serial" in mapping else ""
    out["мак"] = df[mapping["mac"]].map(clean_mac) if "mac" in mapping else ""
    return out

def read_any(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suf == ".xml":
        return read_xml_generic(path)
    raise ValueError(f"Unsupported file type: {suf}")

def read_xml_generic(path: Path) -> pd.DataFrame:
    # Универсальный разбор: ищем «повторяющиеся» элементы-записи.
    # Считаем кандидатами тэги: item, record, row, device, entry, node
    tree = etree.parse(str(path))
    root = tree.getroot()
    candidates = root.xpath(".//*[self::item or self::record or self::row or self::device or self::entry or self::node]")
    # Если кандидатов нет — fallback: берём всех детей корня
    rows = candidates if candidates else list(root)
    norm_rows = []
    for el in rows:
        row = {}
        # атрибуты
        for k, v in el.attrib.items():
            row[norm(k)] = v
        # прямые дети
        for ch in el:
            if ch.text and ch.text.strip():
                row[norm(ch.tag)] = ch.text.strip()
            # если есть вложенные структуры, можно углубиться по необходимости
        if row:
            norm_rows.append(row)
    if not norm_rows:
        return pd.DataFrame()
    df = pd.DataFrame(norm_rows)
    return df

def validate_and_split(df_target: pd.DataFrame):
    valid_mask = df_target["инвентарник"].astype(str).str.len() > 0
    valid_mask &= df_target["имя"].astype(str).str.len() > 0
    valid = df_target[valid_mask].copy()
    invalid = df_target[~valid_mask].copy()
    return valid, invalid

def main():
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    files = list(IN_DIR.glob("*.*"))
    if not files:
        print("No input files in input/. Put your XLSX/CSV/XML there and push.")
        sys.exit(1)
    # Берём первый найденный (или можно перебор всех — оставим просто)
    src = files[0]
    print("Processing:", src.name)
    df = read_any(src)
    if df.empty:
        print("Parsed 0 rows → check input format/structure.")
    target = to_target_df(df)
    valid, invalid = validate_and_split(target)
    # дедуп по инвентарнику
    valid = valid.drop_duplicates(subset=["инвентарник"], keep="first")
    # save
    valid.to_csv(OUT_DIR/"supabase_items.csv", index=False, encoding="utf-8")
    if not invalid.empty:
        invalid.to_csv(OUT_DIR/"invalid_rows.csv", index=False, encoding="utf-8")
    # report
    with (OUT_DIR/"report.md").open("w", encoding="utf-8") as f:
        f.write("# ETL Report\n\n")
        f.write(f"Файл: **{src.name}**\n\n")
        f.write(f"Всего строк: {len(target)}\n\n")
        f.write(f"Валидных: {len(valid)}, отброшено: {len(invalid)}\n")
    print("Done. Output → output/supabase_items.csv")

if __name__ == "__main__":
    main()
