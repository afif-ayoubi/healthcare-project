from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"


def test_processed_country_year_model():
    df = pd.read_csv(P / "tb_country_year.csv")
    assert not df.duplicated(["country_key", "year"]).any()
    assert int(df["year"].min()) == 2000
    assert int(df["year"].max()) == 2024
    assert (df[["e_inc_num", "e_mort_num", "c_newinc"]].dropna() >= 0).all().all()
    assert df["iso3"].notna().mean() > 0.99


def test_latest_global_metrics_are_coherent():
    agg = pd.read_csv(P / "tb_aggregates_year.csv")
    row = agg[(agg["geo_level"] == "Global") & (agg["year"] == 2024)].iloc[0]
    assert 10_000_000 < row["e_inc_num"] < 11_000_000
    assert 8_000_000 < row["c_newinc"] < 9_000_000
    assert abs(row["c_cdr"] - row["c_newinc"] / row["e_inc_num"] * 100) < 1e-8
    assert abs(row["notification_gap_num"] - (row["e_inc_num"] - row["c_newinc"])) < 1e-6


def test_age_sex_cross_section():
    age = pd.read_csv(P / "tb_age_sex_2024.csv")
    assert set(age["year"].dropna().astype(int)) == {2024}
    assert {"m", "f"}.issubset(set(age["sex"].dropna()))
    assert {"0_4", "25_34", "65plus"}.issubset(set(age["age_group"].dropna()))


def test_streamlit_app_smoke():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40)
    app.run()
    assert len(app.exception) == 0
    assert len(app.tabs) == 6
    assert len(app.metric) >= 10
