import pandas as pd
import pytest

from functions import (
    check_ranges,
    check_unique_len,
    outlier_found,
)

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
    assert result["outlier_count"] == 1.0
    assert result["total"] == 5
    assert result["outliers_rate"] == 1.0 / 5


# test case for check_ranges


def test_check_ranges_negative_value():
    df = pd.DataFrame({"Data Value": [1, -5, 10]})

    assert check_ranges(df) is False
