# Data Findings

## Missing Values
- All columns except ```Messages``` has no missing value
- This indicates that there are no necessary imputation and row removal 

## Unique ID Consistency
- This column contains fully unique values
- All we need to check is whether the length of the ```Unique ID``` values are similar.
- Trough the unit function, we found that all the values have the same length (6)

## ```Data Values``` Column
- Contains only numeric value
- Contains no negative number
- Need to check the range of values within this column, but we only set the minimum value to avoid negative value in the future.

## Outliers in ```Data Value``` Distribution
- the dataset is clean, but the distribution of ```Data Value``` shows high upper outlier
- the data may be sensitive to extreme values
- the median may provide more stable summaries

## No Duplicate Rows
No fully duplicate rows were found in the dataset, indicating:
- No redundant records
- Aggregation and counts will not be inflated

