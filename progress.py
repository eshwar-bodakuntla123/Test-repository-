import re
import pandas as pd

def _norm(x):
    if pd.isna(x):
        return ""
    s = str(x)
    # normalize odd whitespace & punctuation variants
    s = s.replace("\u00A0", " ")  # NBSP -> space
    s = s.replace("–", "-").replace("—", "-")  # en/em dashes -> hyphen
    s = s.strip()
    # drop leading line numbers like "6 Date Range:"
    s = re.sub(r"^\s*\d+\s+", "", s)
    return s

def _find_first_cell(df, predicate):
    """Return (row, col) of first cell meeting predicate, else (None, None)."""
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            val = _norm(df.iat[r, c])
            if predicate(val):
                return r, c
    return None, None

def _parse_dates_from_text(text):
    # Accept YYYY/MM/DD or YYYY-MM-DD around 'to' with optional spaces
    m = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})\s*to\s*(\d{4}[-/]\d{2}[-/]\d{2})", text, flags=re.I)
    if not m:
        return None, None, None
    start_s, end_s = m.group(1), m.group(2)
    start = pd.to_datetime(start_s, errors="coerce")
    end   = pd.to_datetime(end_s, errors="coerce")
    return start, end, f"{start_s} to {end_s}"

def extract_date_range(df_all: pd.DataFrame):
    """
    Robustly extract (start_ts, end_ts, raw_str) for 'Date Range:' from a messy DataFrame.
    Returns (None, None, None) if not found.
    """
    # 1) Try cell-wise: find the cell that contains 'Date Range'
    r, c = _find_first_cell(df_all, lambda s: s.lower().startswith("date range"))
    if r is not None:
        # Gather the rest of the row to the right, joined with spaces
        right_cells = " ".join(_norm(df_all.iat[r, k]) for k in range(c, df_all.shape[1]))
        # If the label and value are split, try also cells after the label
        # Example: ["Date Range:", "2025/08/01 to 2025/08/28"]
        start, end, raw = _parse_dates_from_text(right_cells)
        if start is not None:
            return start, end, raw

    # 2) Fallback: join each entire row and search
    row_text = (
        df_all.applymap(_norm)
              .apply(lambda s: " ".join([x for x in s if x]), axis=1)
    )
    for txt in row_text:
        if "date range" in txt.lower():
            start, end, raw = _parse_dates_from_text(txt)
            if start is not None:
                return start, end, raw

    # 3) Last resort: scan all cells and parse any dates around 'to'
    all_cells = " ".join(df_all.applymap(_norm).stack().tolist())
    start, end, raw = _parse_dates_from_text(all_cells)
    if start is not None:
        return start, end, raw

    return None, None, None

# ---------- Example usage ----------
# Read your file as a raw grid (no header) to retain the metadata rows
# df_all = pd.read_csv("sample1.csv", header=None, dtype=str, engine="python", on_bad_lines="skip")

# start_ts, end_ts, raw = extract_date_range(df_all)
# print("Raw Date Range:", raw)
# print("Start:", start_ts)
# print("End:", end_ts)