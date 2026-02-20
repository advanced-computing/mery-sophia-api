import pandas as pd
from flask import Flask, Response, request
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
