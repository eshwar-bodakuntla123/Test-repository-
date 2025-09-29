import re
import pandas as pd

def extract_date_range_from_df(df_all: pd.DataFrame):
    """
    Find a row containing 'Date Range:' anywhere in the dataframe (any column),
    extract 'YYYY/MM/DD to YYYY/MM/DD', and return (start_ts, end_ts, raw_str).
    Returns (None, None, None) if not found.
    """
    # Join each row to one string like "6, Date Range:, 2025/08/01 to 2025/08/28"
    row_text = (
        df_all
        .astype(str)
        .replace({"nan": ""})
        .apply(lambda s: ", ".join([x.strip() for x in s if x.strip() != ""]), axis=1)
    )

    # Find first row that mentions Date Range:
    candidates = row_text[row_text.str.contains(r"\bDate Range:\b", na=False)]
    if candidates.empty:
        return None, None, None

    line = candidates.iloc[0]

    # Extract pattern "YYYY/MM/DD to YYYY/MM/DD"
    m = re.search(r"(\d{4}/\d{2}/\d{2})\s*to\s*(\d{4}/\d{2}/\d{2})", line)
    if not m:
        return None, None, line  # raw line for debugging

    start_s, end_s = m.group(1), m.group(2)
    start_ts = pd.to_datetime(start_s, format="%Y/%m/%d", errors="coerce")
    end_ts   = pd.to_datetime(end_s,   format="%Y/%m/%d", errors="coerce")
    return start_ts, end_ts, f"{start_s} to {end_s}"


# ---------------- Example usage ----------------
# If you already loaded your CSV-ish content into a DataFrame:
# df_all = pd.read_csv("sample1.csv", header=None, dtype=str, engine="python", on_bad_lines="skip")

start_ts, end_ts, raw = extract_date_range_from_df(df_all)
print("Raw Date Range:", raw)
print("Start:", start_ts)
print("End:", end_ts)