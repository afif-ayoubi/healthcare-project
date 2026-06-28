from __future__ import annotations

from functools import reduce
from hashlib import sha256 as _sha256
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

INDICATOR_FILES = {
    "e_inc_100k": "ddf_e_inc_100k.csv",
    "e_inc_num": "ddf_e_inc_num.csv",
    "e_mort_100k": "ddf_e_mort_100k.csv",
    "e_mort_num": "ddf_e_mort_num.csv",
    "e_mort_tbhiv_100k": "ddf_e_mort_tbhiv_100k.csv",
    "e_mort_tbhiv_num": "ddf_e_mort_tbhiv_num.csv",
    "e_pop_num": "ddf_e_pop_num.csv",
    "c_cdr_source": "ddf_c_cdr.csv",
    "c_newinc": "ddf_c_newinc.csv",
    "c_newinc_100k": "ddf_c_newinc_100k.csv",
    "cfr_source": "ddf_cfr.csv",
    "e_inc_tbhiv_100k": "ddf_e_inc_tbhiv_100k.csv",
    "e_inc_tbhiv_num": "ddf_e_inc_tbhiv_num.csv",
    "e_inc_rr_num": "ddf_e_inc_rr_num.csv",
    "e_tbhiv_prct": "ddf_e_tbhiv_prct.csv",
}

SOURCE_URLS = {
    "ddf_entities_country.csv": "https://raw.githubusercontent.com/open-numbers/ddf--who--tb_burden_estimates/refs/heads/master/ddf--entities--country.csv",
    "who_tb_burden_2025.csv": "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-11-11/who_tb_data.csv",
    "who_tb_incidence_age_sex_2024report.csv": "https://raw.githubusercontent.com/open-numbers/ddf--who--tb_burden_estimates/refs/heads/master/ddf--datapoints--e_inc_num--by--country--year--age_group--sex.csv",
}

DDF_FILENAMES = {
    "ddf_e_inc_100k.csv": "ddf--datapoints--e_inc_100k--by--country--year.csv",
    "ddf_e_inc_num.csv": "ddf--datapoints--e_inc_num--by--country--year.csv",
    "ddf_e_mort_100k.csv": "ddf--datapoints--e_mort_100k--by--country--year.csv",
    "ddf_e_mort_num.csv": "ddf--datapoints--e_mort_num--by--country--year.csv",
    "ddf_e_mort_tbhiv_100k.csv": "ddf--datapoints--e_mort_tbhiv_100k--by--country--year.csv",
    "ddf_e_mort_tbhiv_num.csv": "ddf--datapoints--e_mort_tbhiv_num--by--country--year.csv",
    "ddf_e_pop_num.csv": "ddf--datapoints--e_pop_num--by--country--year.csv",
    "ddf_c_cdr.csv": "ddf--datapoints--c_cdr--by--country--year.csv",
    "ddf_c_newinc.csv": "ddf--datapoints--c_newinc--by--country--year.csv",
    "ddf_c_newinc_100k.csv": "ddf--datapoints--c_newinc_100k--by--country--year.csv",
    "ddf_cfr.csv": "ddf--datapoints--cfr--by--country--year.csv",
    "ddf_e_inc_tbhiv_100k.csv": "ddf--datapoints--e_inc_tbhiv_100k--by--country--year.csv",
    "ddf_e_inc_tbhiv_num.csv": "ddf--datapoints--e_inc_tbhiv_num--by--country--year.csv",
    "ddf_e_inc_rr_num.csv": "ddf--datapoints--e_inc_rr_num--by--country--year.csv",
    "ddf_e_tbhiv_prct.csv": "ddf--datapoints--e_tbhiv_prct--by--country--year.csv",
}
for local_name, remote_name in DDF_FILENAMES.items():
    SOURCE_URLS[local_name] = (
        "https://raw.githubusercontent.com/open-numbers/"
        "ddf--who--tb_burden_estimates/refs/heads/master/" + remote_name
    )


def file_sha256(path: Path) -> str:
    digest = _sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_indicator(local_name: str, desired_name: str) -> pd.DataFrame:
    frame = pd.read_csv(RAW / local_name)
    value_columns = [c for c in frame.columns if c not in {"country", "year"}]
    if len(value_columns) != 1:
        raise ValueError(f"Expected one value column in {local_name}; found {value_columns}")
    frame = frame.rename(columns={value_columns[0]: desired_name})
    frame["country_key"] = frame["country"].astype(str).str.lower()
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    frame[desired_name] = pd.to_numeric(frame[desired_name], errors="coerce")
    return frame[["country_key", "year", desired_name]]


def build_country_lookup() -> pd.DataFrame:
    entities = pd.read_csv(RAW / "ddf_entities_country.csv")
    entities = entities.rename(columns={"country": "country_key", "name": "country"})
    entities["country_key"] = entities["country_key"].astype(str).str.lower()
    entities["iso3"] = entities["iso3"].astype(str).str.upper()

    # A second WHO-derived table is used only to attach WHO region labels.
    tidy = pd.read_csv(RAW / "who_tb_burden_2025.csv")
    region_lookup = (
        tidy[["iso3", "g_whoregion"]]
        .dropna()
        .drop_duplicates()
        .groupby("iso3", as_index=False)["g_whoregion"]
        .first()
    )
    region_lookup["iso3"] = region_lookup["iso3"].astype(str).str.upper()
    lookup = entities.merge(region_lookup, on="iso3", how="left")
    lookup["g_whoregion"] = lookup["g_whoregion"].fillna("Historical / Other")

    # Consistent dashboard-friendly names.
    replacements = {
        "Bolivia (Plurinational State of)": "Bolivia",
        "China, Hong Kong SAR": "Hong Kong SAR, China",
        "China, Macao SAR": "Macao SAR, China",
        "Democratic People's Republic of Korea": "North Korea",
        "Iran (Islamic Republic of)": "Iran",
        "Lao People's Democratic Republic": "Lao PDR",
        "Republic of Korea": "South Korea",
        "Republic of Moldova": "Moldova",
        "Russian Federation": "Russia",
        "Syrian Arab Republic": "Syria",
        "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
        "United Republic of Tanzania": "Tanzania",
        "Venezuela (Bolivarian Republic of)": "Venezuela",
        "Viet Nam": "Vietnam",
        "occupied Palestinian territory, including east Jerusalem": "Occupied Palestinian territory",
    }
    lookup["country"] = lookup["country"].replace(replacements)
    lookup = lookup[["country_key", "country", "iso3", "iso2", "iso_numeric", "g_whoregion"]]
    lookup.to_csv(PROCESSED / "tb_country_lookup.csv", index=False)
    return lookup


def build_country_year(lookup: pd.DataFrame) -> pd.DataFrame:
    frames = [load_indicator(filename, variable) for variable, filename in INDICATOR_FILES.items()]
    combined = reduce(lambda left, right: left.merge(right, on=["country_key", "year"], how="outer"), frames)
    combined = combined[(combined["year"] >= 2000) & (combined["year"] <= 2024)].copy()
    combined = combined.merge(lookup, on="country_key", how="left")

    # Prefer internally coherent formulas over source-rounded ratios.
    combined["c_cdr"] = np.where(
        combined["e_inc_num"].gt(0), combined["c_newinc"] / combined["e_inc_num"] * 100, np.nan
    )
    combined["coverage_gap_pct"] = 100 - combined["c_cdr"]
    combined["coverage_gap_pct_nonnegative"] = combined["coverage_gap_pct"].clip(lower=0, upper=100)
    combined["notification_gap_num"] = combined["e_inc_num"] - combined["c_newinc"]
    combined["notification_gap_num_nonnegative"] = combined["notification_gap_num"].clip(lower=0)
    combined["notification_gap_pct"] = np.where(
        combined["e_inc_num"].gt(0), combined["notification_gap_num"] / combined["e_inc_num"] * 100, np.nan
    )
    combined["case_fatality_pct"] = np.where(
        combined["e_inc_num"].gt(0), combined["e_mort_num"] / combined["e_inc_num"] * 100, np.nan
    )
    combined["hiv_incidence_share_pct"] = np.where(
        combined["e_inc_num"].gt(0), combined["e_inc_tbhiv_num"] / combined["e_inc_num"] * 100, np.nan
    )
    combined["rr_incidence_share_pct"] = np.where(
        combined["e_inc_num"].gt(0), combined["e_inc_rr_num"] / combined["e_inc_num"] * 100, np.nan
    )
    combined["mortality_excluding_hiv_num"] = combined["e_mort_num"] - combined["e_mort_tbhiv_num"]

    ordered = [
        "country_key", "country", "iso3", "iso2", "iso_numeric", "g_whoregion", "year",
        "e_pop_num", "e_inc_num", "e_inc_100k", "c_newinc", "c_newinc_100k",
        "c_cdr", "c_cdr_source", "coverage_gap_pct", "coverage_gap_pct_nonnegative",
        "notification_gap_num", "notification_gap_num_nonnegative", "notification_gap_pct",
        "e_mort_num", "e_mort_100k", "case_fatality_pct", "cfr_source",
        "e_inc_tbhiv_num", "e_inc_tbhiv_100k", "e_mort_tbhiv_num", "e_mort_tbhiv_100k",
        "e_tbhiv_prct", "hiv_incidence_share_pct", "e_inc_rr_num", "rr_incidence_share_pct",
        "mortality_excluding_hiv_num",
    ]
    combined = combined[ordered].sort_values(["country", "year"], na_position="last")
    combined.to_csv(PROCESSED / "tb_country_year.csv", index=False)
    return combined


def aggregate_group(frame: pd.DataFrame, keys: list[str], level: str) -> pd.DataFrame:
    sum_columns = [
        "e_pop_num", "e_inc_num", "c_newinc", "e_mort_num", "e_inc_tbhiv_num",
        "e_mort_tbhiv_num", "e_inc_rr_num", "mortality_excluding_hiv_num",
    ]
    out = frame.groupby(keys, dropna=False)[sum_columns].sum(min_count=1).reset_index()
    out["e_inc_100k"] = out["e_inc_num"] / out["e_pop_num"] * 100000
    out["c_newinc_100k"] = out["c_newinc"] / out["e_pop_num"] * 100000
    out["e_mort_100k"] = out["e_mort_num"] / out["e_pop_num"] * 100000
    out["e_inc_tbhiv_100k"] = out["e_inc_tbhiv_num"] / out["e_pop_num"] * 100000
    out["e_mort_tbhiv_100k"] = out["e_mort_tbhiv_num"] / out["e_pop_num"] * 100000
    out["c_cdr"] = out["c_newinc"] / out["e_inc_num"] * 100
    out["coverage_gap_pct"] = 100 - out["c_cdr"]
    out["coverage_gap_pct_nonnegative"] = out["coverage_gap_pct"].clip(lower=0, upper=100)
    out["notification_gap_num"] = out["e_inc_num"] - out["c_newinc"]
    out["notification_gap_num_nonnegative"] = out["notification_gap_num"].clip(lower=0)
    out["notification_gap_pct"] = out["notification_gap_num"] / out["e_inc_num"] * 100
    out["case_fatality_pct"] = out["e_mort_num"] / out["e_inc_num"] * 100
    out["hiv_incidence_share_pct"] = out["e_inc_tbhiv_num"] / out["e_inc_num"] * 100
    out["rr_incidence_share_pct"] = out["e_inc_rr_num"] / out["e_inc_num"] * 100
    out["geo_level"] = level
    return out


def build_aggregates(country_year: pd.DataFrame) -> pd.DataFrame:
    base = country_year[(country_year["country"].notna()) & (country_year["g_whoregion"] != "Historical / Other")].copy()
    regions = aggregate_group(base, ["g_whoregion", "year"], "WHO region").rename(columns={"g_whoregion": "geography"})
    world = aggregate_group(base, ["year"], "Global")
    world["geography"] = "Global"
    cols = [
        "geo_level", "geography", "year", "e_pop_num", "e_inc_num", "e_inc_100k",
        "c_newinc", "c_newinc_100k", "c_cdr", "coverage_gap_pct",
        "coverage_gap_pct_nonnegative", "notification_gap_num",
        "notification_gap_num_nonnegative", "notification_gap_pct", "e_mort_num",
        "e_mort_100k", "case_fatality_pct", "e_inc_tbhiv_num", "e_inc_tbhiv_100k",
        "e_mort_tbhiv_num", "e_mort_tbhiv_100k", "hiv_incidence_share_pct",
        "e_inc_rr_num", "rr_incidence_share_pct", "mortality_excluding_hiv_num",
    ]
    result = pd.concat([world[cols], regions[cols]], ignore_index=True).sort_values(["geo_level", "geography", "year"])
    result.to_csv(PROCESSED / "tb_aggregates_year.csv", index=False)
    return result


def build_age_sex(lookup: pd.DataFrame) -> pd.DataFrame:
    age = pd.read_csv(RAW / "who_tb_incidence_age_sex_2024report.csv")
    age["country_key"] = age["country"].astype(str).str.lower()
    age = age.drop(columns=["country"]).merge(lookup, on="country_key", how="left")
    age_labels = {
        "0_4": "0-4", "5_9": "5-9", "10_14": "10-14", "15_19": "15-19",
        "20_24": "20-24", "25_34": "25-34", "35_44": "35-44", "45_54": "45-54",
        "55_64": "55-64", "65plus": "65+", "0_14": "0-14", "15_24": "15-24",
        "15plus": "15+", "5_14": "5-14", "all": "All ages",
    }
    sex_labels = {"a": "All sexes", "f": "Female", "m": "Male"}
    age["age_group_label"] = age["age_group"].map(age_labels).fillna(age["age_group"])
    age["sex_label"] = age["sex"].map(sex_labels).fillna(age["sex"])
    age["e_inc_num"] = pd.to_numeric(age["e_inc_num"], errors="coerce")
    age = age[[
        "country_key", "country", "iso3", "g_whoregion", "year", "age_group",
        "age_group_label", "sex", "sex_label", "e_inc_num",
    ]].sort_values(["country", "age_group", "sex"])
    age.to_csv(PROCESSED / "tb_age_sex_2024.csv", index=False)
    return age


def build_dictionary() -> pd.DataFrame:
    rows = [
        ("e_inc_num", "Estimated incident TB cases", "count", "WHO-derived estimate of people who developed TB during the year."),
        ("e_inc_100k", "TB incidence rate", "cases per 100,000", "Estimated incident TB cases per 100,000 population."),
        ("c_newinc", "Notified new and relapse cases", "count", "New and relapse TB cases officially notified to national programmes."),
        ("c_newinc_100k", "Case notification rate", "cases per 100,000", "Notified new and relapse cases per 100,000 population."),
        ("c_cdr", "Case detection / diagnosis and treatment coverage", "%", "Notified new and relapse cases divided by estimated incident cases."),
        ("coverage_gap_pct", "Coverage gap", "percentage points", "100 minus calculated diagnosis and treatment coverage."),
        ("notification_gap_num", "Estimated notification difference", "count", "Estimated incident cases minus notified cases; it is not proof that every person in the difference was untreated."),
        ("e_mort_num", "Estimated TB deaths", "count", "Estimated deaths from TB, including HIV-associated TB deaths where included in the source measure."),
        ("e_mort_100k", "TB mortality rate", "deaths per 100,000", "Estimated TB deaths per 100,000 population."),
        ("case_fatality_pct", "Case fatality ratio", "%", "Estimated TB deaths divided by estimated incident TB cases."),
        ("e_inc_tbhiv_num", "HIV-associated incident TB", "count", "Estimated incident TB cases among people living with HIV."),
        ("e_mort_tbhiv_num", "TB deaths among people with HIV", "count", "Estimated TB deaths among people living with HIV."),
        ("hiv_incidence_share_pct", "HIV-associated share of incident TB", "%", "Estimated HIV-associated incident TB divided by all incident TB."),
        ("e_inc_rr_num", "Estimated RR/MDR-TB incidence", "count", "Estimated incident rifampicin-resistant or multidrug-resistant TB cases."),
        ("rr_incidence_share_pct", "RR/MDR-TB share of incident TB", "%", "Estimated RR/MDR-TB incidence divided by all incident TB."),
        ("e_pop_num", "Population", "people", "Population denominator used for rate calculation."),
        ("age_group", "Age group", "category", "Age category used in the 2024 age-sex incidence estimate."),
        ("sex", "Sex", "category", "All sexes, female or male in the source age-sex estimate."),
    ]
    dictionary = pd.DataFrame(rows, columns=["variable", "label", "unit", "definition"])
    dictionary.to_csv(PROCESSED / "data_dictionary.csv", index=False)
    return dictionary


def build_manifest() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(RAW.glob("*.csv")):
        try:
            frame = pd.read_csv(path)
        except Exception:
            continue
        years = pd.to_numeric(frame.get("year", pd.Series(dtype=float)), errors="coerce")
        rows.append({
            "file": path.name,
            "source": "WHO Global Tuberculosis Programme data via WHO GitHub, TidyTuesday, or Open Numbers DDF mirror",
            "source_url": SOURCE_URLS.get(path.name, "See README source table"),
            "retrieved_on": "2026-06-23",
            "rows": len(frame),
            "columns": len(frame.columns),
            "year_min": int(years.min()) if len(years) and years.notna().any() else None,
            "year_max": int(years.max()) if len(years) and years.notna().any() else None,
            "sha256": file_sha256(path),
        })
    manifest = pd.DataFrame(rows)
    manifest.to_csv(PROCESSED / "data_manifest.csv", index=False)
    return manifest


def main() -> None:
    lookup = build_country_lookup()
    country_year = build_country_year(lookup)
    aggregates = build_aggregates(country_year)
    age = build_age_sex(lookup)
    build_dictionary()
    build_manifest()
    summary = {
        "country_year_rows": len(country_year),
        "countries_or_territories": int(country_year["iso3"].nunique()),
        "year_min": int(country_year["year"].min()),
        "year_max": int(country_year["year"].max()),
        "age_sex_rows": len(age),
        "aggregate_rows": len(aggregates),
        "data_note": "Country-level WHO-derived mirror; aggregate values may differ slightly from rounded figures in the published WHO 2025 report.",
    }
    (PROCESSED / "build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
