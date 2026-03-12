import duckdb

# duckdb.sql("SELECT 42").show()

con = duckdb.connect("air_quality.db")

df = con.table("air_quality").to_df()
print(df)

print(con.execute("SHOW TABLES").fetchall())

con.sql(
    "CREATE TABLE IF NOT EXISTS users (username VARCHAR, age INTEGER, country VARCHAR)"
)

con.table("users").show()

con.close()

# with duckdb.connect("air_quality.db") as con:
#     df = con.table("air_quality").to_df()
#     print(df)
#     # create folder

# con2 = duckdb.connect("air_quality.db")

# print(con2.execute("SHOW TABLES").fetchall())
# con.sql("CREATE TABLE users (username VARCHAR, age INTEGER, country VARCHAR)")
# con.table("users").show()

# con2.sql("CREATE TABLE IF NOT EXISTS users (username VARCHAR, age INTEGER, country VARCHAR)")
# con2.table("users").show()
