import duckdb
import pandas as pd

cpi = duckdb.read_csv("PCPI24M1.csv")
cpi.show()


con = duckdb.connect("cpi.db")
con.execute("CREATE OR REPLACE TABLE cpi AS SELECT * FROM read_csv('PCPI24M1.csv')")
print(con.execute("SHOW TABLES").fetchall())
con.close()

file = "cpi.db"
# add Month 2 data as new data
new_data = pd.read_csv("PCPI25M2.csv")
new_data_columns = new_data.columns.str.strip().str.upper()


def append_data(con, data):
    con.sql("CREATE OR REPLACE TABLE cpi_append AS SELECT * FROM cpi")
    max_date = con.sql("SELECT MAX(date) FROM cpi_append").fetchone()[0]
    data = data[data["DATE"] > max_date]
    for _, row in data.iterrows():
        con.execute("INSERT INTO cpi_append VALUES (?, ?)", [row["DATE"], row["CPI"]])


with duckdb.connect(file) as con:
    con.sql("BEGIN TRANSACTION")  # starting a transaction
    append_data(con, new_data)
    con.sql("COMMIT")  # committing the transaction
    print("append_method")
    print(con.sql("SELECT * FROM cpi_append").fetchdf())


# truncate


def truncate_and_load(con, data):
    con.sql("CREATE OR REPLACE TABLE cpi_trunc AS SELECT * FROM cpi")
    con.sql("DELETE FROM cpi_trunc")

    for _, row in data.iterrows():
        con.execute("INSERT INTO cpi_trunc VALUES (?, ?)", [row["DATE"], row["CPI"]])


with duckdb.connect(file) as con:
    truncate_and_load(con, new_data)
    print("truncate_method")
    print(con.sql("SELECT * FROM cpi_trunc").fetchdf())


# incremental
def incremental_load(con, data):
    # creating a copy of the original data (not necessary in general)
    con.sql("CREATE OR REPLACE TABLE cpi_inc AS SELECT * FROM cpi")

    # find existing data
    existing = con.sql("SELECT DATE, CPI FROM cpi_inc").fetchdf()
    existing_col = existing.columns.str.upper()
    merged = existing.merge(data[["DATE", "CPI"]], on="DATE", suffixes=("_old", "_new"))
    revised_date = merged[merged["CPI_old"] != merged["CPI_new"]]["DATE"]

    # deleting "outdated" rows
    for date in revised_date:
        con.execute("DELETE FROM cpi_inc WHERE DATE = ?", [date])
    revise_rows = data[data["DATE"].isin(revised_date)]

    for _, row in revise_rows.iterrows():
        con.execute("INSERT INTO cpi_inc VALUES (?, ?)", [row["DATE"], row["CPI"]])

    # append new rows that did not exist before
    most_recent_date = con.sql("SELECT MAX(DATE) FROM cpi_inc").fetchone()[0]
    new_rows = data[data["DATE"] > most_recent_date]
    for _, row in new_rows.iterrows():
        con.execute("INSERT INTO cpi_inc VALUES (?, ?)", [row["DATE"], row["CPI"]])


with duckdb.connect(file) as con:
    con.sql("BEGIN TRANSACTION")
    incremental_load(con, new_data)
    con.sql("COMMIT")  # committing the transaction
    print("increment_method")
    print(con.sql("SELECT * FROM cpi_inc").fetchdf())

# verifying revised value differ across tables

print("\n spot check date = 2023:08 (revided 306.3 to 306.1)")
with duckdb.connect(file) as con:
    for table in ["cpi_append", "cpi_trunc", "cpi_inc"]:
        val = con.execute(f"SELECT CPI FROM {table} WHERE DATE = '2023:08'").fetchone()
        print(f"{table:15s} -> {val[0] if val else 'missing'}")
