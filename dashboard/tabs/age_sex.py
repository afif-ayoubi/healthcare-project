from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.config import CORAL, TEAL
from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState, selected_age_data
from dashboard.formatting import fmt_count


def render_age_sex_tab(data: DashboardData, state: SelectionState) -> None:
    st.subheader("Estimated TB incidence by age and sex — 2024")
    st.markdown(
        '<div class="section-note"><b>Scope note:</b> age-sex estimates in this project are a 2024 cross-section. '
        'The chart uses non-overlapping age bands to avoid double-counting.</div>',
        unsafe_allow_html=True,
    )
    non_overlapping = ["0_4", "5_9", "10_14", "15_19", "20_24", "25_34", "35_44", "45_54", "55_64", "65plus"]
    age_scope = selected_age_data(data, state.mode, state.selection)
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
            title=f"Age-sex distribution of estimated incident TB — {state.selection}",
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
