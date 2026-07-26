"""Shared Plotly styling for a compact, legible dark dashboard."""

from __future__ import annotations

import plotly.graph_objects as go

BACKGROUND = "#09121F"
PANEL = "#142235"
TEXT = "#E8F0F7"
MUTED = "#9FB0C3"
GRID = "#2B3B50"
ACCENT = "#20B486"
NEGATIVE = "#E76F75"

RETURN_COLORSCALE = [
    [0.0, "#C64D5B"],
    [0.5, "#F3F6F8"],
    [1.0, "#159B70"],
]
CORRELATION_COLORSCALE = [
    [0.0, "#4F6EA8"],
    [0.5, "#F3F6F8"],
    [1.0, "#C65A64"],
]


def apply_theme(fig: go.Figure, **layout_updates: object) -> go.Figure:
    """Apply the project's Plotly defaults while allowing plot-specific options."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font={"color": TEXT, "family": "Inter, Arial, sans-serif"},
        margin={"l": 16, "r": 16, "t": 46, "b": 16},
        hoverlabel={"bgcolor": PANEL, "font": {"color": TEXT}},
        **layout_updates,
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig
