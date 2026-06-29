from __future__ import annotations

import plotly.graph_objects as go

from dashboard.config import NAVY, WHITE


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
