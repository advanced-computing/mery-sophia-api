# loading CPI the hard way

# import all libraries
import re
from datetime import datetime

import duckdb
import pandas as pd

# set configuration
file = "pcpiMvMd.xlsx"
db_file = "cpi_hard.db"


def parse_old_date(col: str) -> datetime:
    """change column name to datetime format of the release date
    example: PCPI98M11 -> datetime(1998, 11, 1)"""
    m = re.fullmatch(r"PCPI(\d{2})M(\d{1,2})", col, re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse vintage column: {col!r}")
    yy = int(m.group(1))
    month = int(m.group(2))
    year = (2000 + yy) if yy < 30 else (1900 + yy)
    return datetime(year, month, 1)


def get_old_columns(df: pd.DataFrame) -> list:
    """Return all PCPI column on dataset in chronoloogical order"""
    cols = [
        c
        for c in df.columns
        if re.fullmatch(r"PCPI(\d{2})M(\d{1,2})", c, re.IGNORECASE)
    ]
    return sorted(cols, key=parse_old_date)


print("Loading Excel file (once)...")
_RAW = pd.read_excel(file, na_values=["#N/A", "NA", "N/A", ""], engine="openpyxl")
_RAW.columns = _RAW.columns.str.strip()
_RAW = _RAW.rename(columns={_RAW.columns[0]: "DATE"})
_RAW["DATE"] = _RAW["DATE"].str.strip()
_OLD_COLS = sorted(
    [
        c
        for c in _RAW.columns
        if re.fullmatch(r"PCPI(\d{2})M(\d{1,2})", c, re.IGNORECASE)
    ],
    key=parse_old_date,
)
print(f"Loaded {len(_RAW)} rows, {len(_OLD_COLS)} vintage columns.")


# insert data


def get_lastest_data(download_date: str) -> pd.DataFrame:
    pull_dt = datetime.strptime(download_date, "%Y-%m-%d")

    eligible = [c for c in _OLD_COLS if parse_old_date(c) <= pull_dt]
    if not eligible:
        raise ValueError(
            f"No old data found before {download_date}."
            f"Earliest old date in file: {_OLD_COLS[0] if _OLD_COLS else 'none'}"
        )
    lastest_col = eligible[-1]

    df = _RAW[["DATE", lastest_col]].copy()
    df = df.rename(columns={lastest_col: "CPI"})
    df["CPI"] = pd.to_numeric(df["CPI"], errors="coerce")
    df = df.dropna(subset=["CPI"]).reset_index(drop=True)

    return df[["DATE", "CPI"]]


# innitialize database
def initialize_db():
    with duckdb.connect(db_file) as con:
        for table in ["cpi_append", "cpi_trunc", "cpi_inc"]:
            con.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table} (
                        DATE VARCHAR,
                        CPI DOUBLE)
                        """)


# append method
def append_data(con, download_date: str) -> int:
    data = get_lastest_data(download_date)
    max_date = con.sql("SELECT MAX(DATE) FROM cpi_append").fetchone()[0]
    new_rows = data if max_date is None else data[data["DATE"] > max_date]
    for _, row in new_rows.iterrows():
        con.execute("INSERT INTO cpi_append VALUES (?, ?)", [row["DATE"], row["CPI"]])
    return len(new_rows)


# truncate method
def truncate_data(con, download_date: str) -> int:
    data = get_lastest_data(download_date)
    con.execute("DELETE FROM cpi_trunc")
    for _, row in data.iterrows():
        con.execute("INSERT INTO cpi_trunc VALUES (?, ?)", [row["DATE"], row["CPI"]])
    return len(data)


# increment method
def incremental_data(con, download_date: str) -> dict:
    data = get_lastest_data(download_date)

    # find and fix revised rows
    existing = con.sql("SELECT DATE, CPI FROM cpi_inc").fetchdf()
    existing.columns = existing.columns.str.upper()

    revised_date = pd.Series(dtype=str)
    if not existing.empty:
        merged = existing.merge(
            data[["DATE", "CPI"]], on="DATE", suffixes=("_old", "_new")
        )
        revised_date = merged[merged["CPI_old"] != merged["CPI_new"]]["DATE"]
        for date in revised_date:
            con.execute("DELETE FROM cpi_inc WHERE DATE = ?", [date])
    for _, row in data[data["DATE"].isin(revised_date)].iterrows():
        con.execute("INSERT INTO cpi_inc VALUES (?, ?)", [row["DATE"], row["CPI"]])

    # append new rows
    most_recent = con.sql("SELECT MAX(DATE) FROM cpi_inc").fetchone()[0]
    new_rows = data if most_recent is None else data[data["DATE"] > most_recent]

    for _, row in new_rows.iterrows():
        con.execute("INSERT INTO cpi_inc VALUES(?, ?)", [row["DATE"], row["CPI"]])
    return {"revised": len(revised_date), "inserted": len(new_rows)}


# main

if __name__ == "__main__":
    DOWNLOAD_DATE = "2025-02-15"

    initialize_db()

    with duckdb.connect(db_file) as con:
        con.execute("BEGIN TRANSACTION")
        n = append_data(con, DOWNLOAD_DATE)
        con.execute("COMMIT")
        print(f"\n[append] rows inserted : {n}")
        print(con.sql("SELECT * FROM cpi_append").fetchdf())

    with duckdb.connect(db_file) as con:
        n = truncate_data(con, DOWNLOAD_DATE)
        print(f"\n[trunc] rows landed : {n}")
        print(con.sql("SELECT * FROM cpi_trunc").fetchdf())

    with duckdb.connect(db_file) as con:
        con.execute("BEGIN TRANSACTION")
        result = incremental_data(con, DOWNLOAD_DATE)
        con.execute("COMMIT")
        print(f"\n[incremental] {result}")
        print(con.sql("SELECT * FROM cpi_inc").fetchdf())

    # check all table
    print("\n-- check: DATE = 2003:09 --")
    with duckdb.connect(db_file) as con:
        for tbl in ["cpi_append", "cpi_trunc", "cpi_inc"]:
            val = con.execute(
                f"SELECT CPI FROM {tbl} WHERE DATE = '2003:09'"
            ).fetchone()
            print(f" {tbl:15s} -> {val[0] if val else 'missing'}")
