from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"

NAVY = "#0B1F33"
TEAL = "#0E7490"
MINT = "#14B8A6"
CORAL = "#E76F51"
GOLD = "#F4A261"
SLATE = "#64748B"
PALE = "#F4F8FB"
WHITE = "#FFFFFF"

PAGE_CONFIG = {
    "page_title": "Global TB Burden & Treatment Gaps",
    "page_icon": "🫁",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
