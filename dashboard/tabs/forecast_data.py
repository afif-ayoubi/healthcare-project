from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.config import CORAL, TEAL
from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState


def render_forecast_data_tab(data: DashboardData, state: SelectionState) -> None:
    st.subheader("Exploratory projection and data access")
    st.markdown(
        '<div class="section-note"><b>Forecasting guardrail:</b> this is a descriptive time-series extrapolation, not a causal or clinical prediction. '
        'Policy shifts, outbreaks, conflict, diagnostics and reporting changes can invalidate the projection.</div>',
        unsafe_allow_html=True,
    )
    countries = sorted(data.country["country"].dropna().unique())
    forecast_country = st.selectbox(
        "Country for exploratory incidence-rate projection",
        countries,
        index=countries.index(state.selection) if state.mode == "Country" and state.selection in set(data.country["country"]) else 0,
    )
    history_years = st.slider("Training window (most recent years)", 8, 20, 12)
    fc = data.country[
        (data.country["country"] == forecast_country) & data.country["e_inc_100k"].notna()
    ].sort_values("year")[["year", "e_inc_100k"]].copy()
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
    download_scope = state.series_window.copy()
    st.download_button(
        "Download current trend selection (CSV)",
        data=download_scope.to_csv(index=False).encode("utf-8"),
        file_name=f"tb_{state.mode.lower().replace(' ', '_')}_{str(state.selection).lower().replace(' ', '_')}_{state.trend_range[0]}_{state.trend_range[1]}.csv",
        mime="text/csv",
    )
    st.markdown("#### Data dictionary")
    st.dataframe(data.data_dictionary, use_container_width=True, hide_index=True)

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
