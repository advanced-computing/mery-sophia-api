# API Documentation

## Connecting to the API
Since we are running our API locally, we will access the endpoint at the address that appears on your console.

## Welcome
- Method: GET
- Path: ```/```
- Query Parameters: None

This page is just a friendly welcome to the API 

## List
- Method: GET
- Path: ```/api/list```
- Query Parameters: None

Returns records from NYC Air Quality Dataset

## Records
- Method: GET
- Path: ```/api/record/<record_id>```
- Parameters = ```record_id```
- Get data based on ```UNIQUE_ID```

## Query Parameters

### Output Format
- ```format``` default: ```json```, option: change to ```csv```


### Filtering NYC Air Quality
source: [NYC Open Data](https://data.cityofnewyork.us/Environment/Air-Quality/c3uy-2p5r/about_data)
please look at the data dictionary for more insights.
- Method: GET
- Path: ```/api/list```
- Query parameters: 
    -format: ```json``` or ```csv```
    - filterby (optional): name of the column to filter the list. Columns:
        - ```Unique%20ID```: Unique record identifier.
        - ```Indicator%20ID```: Identifier of the type of measured value across time and space.
        - ```Name``` : Name of Indicator.
        - ```Measure```: How the indicator is measured.
        - ```Measure%20Info```: Information (such as units) about the measure.
        - ```Geo%20Type%20Name```: Geography type; UHF' stands for United Hospital Fund neighborhoods; For instance, Citywide.
        - ```Geo%20Join%20ID```: Identifier of the neighborhood geographic area, used for joining to mapping geography files.
        - ```Geo%20Place%20Name```: Neighborhood name.
        - ```Time%20Period```: Description of the time that the data applies to ; Could be a year, range of years, or season.
        - ```Start%20Date```: Date value for the start of the time_period; Always a date value.
        - ```Data%20Value```: The actual data value for this indicator, measure, place, and time.       
        - ```Message```:  	notes that apply to the data value.
    - filtervalue (optional): value to filter the list by the column specified in filterby.
    - limit (optional): limit the number of results to show.
    - offset (optional): offset the results to show

### Sorting (Bonus Feature)
- ```sortby``` : Column name to sort by
- ```order```  : ```asc``` (default), ```desc```

### Pagination
- ```limit``` : Max limit of number records to return (default: ```1000```)
- ```offset```  : Number of records to skip (default : ```0``` )


## DATABASE

### GET USERS
- Method: GET
- Path: ```/users```
- Parameters = None
- View data in users table

### ADD USERS
- Method: POST
- Path: ```/users/add```
- Parameters = Name, Age, Country
- Add data in users table


### POST USERS
- Method: POST
- Path: ```/users```
- Parameters = Name, Age, Country
- Add data in users table with both JSON and HTML

### GET USER STATS
- Method: GET
- Path: ```/users/stats```
- Parameters = None
- Add data in users table with both JSON and HTML

- Example query:
```
http://127.0.0.1:5000/api/list?format=csv&filterby=Geo%20Place%20Name&filtervalue=Upper&sortby=Data%20Value&order=desc&limit=25&offset=5
```

# CPI Data Warehousing - Lab 8

## Overview

This project implements a simple data warehousing pipeline using **DuckDB** to manage continuously updated Consumer Price Index (CPI) data from the Philadelphia Federal Reserve.

The goal of this lab is to simulate how an organization ingests new data and handles **historical revisions** using three different data loading strategies:

- **Append**
- **Truncate (Full Reload)**
- **Incremental (Update + Append)**

Each method writes to its own table:
- `cpi_append`
- `cpi_trunc`
- `cpi_inc`

---

##  Data Sources

- `PCPI24M1.csv` → Initial dataset (January 2024)
- `PCPI25M2.csv` → Updated dataset (February 2025, includes revisions)

Each dataset contains:
- `DATE`: Monthly observation
- `CPI`: Price index value

Important: CPI data is revised annually, meaning past values can change.

---

## Setup Instructions

1. Install dependencies (duckdb, pandas, pytest):
```bash
pip install -r requirements.txt
```


2. Ensure the following files are in your project directory:
PCPI24M1.csv
PCPI25M2.csv

3. Run the script:
```bash
python cpi.py
```
---
##  Database Setup

A persistent DuckDB database is created:

```
cpi.db
```

The base table is initialized from the first dataset:

```sql
CREATE TABLE cpi AS SELECT * FROM read_csv('PCPI24M1.csv')
```

Each loading method then creates its own table from this base.

---

## Data Loading Methods

### 1. Append Method (cpi_append)

- <u> Description:</u>
Adds only new rows to the tableand determines new data based on the maximum existing date

- <u> Behavior:</u>
Keeps all existing data unchanged and does NOT update revised historical values

- <u> Expected Outcome:</u>
Table grows over time and historical inaccuracies persist if revisions occur

### 2. Truncate Method (cpi_trunc)

- <u> Description:</u>
Deletes all existing data and reloads the entire dataset from scratch

- <u> Behavior:</u>
Always reflects the most recent dataset and handles revisions automatically

- <u> Expected Outcome:</u>
Table exactly matches latest data, higher computational cost

### 3. Incremental Method (cpi_inc)

- <u> Description: </u>
Updates revised historical values, appends new observations

- <u> Behavior:</u>
Compares existing data with new data and identifies rows where values changed
Deletes outdated row, inserts updated valuesm and appends new rows

- <u> Expected Outcome:</u>
Efficient handling of both updates and new data

---

## Manual Testing Instructions

### Step 1: Initial Load
- Run the script using PCPI24M1.csv.
- Expected Result:
All three tables (cpi_append, cpi_trunc, cpi_inc) contain identical data

### Step 2: Load Updated Data
- Run the script again using PCPI25M2.csv.

---
## Expected Differences

| Method      | Adds New Rows | Handles Revisions | Accuracy | Speed   |
|------------|--------------|------------------|----------|---------|
| Append     | Yes          | No               | Low      | Fast    |
| Truncate   | Yes          | Yes              | High     | Slow    |
| Incremental| Yes          | Yes              | High     | Medium  |


