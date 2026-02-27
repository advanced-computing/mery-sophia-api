# data cleaning functions
from __future__ import annotations

import pandas as pd


# load data
def load_data(csv_path: str = "Air_Quality.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    return df


# 1. check unique_id whether it is within certain length
def check_unique_len(
    df: pd.DataFrame,
    id_col: str = "Unique ID",
    expected_length: int = 6,
) -> bool:
    if id_col not in df.columns:
        return False

    length = df[id_col].astype(str).str.len()

    return bool((length == expected_length).all())


# 2. find outlier
def outlier_found(
    df: pd.DataFrame,
    col: str = "Data Value",
    r: float = 1.5,
) -> dict:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

    s = pd.to_numeric(df[col], errors="coerce")
    if s.isna().any():
        raise ValueError(f"{col} contains non numeric values")

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - r * iqr
    upper = q3 + r * iqr

    outliers = (s < lower) | (s > upper)
    outliers_count = int(outliers.sum())
    total = int(len(s))
    outliers_rate = outliers_count / total if total else 0.0

    return {
        "col": col,
        "k": float(r),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower": float(lower),
        "upper": float(upper),
        "outlier_count": outliers_count,
        "total": total,
        "outliers_rate": float(outliers_rate),
    }


# 3. check valid ranges (only set the minimum because we cant set the maximum for air quality values, only minimun = 0)
def check_ranges(
    df: pd.DataFrame,
    col: str = "Data Value",
    min_allowed: float = 0,
) -> bool:

    if col not in df.columns:
        return False

    s = pd.to_numeric(df[col], errors="coerce")
    # check whether it is fully numerical
    if not s.notna().all():
        return False

    # set the range check (include 0 as minimum )
    if not (s >= min_allowed).all():
        return False

    return True
