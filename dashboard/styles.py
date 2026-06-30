from __future__ import annotations

import streamlit as st

from dashboard.config import CORAL, MINT, NAVY, PALE, SLATE, TEAL


def apply_global_styles() -> None:
    st.markdown(
        f"""
        <style>
        :root {{ --navy:{NAVY}; --teal:{TEAL}; --mint:{MINT}; --coral:{CORAL}; --pale:{PALE}; }}
        .stApp {{ background: linear-gradient(180deg, #F7FAFC 0%, #FFFFFF 28%); color: {NAVY}; }}
        header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
        [data-testid="stStatusWidget"], [data-testid="stHeaderActionElements"], .stDeployButton,
        #MainMenu, footer {{ display: none !important; visibility: hidden !important; height: 0 !important; }}
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
        .filter-guide {{ display:flex; flex-wrap:wrap; gap:.45rem; margin:.25rem 0 1.1rem 0; }}
        .filter-chip {{ background:#EAF5F7; border:1px solid #CFE4EA; border-radius:999px; color:{NAVY}; font-size:.83rem; font-weight:700; padding:.34rem .65rem; }}
        .section-head {{ margin:1.05rem 0 .4rem 0; }}
        .section-head h3 {{ margin:0 0 .15rem 0; font-size:1.25rem; }}
        .section-head p {{ margin:0; color:{SLATE}; font-size:.9rem; line-height:1.35; }}
        .insight {{ background: white; border: 1px solid #DDE7EC; border-radius: 8px; padding: 1rem; height: 100%; box-shadow: 0 4px 16px rgba(11,31,51,.04); }}
        .insight b {{ color:{TEAL}; }}
        [data-testid="stMetric"] {{ background:white; border:1px solid #DDE7EC; border-radius:8px; padding:.75rem .85rem; box-shadow:0 4px 14px rgba(11,31,51,.04); }}
        [data-testid="stMetricLabel"] {{ color:{SLATE}; font-weight:700; }}
        [data-testid="stMetricValue"] {{ color:{NAVY}; font-weight:800; font-size:1.7rem; }}
        .smallprint {{ font-size:.82rem; color:{SLATE}; line-height:1.45; }}
        .footer {{ border-top:1px solid #DDE7EC; padding-top:1rem; color:{SLATE}; font-size:.8rem; }}
        [data-testid="stPlotlyChart"] {{ background:white; border:1px solid #E2EBF0; border-radius:8px; padding:.35rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
