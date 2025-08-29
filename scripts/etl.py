import sys
from pathlib import Path
import pandas as pd
from lxml import etree
from scripts.config import COLUMN_ALIASES, TARGET_HEADERS_RU, INV_FILTER_REGEX, norm, clean_text, clean_serial, clean_mac

IN_DIR = Path("input")
OUT_DIR = Path("output")

def pick_best_sheet(xlsx: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(xlsx)
    best_df, best_score = None, -1
    for name in xl.sheet_names:
        df = xl.parse(name, header=None)
        score = int(df.notna().sum().sum())
        if score > best_score:
            best_df, best_score = df, score
    return best_df

def detect_header_row(df: pd.DataFrame):
    alias_flat = set().union(*COLUMN_ALIASES.values())
    for i in range(min(len(df), 50)):
        row = df.iloc[i].astype(str).fillna("").tolist()
        normed = [norm(x) for x in row]
        hits = sum(1 for x in normed if x in alias_flat)
        if hits >= 2:
            return i, normed
    return 0, [norm(x) for x in df.iloc[0].astype(str).fillna("").tolist()]

def headers_to_columns(headers_norm, width):
    return headers_norm + [""]*(width-len(headers_norm))

def map_columns(headers_norm):
    mapping = {}
    for key, aliases in COLUMN_ALIASES.items():
        for idx, h in enumerate(headers_norm):
            if h in aliases or h == key:
                mapping[key] = idx
                break
    return mapping

def to_target_df_from_matrix(df: pd.DataFrame) -> pd.DataFrame:
    hdr_idx, hdr_norm = detect_header_row(df)
    width = df.shape[1]
    hdr_norm = headers_to_columns(hdr_norm, width)
    mapping = map_columns(hdr_norm)
    data = df.iloc[hdr_idx+1:].reset_index(drop=True)
    def col(ix): 
        return data.iloc[:, ix] if ix is not None and ix in range(width) else pd.Series([""]*len(data))
    out = pd.DataFrame()
    out["инвентарник"] = col(mapping.get("inv")).map(clean_text)
    out["имя"] = col(mapping.get("name")).map(clean_text)
    out["локация"] = col(mapping.get("location")).map(clean_text)
    out["серийник"] = col(mapping.get("serial")).map(clean_serial)
    out["мак"] = col(mapping.get("mac")).map(clean_mac)
    return out

def read_any(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".csv": return pd.read_csv(path, header=None)
    if suf in {".xlsx", ".xls"}: return pick_best_sheet(path)
    if suf == ".xml":
        tree = etree.parse(str(path)); root = tree.getroot()
        rows = list(root)
        norm_rows = []
        for el in rows:
            row = {}
            for k,v in el.attrib.items(): row[norm(k)] = v
            for ch in el:
                if ch.text and ch.text.strip(): row[norm(ch.tag)] = ch.text.strip()
            if row: norm_rows.append(row)
        df = pd.DataFrame(norm_rows)
        # добавим строку с "шапкой" для общего механизма
        if not df.empty:
            hdr = [norm(c) for c in df.columns]
            df = pd.concat([pd.DataFrame([hdr]), df], ignore_index=True)
        return df
    raise ValueError(f"Unsupported file type: {suf}")

def main():
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    files = sorted([p for p in IN_DIR.glob("*.*") if p.suffix.lower() in {".xlsx",".xls",".csv",".xml"}])
    if not files:
        print("No input files in input/.")
        sys.exit(1)
    src = files[0]
    print("Processing:", src.name)
    df_raw = read_any(src)
    target = to_target_df_from_matrix(df_raw)
    # Фильтр по инвентарнику 990000******
    mask = target["инвентарник"].astype(str).str.match(INV_FILTER_REGEX, na=False)
    target = target[mask].copy()
    # Дедуп по инвентарнику (первая запись остаётся)
    target = target.drop_duplicates(subset=["инвентарник"], keep="first")
    # Гарантируем порядок и наличие столбцов
    target = target[["инвентарник","имя","локация","серийник","мак"]]
    target.to_csv(OUT_DIR/"supabase_items.csv", index=False, encoding="utf-8")
    print("Done. Output → output/supabase_items.csv")

if __name__ == "__main__":
    main()
