from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"

NAVY = "#0B1F33"
TEAL = "#0E7490"
MINT = "#14B8A6"
CORAL = "#E76F51"
GOLD = "#F4A261"
SLATE = "#64748B"
PALE = "#F4F8FB"
WHITE = "#FFFFFF"

st.set_page_config(
    page_title="Global TB Burden & Treatment Gaps",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    :root {{ --navy:{NAVY}; --teal:{TEAL}; --mint:{MINT}; --coral:{CORAL}; --pale:{PALE}; }}
    .stApp {{ background: linear-gradient(180deg, #F7FAFC 0%, #FFFFFF 28%); color: {NAVY}; }}
    .block-container {{ padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1500px; }}
    [data-testid="stSidebar"] {{ background: #F0F6F8; border-right: 1px solid #D8E5EA; }}
    h1, h2, h3 {{ color: {NAVY}; letter-spacing: -0.02em; }}
    h1 {{ font-weight: 800; }}
    .hero {{
        background: linear-gradient(120deg, {NAVY} 0%, #123A52 68%, {TEAL} 100%);
        border-radius: 20px; padding: 1.5rem 1.7rem; color: white; margin-bottom: 1rem;
        box-shadow: 0 12px 30px rgba(11,31,51,.15);
    }}
    .hero h1 {{ color: white; margin: 0 0 .35rem 0; font-size: 2.15rem; }}
    .hero p {{ margin: 0; color: #DCEFF4; font-size: 1.02rem; max-width: 1000px; }}
    .eyebrow {{ font-weight: 700; text-transform: uppercase; letter-spacing: .12em; font-size: .73rem; color: #9EE7E5; }}
    .section-note {{ background: #EAF5F7; border-left: 4px solid {TEAL}; padding: .75rem 1rem; border-radius: 8px; color:{NAVY}; }}
    .warning-note {{ background: #FFF6ED; border-left: 4px solid {CORAL}; padding: .75rem 1rem; border-radius: 8px; color:{NAVY}; }}
    .insight {{ background: white; border: 1px solid #DDE7EC; border-radius: 14px; padding: 1rem; height: 100%; box-shadow: 0 4px 16px rgba(11,31,51,.04); }}
    .insight b {{ color:{TEAL}; }}
    [data-testid="stMetric"] {{ background:white; border:1px solid #DDE7EC; border-radius:14px; padding:.8rem 1rem; box-shadow:0 4px 14px rgba(11,31,51,.04); }}
    [data-testid="stMetricLabel"] {{ color:{SLATE}; font-weight:700; }}
    [data-testid="stMetricValue"] {{ color:{NAVY}; font-weight:800; }}
    .smallprint {{ font-size:.82rem; color:{SLATE}; line-height:1.45; }}
    .footer {{ border-top:1px solid #DDE7EC; padding-top:1rem; color:{SLATE}; font-size:.8rem; }}
    div[data-baseweb="tab-list"] {{ gap:.35rem; }}
    button[data-baseweb="tab"] {{ background:white; border:1px solid #DDE7EC; border-radius:10px; padding:.45rem .75rem; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ background:#DDF2F2; color:{NAVY}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def password_gate() -> None:
    """Optional password screen. It is disabled when APP_PASSWORD is not configured."""
    expected = os.getenv("APP_PASSWORD", "")
    if not expected:
        try:
            expected = str(st.secrets.get("APP_PASSWORD", ""))
        except Exception:
            expected = ""
    if not expected:
        return
    if st.session_state.get("authenticated"):
        return
    st.markdown(
        '<div class="hero"><div class="eyebrow">Protected analytics tool</div>'
        '<h1>Global Tuberculosis Dashboard</h1><p>Enter the project password to continue.</p></div>',
        unsafe_allow_html=True,
    )
    entered = st.text_input("Password", type="password")
    if st.button("Open dashboard", type="primary"):
        if entered == expected:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


password_gate()


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    country = pd.read_csv(DATA / "tb_country_year.csv")
    aggregates = pd.read_csv(DATA / "tb_aggregates_year.csv")
    age_sex = pd.read_csv(DATA / "tb_age_sex_2024.csv")
    dictionary = pd.read_csv(DATA / "data_dictionary.csv")
    for frame in (country, aggregates, age_sex):
        frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    return country, aggregates, age_sex, dictionary


country, aggregates, age_sex, data_dictionary = load_data()
LATEST_YEAR = int(country["year"].max())
MIN_YEAR = int(country["year"].min())


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


def style_figure(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color=NAVY, size=13),
        title_font=dict(size=18, color=NAVY),
        legend_title_text="",
        hoverlabel=dict(bgcolor=WHITE, font_color=NAVY),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D8E5EA")
    fig.update_yaxes(gridcolor="#E6EEF2", zeroline=False)
    return fig


def geography_series(mode: str, selection: str) -> pd.DataFrame:
    if mode == "Global":
        out = aggregates[(aggregates["geo_level"] == "Global") & (aggregates["geography"] == "Global")]
    elif mode == "WHO region":
        out = aggregates[(aggregates["geo_level"] == "WHO region") & (aggregates["geography"] == selection)]
    else:
        out = country[country["country"] == selection]
    return out.sort_values("year").copy()


def filter_map_scope(frame: pd.DataFrame, mode: str, selection: str) -> pd.DataFrame:
    if mode == "WHO region":
        return frame[frame["g_whoregion"] == selection].copy()
    if mode == "Country":
        return frame[frame["country"] == selection].copy()
    return frame.copy()


def selected_age_data(mode: str, selection: str) -> pd.DataFrame:
    base = age_sex.copy()
    if mode == "WHO region":
        base = base[base["g_whoregion"] == selection]
    elif mode == "Country":
        base = base[base["country"] == selection]
    return base


with st.sidebar:
    st.markdown("### Dashboard controls")
    mode = st.radio("Geographic level", ["Global", "WHO region", "Country"], horizontal=False)
    if mode == "WHO region":
        options = sorted(x for x in country["g_whoregion"].dropna().unique() if x != "Historical / Other")
        selection = st.selectbox("WHO region", options, index=options.index("South-East Asia") if "South-East Asia" in options else 0)
    elif mode == "Country":
        options = sorted(country["country"].dropna().unique())
        selection = st.selectbox("Country", options, index=options.index("Lebanon") if "Lebanon" in options else 0)
    else:
        selection = "Global"

    trend_range = st.slider("Trend years", MIN_YEAR, LATEST_YEAR, (2000, LATEST_YEAR))
    map_year = st.slider("Map / ranking year", MIN_YEAR, LATEST_YEAR, LATEST_YEAR)
    st.markdown("---")
    st.markdown(
        "**Snapshot:** WHO-derived annual estimates and notifications, 2000–2024. "
        "Age-sex estimates are available for 2024 in this project package."
    )
    st.caption("Use the download controls on the final tab to inspect the exact data behind each view.")

series = geography_series(mode, selection)
series_window = series[series["year"].between(trend_range[0], trend_range[1])].copy()
latest_rows = series[series["year"] <= map_year]
latest = latest_rows.iloc[-1] if not latest_rows.empty else series.iloc[-1]
latest_label = f"{selection}, {int(latest['year'])}"

st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">MSBA382 · Healthcare Analytics</div>
      <h1>Global Tuberculosis Burden & Treatment Gaps</h1>
      <p>Explore where TB burden is concentrated, how incidence and mortality have changed, who is most affected, and where diagnosis-and-treatment coverage remains incomplete.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"Current analytical scope: **{selection}** · trend window **{trend_range[0]}–{trend_range[1]}** · map/ranking year **{map_year}**"
)

tabs = st.tabs([
    "Executive overview",
    "Global map",
    "Trends & comparisons",
    "Age & sex",
    "TB–HIV & drug resistance",
    "Forecast & data",
])

with tabs[0]:
    st.subheader(f"Executive snapshot — {latest_label}")
    cols = st.columns(5)
    cols[0].metric("Estimated incident cases", fmt_count(latest.get("e_inc_num")))
    cols[1].metric("Incidence per 100,000", fmt_rate(latest.get("e_inc_100k")))
    cols[2].metric("Estimated TB deaths", fmt_count(latest.get("e_mort_num")))
    cols[3].metric("Diagnosis & treatment coverage", fmt_pct(latest.get("c_cdr")))
    cols[4].metric("Estimated notification difference", fmt_count(latest.get("notification_gap_num_nonnegative")))

    st.markdown(
        '<div class="warning-note"><b>Interpretation:</b> the notification difference equals estimated incident cases minus notified new and relapse cases. '
        'It is a surveillance and service-coverage signal, not proof that every person in the difference was untreated. WHO burden values are estimates and carry uncertainty.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    left, right = st.columns([1.15, 1])
    with left:
        burden = series_window[["year", "e_inc_num", "c_newinc"]].melt(
            "year", var_name="measure", value_name="people"
        )
        burden["measure"] = burden["measure"].map({
            "e_inc_num": "Estimated incident TB",
            "c_newinc": "Notified new & relapse",
        })
        fig = px.line(
            burden,
            x="year",
            y="people",
            color="measure",
            markers=True,
            color_discrete_map={"Estimated incident TB": CORAL, "Notified new & relapse": TEAL},
            title="Estimated burden versus notified cases",
        )
        fig.update_yaxes(tickformat="~s", title="People")
        fig.update_xaxes(title="")
        st.plotly_chart(style_figure(fig), use_container_width=True)
    with right:
        rates = series_window[["year", "e_inc_100k", "e_mort_100k"]].melt(
            "year", var_name="measure", value_name="rate"
        )
        rates["measure"] = rates["measure"].map({
            "e_inc_100k": "Incidence rate",
            "e_mort_100k": "Mortality rate",
        })
        fig = px.line(
            rates,
            x="year",
            y="rate",
            color="measure",
            markers=True,
            color_discrete_map={"Incidence rate": NAVY, "Mortality rate": GOLD},
            title="TB incidence and mortality rates",
        )
        fig.update_yaxes(title="Per 100,000")
        fig.update_xaxes(title="")
        st.plotly_chart(style_figure(fig), use_container_width=True)

    start, end = trend_range
    indexed = series.set_index("year")
    incidence_change = pct_change(indexed["e_inc_100k"], start, end)
    mortality_change = pct_change(indexed["e_mort_100k"], start, end)
    coverage_change = pct_change(indexed["c_cdr"], start, end)
    notif_change = pct_change(indexed["c_newinc"], start, end)

    st.markdown("### Decision-oriented interpretation")
    insight_cols = st.columns(3)
    insight_cols[0].markdown(
        f'<div class="insight"><b>Burden direction</b><br>Incidence changed by <strong>{fmt_pct(incidence_change)}</strong> and mortality by '
        f'<strong>{fmt_pct(mortality_change)}</strong> between {start} and {end}. Negative values indicate improvement.</div>',
        unsafe_allow_html=True,
    )
    insight_cols[1].markdown(
        f'<div class="insight"><b>Service reach</b><br>Notifications changed by <strong>{fmt_pct(notif_change)}</strong>, while calculated coverage changed by '
        f'<strong>{fmt_pct(coverage_change)}</strong>. Interpret this alongside estimated burden, not in isolation.</div>',
        unsafe_allow_html=True,
    )
    pandemic_note = "The 2020 notification fall is visible in the global series and is consistent with pandemic-related service disruption." if mode == "Global" else "Use the time series to check whether 2020 interrupted detection and reporting in this geography."
    insight_cols[2].markdown(
        f'<div class="insight"><b>System resilience</b><br>{pandemic_note}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Countries contributing most to the 2024 analytical snapshot")
    snapshot = country[country["year"] == map_year].dropna(subset=["country", "e_inc_num"]).copy()
    top = snapshot.nlargest(12, "e_inc_num")[
        ["country", "g_whoregion", "e_inc_num", "e_inc_100k", "c_newinc", "c_cdr", "notification_gap_num_nonnegative"]
    ].rename(columns={
        "country": "Country", "g_whoregion": "WHO region", "e_inc_num": "Estimated cases",
        "e_inc_100k": "Incidence /100k", "c_newinc": "Notified cases", "c_cdr": "Coverage %",
        "notification_gap_num_nonnegative": "Notification difference",
    })
    st.dataframe(
        top.style.format({
            "Estimated cases": "{:,.0f}", "Incidence /100k": "{:,.1f}", "Notified cases": "{:,.0f}",
            "Coverage %": "{:,.1f}", "Notification difference": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

with tabs[1]:
    st.subheader(f"Geographic pattern — {map_year}")
    metric_options = {
        "TB incidence rate per 100,000": ("e_inc_100k", "Incidence /100k", "YlOrRd"),
        "Estimated incident TB cases": ("e_inc_num", "Estimated cases", "YlOrRd"),
        "TB mortality rate per 100,000": ("e_mort_100k", "Mortality /100k", "OrRd"),
        "Diagnosis & treatment coverage (%)": ("c_cdr", "Coverage %", "Teal"),
        "Estimated notification difference": ("notification_gap_num_nonnegative", "Notification difference", "Reds"),
        "HIV-associated share of incident TB (%)": ("hiv_incidence_share_pct", "HIV-associated share %", "Purples"),
        "Estimated RR/MDR-TB incidence": ("e_inc_rr_num", "RR/MDR-TB cases", "Magenta"),
    }
    map_label = st.selectbox("Map indicator", list(metric_options), index=0)
    metric, display_label, scale = metric_options[map_label]
    map_data = country[country["year"] == map_year].dropna(subset=["iso3", metric]).copy()
    scoped = filter_map_scope(map_data, mode, selection)

    fig = px.choropleth(
        map_data,
        locations="iso3",
        color=metric,
        hover_name="country",
        hover_data={
            "iso3": False,
            "g_whoregion": True,
            "e_inc_num": ":,.0f",
            "e_inc_100k": ":.1f",
            "c_cdr": ":.1f",
            "notification_gap_num_nonnegative": ":,.0f",
        },
        color_continuous_scale=scale,
        title=map_label,
        labels={metric: display_label, "g_whoregion": "WHO region"},
    )
    fig.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#C9D6DC", projection_type="natural earth")
    fig.update_layout(coloraxis_colorbar=dict(title=display_label))
    st.plotly_chart(style_figure(fig, 550), use_container_width=True)

    if mode != "Global":
        st.caption(f"The map remains global for context; the ranking below is filtered to **{selection}**.")
    rank = scoped.nlargest(15, metric)[["country", "g_whoregion", metric, "e_inc_num", "c_cdr"]].copy()
    rank = rank.rename(columns={"country": "Country", "g_whoregion": "WHO region", metric: display_label, "e_inc_num": "Estimated TB cases", "c_cdr": "Coverage %"})
    left, right = st.columns([1.2, 1])
    with left:
        bar = rank.sort_values(display_label)
        fig = px.bar(
            bar,
            x=display_label,
            y="Country",
            orientation="h",
            color=display_label,
            color_continuous_scale=scale,
            title=f"Top countries by {display_label.lower()}",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)
    with right:
        st.dataframe(
            rank.style.format({display_label: "{:,.1f}", "Estimated TB cases": "{:,.0f}", "Coverage %": "{:,.1f}"}),
            use_container_width=True,
            hide_index=True,
            height=500,
        )

with tabs[2]:
    st.subheader("Country and regional comparisons")
    metric_labels = {
        "Incidence rate per 100,000": "e_inc_100k",
        "Mortality rate per 100,000": "e_mort_100k",
        "Estimated incident cases": "e_inc_num",
        "Notified new & relapse cases": "c_newinc",
        "Diagnosis & treatment coverage (%)": "c_cdr",
        "Estimated notification difference": "notification_gap_num_nonnegative",
        "HIV-associated incident TB": "e_inc_tbhiv_num",
        "Estimated RR/MDR-TB incidence": "e_inc_rr_num",
    }
    trend_label = st.selectbox("Trend indicator", list(metric_labels), index=0)
    trend_metric = metric_labels[trend_label]
    all_countries = sorted(country["country"].dropna().unique())
    if mode == "Country":
        default_countries = [selection]
    else:
        default_countries = [x for x in ["India", "Indonesia", "Philippines", "China", "Pakistan"] if x in all_countries]
    compare = st.multiselect("Countries to compare (up to 8)", all_countries, default=default_countries, max_selections=8)
    if not compare:
        st.info("Select at least one country.")
    else:
        comp = country[country["country"].isin(compare) & country["year"].between(*trend_range)].copy()
        fig = px.line(
            comp,
            x="year",
            y=trend_metric,
            color="country",
            markers=True,
            title=trend_label,
            labels={trend_metric: trend_label, "year": "Year", "country": "Country"},
        )
        if trend_metric.endswith("num") or trend_metric in {"c_newinc", "notification_gap_num_nonnegative"}:
            fig.update_yaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)

        summary_rows = []
        for name, grp in comp.groupby("country"):
            s = grp.set_index("year")[trend_metric].dropna()
            start_available = int(s.index.min()) if not s.empty else None
            end_available = int(s.index.max()) if not s.empty else None
            change = (s.iloc[-1] / s.iloc[0] - 1) * 100 if len(s) >= 2 and s.iloc[0] != 0 else np.nan
            summary_rows.append({
                "Country": name,
                "First year": start_available,
                "Latest year": end_available,
                "First value": s.iloc[0] if not s.empty else np.nan,
                "Latest value": s.iloc[-1] if not s.empty else np.nan,
                "Change %": change,
            })
        change_df = pd.DataFrame(summary_rows).sort_values("Latest value", ascending=False)
        st.dataframe(
            change_df.style.format({"First value": "{:,.1f}", "Latest value": "{:,.1f}", "Change %": "{:+,.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### WHO region comparison")
    region_snapshot = aggregates[(aggregates["geo_level"] == "WHO region") & (aggregates["year"] == map_year)].copy()
    region_snapshot = region_snapshot.sort_values("e_inc_num", ascending=False)
    fig = px.scatter(
        region_snapshot,
        x="e_inc_100k",
        y="c_cdr",
        size="e_inc_num",
        color="geography",
        text="geography",
        hover_data={"e_inc_num": ":,.0f", "notification_gap_num_nonnegative": ":,.0f"},
        title="Burden and service coverage by WHO region",
        labels={"e_inc_100k": "Incidence per 100,000", "c_cdr": "Coverage (%)", "geography": "WHO region", "e_inc_num": "Estimated cases"},
        size_max=70,
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(style_figure(fig, 500), use_container_width=True)

with tabs[3]:
    st.subheader("Estimated TB incidence by age and sex — 2024")
    st.markdown(
        '<div class="section-note"><b>Scope note:</b> age-sex estimates in this project are a 2024 cross-section. '
        'The chart uses non-overlapping age bands to avoid double-counting.</div>',
        unsafe_allow_html=True,
    )
    non_overlapping = ["0_4", "5_9", "10_14", "15_19", "20_24", "25_34", "35_44", "45_54", "55_64", "65plus"]
    age_scope = selected_age_data(mode, selection)
    age_scope = age_scope[age_scope["age_group"].isin(non_overlapping) & age_scope["sex"].isin(["m", "f"])].copy()
    if age_scope.empty:
        st.warning("No age-sex estimate is available for the selected geography.")
    else:
        age_order = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        age_summary = age_scope.groupby(["age_group_label", "sex_label"], as_index=False)["e_inc_num"].sum(min_count=1)
        age_summary["age_group_label"] = pd.Categorical(age_summary["age_group_label"], categories=age_order, ordered=True)
        age_summary = age_summary.sort_values("age_group_label")
        fig = px.bar(
            age_summary,
            x="age_group_label",
            y="e_inc_num",
            color="sex_label",
            barmode="group",
            color_discrete_map={"Male": TEAL, "Female": CORAL},
            title=f"Age-sex distribution of estimated incident TB — {selection}",
            labels={"age_group_label": "Age group", "e_inc_num": "Estimated incident cases", "sex_label": "Sex"},
        )
        fig.update_yaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)

        totals = age_scope.groupby("sex_label")["e_inc_num"].sum(min_count=1)
        male = float(totals.get("Male", np.nan))
        female = float(totals.get("Female", np.nan))
        ratio = male / female if female and not np.isnan(female) else np.nan
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Male estimated cases", fmt_count(male))
        c2.metric("Female estimated cases", fmt_count(female))
        c3.metric("Male : female ratio", "N/A" if np.isnan(ratio) else f"{ratio:.2f}")
        child = age_scope[age_scope["age_group"].isin(["0_4", "5_9", "10_14"])]["e_inc_num"].sum(min_count=1)
        c4.metric("Estimated cases age 0–14", fmt_count(child))

        pivot = age_summary.pivot(index="age_group_label", columns="sex_label", values="e_inc_num").reset_index()
        st.dataframe(pivot.style.format({"Female": "{:,.0f}", "Male": "{:,.0f}"}), use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("TB–HIV co-epidemic and rifampicin/multidrug resistance")
    hiv_cols = st.columns(4)
    hiv_cols[0].metric("HIV-associated incident TB", fmt_count(latest.get("e_inc_tbhiv_num")))
    hiv_cols[1].metric("HIV-associated share", fmt_pct(latest.get("hiv_incidence_share_pct")))
    hiv_cols[2].metric("TB deaths among people with HIV", fmt_count(latest.get("e_mort_tbhiv_num")))
    hiv_cols[3].metric("Estimated RR/MDR-TB incidence", fmt_count(latest.get("e_inc_rr_num")))

    current = country[country["year"] == map_year].copy()
    left, right = st.columns(2)
    with left:
        top_hiv = current.dropna(subset=["e_inc_tbhiv_num"]).nlargest(12, "e_inc_tbhiv_num").sort_values("e_inc_tbhiv_num")
        fig = px.bar(
            top_hiv,
            x="e_inc_tbhiv_num",
            y="country",
            orientation="h",
            color="hiv_incidence_share_pct",
            color_continuous_scale="Purples",
            title="Countries with the largest HIV-associated TB burden",
            labels={"e_inc_tbhiv_num": "Estimated cases", "country": "", "hiv_incidence_share_pct": "Share %"},
        )
        fig.update_xaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)
    with right:
        top_rr = current.dropna(subset=["e_inc_rr_num"]).nlargest(12, "e_inc_rr_num").sort_values("e_inc_rr_num")
        fig = px.bar(
            top_rr,
            x="e_inc_rr_num",
            y="country",
            orientation="h",
            color="rr_incidence_share_pct",
            color_continuous_scale="Magenta",
            title="Countries with the largest estimated RR/MDR-TB burden",
            labels={"e_inc_rr_num": "Estimated cases", "country": "", "rr_incidence_share_pct": "Share %"},
        )
        fig.update_xaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)

    st.markdown(
        '<div class="warning-note"><b>Clinical distinction:</b> HIV increases the risk that latent TB infection progresses to active disease because it weakens immunity. '
        'RR/MDR-TB is different: it refers to resistance to key anti-TB medicines and creates a more difficult treatment pathway.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    scatter_data = current.dropna(subset=["e_inc_100k", "hiv_incidence_share_pct", "e_inc_num"]).copy()
    fig = px.scatter(
        scatter_data,
        x="e_inc_100k",
        y="hiv_incidence_share_pct",
        size="e_inc_num",
        color="g_whoregion",
        hover_name="country",
        size_max=55,
        log_x=True,
        title="Incidence intensity and HIV-associated share",
        labels={"e_inc_100k": "TB incidence per 100,000 (log scale)", "hiv_incidence_share_pct": "HIV-associated share (%)", "g_whoregion": "WHO region"},
    )
    st.plotly_chart(style_figure(fig, 500), use_container_width=True)

with tabs[5]:
    st.subheader("Exploratory projection and data access")
    st.markdown(
        '<div class="section-note"><b>Forecasting guardrail:</b> this is a descriptive time-series extrapolation, not a causal or clinical prediction. '
        'Policy shifts, outbreaks, conflict, diagnostics and reporting changes can invalidate the projection.</div>',
        unsafe_allow_html=True,
    )
    forecast_country = st.selectbox(
        "Country for exploratory incidence-rate projection",
        sorted(country["country"].dropna().unique()),
        index=sorted(country["country"].dropna().unique()).index(selection) if mode == "Country" and selection in set(country["country"]) else 0,
    )
    history_years = st.slider("Training window (most recent years)", 8, 20, 12)
    fc = country[(country["country"] == forecast_country) & country["e_inc_100k"].notna()].sort_values("year")[["year", "e_inc_100k"]].copy()
    if len(fc) < 8:
        st.warning("Too few observations for this exploratory projection.")
    else:
        fc = fc.tail(history_years)
        holdout_n = min(5, max(2, len(fc) // 4))
        train = fc.iloc[:-holdout_n]
        test = fc.iloc[-holdout_n:]
        x_train = train["year"].to_numpy(float)
        y_train = train["e_inc_100k"].to_numpy(float)
        slope, intercept = np.polyfit(x_train, y_train, 1)
        test_pred = slope * test["year"].to_numpy(float) + intercept
        mae = float(np.mean(np.abs(test["e_inc_100k"].to_numpy(float) - test_pred)))
        naive_mae = float(np.mean(np.abs(test["e_inc_100k"].to_numpy(float) - train["e_inc_100k"].iloc[-1])))

        full_slope, full_intercept = np.polyfit(fc["year"].to_numpy(float), fc["e_inc_100k"].to_numpy(float), 1)
        future_years = np.arange(int(fc["year"].max()) + 1, int(fc["year"].max()) + 4)
        future_pred = np.maximum(full_slope * future_years + full_intercept, 0)
        residual_sd = float(np.std(fc["e_inc_100k"] - (full_slope * fc["year"] + full_intercept), ddof=2)) if len(fc) > 2 else 0
        forecast_df = pd.DataFrame({
            "year": future_years,
            "estimate": future_pred,
            "lower": np.maximum(future_pred - 1.96 * residual_sd, 0),
            "upper": future_pred + 1.96 * residual_sd,
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fc["year"], y=fc["e_inc_100k"], mode="lines+markers", name="Observed", line=dict(color=TEAL, width=3)))
        fig.add_trace(go.Scatter(x=forecast_df["year"], y=forecast_df["upper"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=forecast_df["year"], y=forecast_df["lower"], mode="lines", fill="tonexty", fillcolor="rgba(231,111,81,.18)", line=dict(width=0), name="Approx. 95% band", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=forecast_df["year"], y=forecast_df["estimate"], mode="lines+markers", name="Linear projection", line=dict(color=CORAL, width=3, dash="dash")))
        fig.update_layout(title=f"Exploratory incidence-rate projection — {forecast_country}", xaxis_title="Year", yaxis_title="Cases per 100,000")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Holdout MAE — linear trend", f"{mae:.1f} /100k")
        m2.metric("Holdout MAE — last value", f"{naive_mae:.1f} /100k")
        m3.metric("Projected direction", "Decreasing" if full_slope < 0 else "Increasing")
        st.caption("A lower MAE indicates better historical holdout performance. The approximate band reflects residual variation only and is not a full WHO uncertainty interval.")
        st.dataframe(forecast_df.style.format({"estimate": "{:.1f}", "lower": "{:.1f}", "upper": "{:.1f}"}), use_container_width=True, hide_index=True)

    st.markdown("### Download and inspect the project data")
    download_scope = series_window.copy()
    st.download_button(
        "Download current trend selection (CSV)",
        data=download_scope.to_csv(index=False).encode("utf-8"),
        file_name=f"tb_{mode.lower().replace(' ', '_')}_{str(selection).lower().replace(' ', '_')}_{trend_range[0]}_{trend_range[1]}.csv",
        mime="text/csv",
    )
    st.markdown("#### Data dictionary")
    st.dataframe(data_dictionary, use_container_width=True, hide_index=True)

    with st.expander("Methodology, provenance and limitations"):
        st.markdown(
            """
            **Data provenance.** The analytical files are derived from WHO Global Tuberculosis Programme indicators made available through public WHO-related repositories and mirrors. The package keeps raw files, SHA-256 hashes, retrieval dates, a source manifest, processing code and validation output.

            **Analytical unit.** The core file contains one row per country-year for 2000–2024. World and WHO-region indicators are recalculated from country values using population-weighted rates and summed counts.

            **Coverage metric.** Calculated diagnosis-and-treatment coverage equals notified new and relapse cases divided by estimated incident TB cases. Values can occasionally exceed 100 because burden estimates and surveillance counts have uncertainty and may be revised; non-negative gap fields are used for ranking.

            **Snapshot caveat.** Aggregated values from this reproducible country-level extract can differ slightly from rounded totals in WHO's published 2025 report. WHO updates estimates annually, and the latest time series supersedes earlier editions.

            **Age and sex.** The age-sex page uses a 2024 cross-section and avoids overlapping bands when summing.

            **No patient-level inference.** These are ecological national estimates; they cannot establish individual risk or causal relationships.
            """
        )

st.markdown(
    """
    <div class="footer">
    <b>Source:</b> WHO Global Tuberculosis Programme data and WHO Global Tuberculosis Report 2025-related public data resources. 
    This educational dashboard is for population-health analytics, not diagnosis or clinical decision-making.
    </div>
    """,
    unsafe_allow_html=True,
)
