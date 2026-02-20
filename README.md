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
- Example query:
```
http://127.0.0.1:5000/api/list?format=csv&filterby=Geo%20Place%20Name&filtervalue=Upper&sortby=Data%20Value&order=desc&limit=25&offset=5
```
