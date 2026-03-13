import duckdb
import pandas as pd
from flask import Flask, Response, jsonify, request
from pandas.api.types import is_string_dtype

app = Flask(__name__)

csv_path = "Air_Quality.csv"


# set unique identifier column name
id_col = "Unique ID"


@app.route("/")
def hello_world():
    """Return a friendly HTTP greeting."""

    return "<p>Hello, Welcome to NYC Air Quality API!!</p>"


# get list of records
@app.get("/api/list")
def list_records():

    # Get the query parameters
    format = request.args.get("format", "json").lower()
    filterby = request.args.get("filterby", None)
    filtervalue = request.args.get("filtervalue", None)
    sortby = request.args.get("sortby", None)
    order = request.args.get("order", "asc").lower()

    try:
        limit = int(request.args.get("limit", 1000))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return "Invalid limit/offset: must be integers"

    if limit < 0 or offset < 0:
        return "Invalid limit/offset: must be non-negative"

    # Load the data
    data = pd.read_csv(csv_path)
    data.columns = data.columns.str.strip()  # Strip whitespace from column names

    # filter the data
    data = filter_by_value(data, filterby, filtervalue)
    if not isinstance(data, pd.DataFrame):
        return data

    data = apply_sort(data, sortby, order)
    if not isinstance(data, pd.DataFrame):
        return data

    # apply limit and offset
    paged = apply_limit_offset(data, limit, offset)

    # conver to requested format
    return convert_to_format(paged, format)


# record id as a parameter
@app.get("/api/record/<record_id>")
def get_record(record_id):
    data = pd.read_csv(csv_path)
    data.columns = data.columns.str.strip()

    if id_col not in data.columns:
        return "Invalid Identifier Column"

    match = data[data[id_col].astype(str) == str(record_id)]
    if match.empty:
        return "record not found"

    # keeping as a one row data frame

    one_row_df = match.iloc[[0]]
    format = request.args.get("format", "json").lower()
    return convert_to_format(one_row_df, format)


# GET: view all users
@app.get("/users")
def get_users():
    con = duckdb.connect("air_quality.db")
    users = con.sql("SELECT * FROM users").fetchall()
    con.close()
    return jsonify([{"username": u[0], "age": u[1], "country": u[2]} for u in users])


# GET: Use HTML form to add user from the browser
# because POST only works on terminal, we create HTML to make input available in website
@app.route("/users/add")
def add_user_form():
    return """
        <h2>Add a New User</h2>
        <form method="POST" action="/users">
            <label>Username: <input name="username" placeholder="Username"></label><br><br>
            <label>Age: <input name="age" placeholder="Age" type="number"></label><br><br>
            <label>Country: <input name="country" placeholder="Country"></label><br><br>
            <button type="submit">Add User</button>
        </form>
    """


# POST: Add a new user (accepts both JSON and HTML form)
@app.post("/users")
def add_user():
    if request.is_json:
        data = request.get_json()

    else:
        data = request.form

    username = data.get("username")
    age = data.get("age")
    country = data.get("country")

    if not username or not age or not country:
        return jsonify({"error": "all fields are required"}), 400

    con = duckdb.connect("air_quality.db")
    con.execute(
        "INSERT INTO users (username, age, country) VALUES (?, ?, ?)",
        [username, age, country],
    )
    con.close()
    return jsonify({"message": f"User '{username}' added"})


# GET: User stats
@app.get("/users/stats")
def get_user_stats():
    con = duckdb.connect("air_quality.db")

    count = con.sql("SELECT COUNT(*) FROM users").fetchone()[0]
    avg_age = con.sql("SELECT AVG(age) FROM users").fetchone()[0]
    top_countries = con.sql("""
        SELECT country, COUNT(*) as total 
        FROM users 
        GROUP BY country
        ORDER BY total DESC 
        LIMIT 3 """).fetchall()

    con.close()
    return {
        "num_users": count,
        "average_age": round(avg_age, 2) if avg_age else None,
        "top_3_countries": [{"country": r[0], "count": r[1]} for r in top_countries],
    }


def filter_by_value(data, filterby, filtervalue):
    if not filterby:
        return data

    if filterby not in data.columns:
        return "Invalid Filterby Column"

    if filtervalue is None or str(filtervalue).strip() == "":
        return "Invalid Filter Value"

    # choosing column for filtering based on parameters.

    if is_string_dtype(data[filterby]):
        return data[
            data[filterby]
            .astype(str)
            .str.strip()
            .str.contains(str(filtervalue).strip(), case=False, na=False)
        ]

    return data[data[filterby].astype(str) == str(filtervalue)]


# apply limit and offset
def apply_limit_offset(data, limit, offset):
    return data.iloc[offset : offset + limit]


# apply sorting feature (bonus feature)
def apply_sort(data, sortby, order):
    if not sortby:
        return data

    if sortby not in data.columns:
        return "Invalid Sortby Column"

    order = str(order).strip().lower()

    if order not in ("asc", "desc"):
        return "Invalid order value: must use 'asc' or 'desc'"

    ascending = order == "asc"
    return data.sort_values(by=sortby, ascending=ascending)


# convert to json format or csv
def convert_to_format(data, format):
    if format == "json":
        return Response(data.to_json(orient="records"), mimetype="application/json")

    if format == "csv":
        return Response(data.to_csv(index=False), mimetype="text/csv")

    return "Invalid Format"


if __name__ == "__main__":
    app.run(debug=True)
