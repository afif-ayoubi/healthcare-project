from __future__ import annotations

import numpy as np
import pandas as pd


def fmt_count(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    value = float(value)
    abs_v = abs(value)
    if abs_v >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    if abs_v >= 1_000:
        return f"{value/1_000:.0f}K"
    return f"{value:,.0f}"


def fmt_pct(value: float | int | None, decimals: int = 1) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{float(value):.{decimals}f}%"


def fmt_rate(value: float | int | None) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{float(value):,.1f}"


def pct_change(series: pd.Series, start_year: int, end_year: int) -> float:
    indexed = series.dropna()
    if start_year not in indexed.index or end_year not in indexed.index or indexed.loc[start_year] == 0:
        return np.nan
    return (indexed.loc[end_year] / indexed.loc[start_year] - 1) * 100
