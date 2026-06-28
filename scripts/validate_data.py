from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
O = ROOT / "outputs"
O.mkdir(parents=True, exist_ok=True)

country = pd.read_csv(P / "tb_country_year.csv")
agg = pd.read_csv(P / "tb_aggregates_year.csv")
age = pd.read_csv(P / "tb_age_sex_2024.csv")

checks: dict[str, object] = {}
checks["unique_country_year"] = not country.duplicated(["country_key", "year"]).any()
checks["year_range_is_2000_2024"] = [int(country.year.min()), int(country.year.max())] == [2000, 2024]
checks["iso3_completeness_pct"] = round(country.iso3.notna().mean() * 100, 2)
checks["nonnegative_burden"] = bool((country[["e_inc_num", "e_mort_num", "c_newinc"]].dropna() >= 0).all().all())
checks["age_sex_year"] = sorted(age.year.dropna().astype(int).unique().tolist())
checks["age_sex_has_male_female"] = {"m", "f"}.issubset(set(age.sex.dropna()))
checks["who_regions"] = sorted(x for x in country.g_whoregion.dropna().unique() if x != "Historical / Other")
latest = agg[(agg.geo_level == "Global") & (agg.year == 2024)].iloc[0]
checks["latest_global_snapshot"] = {
    "estimated_incident_cases": round(float(latest.e_inc_num)),
    "incidence_per_100k": round(float(latest.e_inc_100k), 2),
    "notified_cases": round(float(latest.c_newinc)),
    "calculated_coverage_pct": round(float(latest.c_cdr), 2),
    "notification_difference": round(float(latest.notification_gap_num)),
    "estimated_deaths": round(float(latest.e_mort_num)),
}
checks["status"] = "PASS" if all([
    checks["unique_country_year"],
    checks["year_range_is_2000_2024"],
    checks["nonnegative_burden"],
    checks["age_sex_has_male_female"],
]) else "FAIL"
(O / "data_validation.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
print(json.dumps(checks, indent=2))
