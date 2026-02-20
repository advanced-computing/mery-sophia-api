import pandas as pd
from flask import Flask, Response, request

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
    limit = int(request.args.get("limit", 1000))
    offset = int(request.args.get("offset", 0))

    # Load the data
    data = pd.read_csv(csv_path)

    # filter the data
    data = filter_by_value(data, filterby, filtervalue)
    if not isinstance(data, pd.DataFrame):
        return data

    # apply limit and offset
    paged = apply_limit_offset(data, limit, offset)

    # conver to requested format
    data = convert_to_format(paged, format)

    return data


# record id as a parameter
@app.get("/api/record/<record_id>/")
def get_record(record_id):
    data = pd.read_csv(csv_path)

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
    if filtervalue is None:
        return "Invalid Filter Value"
    if filterby not in data.columns:
        return "Invalid Filterby Column"

    # choosing column for filtering based on parameters.

    text_columns = [
        "Unique ID",
        "Indicator ID",
        "Name",
        "Measure",
        "Measure Info",
        "Geo Type Name",
        "Geo Join ID",
        "Geo Place Name",
        "Time Period",
        "Start_Date",
        "Data Value",
        "Message",
    ]
    if filterby in text_columns:
        return data[
            data[filterby]
            .astype(str)
            .str.contains(str(filtervalue), case=False, na=False)
        ]

    return data[data[filterby].astype(str) == str(filtervalue)]


def apply_limit_offset(data, limit, offset):
    return data.iloc[offset : offset + limit]


# convert to json format or csv
def convert_to_format(data, format):
    if format == "json":
        return Response(data.to_json(orient="records"), mimetype="application/json")

    if format == "csv":
        return Response(data.to_csv(index=False), mimetype="text/csv")

    return "Invalid Format"


if __name__ == "__main__":
    app.run(debug=True)
