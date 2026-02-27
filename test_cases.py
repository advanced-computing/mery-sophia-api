import pandas as pd
import pytest

from functions import (
    check_ranges,
    check_unique_len,
    load_data,
    outlier_found,
)

# test API


def test_load_data_strips_column_names(tmp_path):
    p = tmp_path / "mini.csv"
    p.write_text(" Unique ID ,Data Value\n123456,10\n")
    df = load_data(str(p))
    assert "Unique ID" in df.columns
    assert "Data Value" in df.columns


def test_check_ranges_below_min_returns_false():
    df = pd.DataFrame({"Data Value": [-1, 0, 1]})
    assert check_ranges(df, min_allowed=0) is False


# test case for check_unique_len


def test_check_unique_len_valid():
    df = pd.DataFrame({"Unique ID": ["123456", "654321", "111111"]})
    assert check_unique_len(df) is True


def test_check_unique_len_invalid_length():
    df = pd.DataFrame({"Unique ID": ["123", "654321"]})
    assert check_unique_len(df) is False


def test_check_unique_len_missing_column():
    df = pd.DataFrame({"Other": ["123456"]})
    assert check_unique_len(df) is False


# test case for outlier_found


def test_outlier_found_normal_case():
    df = pd.DataFrame({"Data Value": [10, 12, 11, 13, 200]})

    result = outlier_found(df)

    assert isinstance(result, dict)
    assert result["outlier_count"] == 1
    assert result["total"] == 5
    assert result["outliers_rate"] == 1 / 5


def test_outlier_missing_column():
    """finding columns not exist"""
    df = pd.DataFrame({"Other": [1, 23]})
    with pytest.raises(ValueError):
        outlier_found(df, col="Data Value")


def test_outlier_nonnumeric():
    """find non numeric data"""
    df = pd.DataFrame({"Data Value": ["bad", "good", "10"]})
    with pytest.raises(ValueError):
        outlier_found(df)


# test case for check_ranges


def test_check_ranges_negative_value():
    df = pd.DataFrame({"Data Value": [1, -5, 10]})

    assert check_ranges(df) is False


def test_check_valid_range():
    """test valid ranges"""
    df = pd.DataFrame({"Data Value": [0, 1, 10]})

    assert check_ranges(df) is True


def test_check_range_missing():
    """test missing column"""
    df = pd.DataFrame({"Other": [0, 1, 10]})

    assert check_ranges(df, col="Data Value", min_allowed=0) is False


def test_check_range_below_min_fail():
    df = pd.DataFrame({"Data Value": [0, -1, 10]})

    assert check_ranges(df, col="Data Value", min_allowed=0) is False


def test_check_ranges_non_numeric_returns_false():
    df = pd.DataFrame({"Data Value": ["bad", "10"]})

    assert check_ranges(df) is False
