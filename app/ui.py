"""
ui.py
=====
Design system and presentation components for the 'Paying for Clean Air?' dashboard.
Implements a clean, high-contrast Light / White Theme inspired by modern editorial interfaces,
with full support for dynamic Dark Mode toggling.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from interactive_viz import AQI_BANDS

_BASE_CSS = """
<style>
  /* Layout & Global Density */
  .block-container { max-width: 1400px; padding-top: 5.25rem !important; padding-bottom: 4rem; }
  @media (max-width: 768px) {
    .block-container { padding-top: 4.75rem !important; }
  }
  [data-testid="stMetricValue"], [data-testid="stDataFrame"], .num { font-variant-numeric: tabular-nums; }
  h1, h2, h3, h4 { letter-spacing: -0.018em; text-wrap: balance; font-weight: 600; }

  /* Typography */
  .eyebrow { font-size: .74rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 0 0 .35rem; }
  .page-title { font-family: Fraunces, Georgia, serif; font-weight: 600; font-size: clamp(2rem, 3.2vw, 2.75rem);
                line-height: 1.1; letter-spacing: -0.025em; margin: 0 0 .5rem; text-wrap: balance; }
  .lede { font-size: 1.02rem; line-height: 1.6; max-width: 68ch; margin: 0 0 1.5rem; text-wrap: pretty; }

  /* Brand Mark */
  .brand { display: flex; align-items: center; gap: .75rem; margin: .2rem 0 1.2rem; }
  .brand-mark { width: 2.4rem; height: 2.4rem; border-radius: .7rem; display: grid; place-items: center;
                background: linear-gradient(145deg, #1F5F74, #134252); color: #FFFFFF; flex: none;
                box-shadow: 0 3px 10px rgba(31, 95, 116, .22); }
  .brand-icon { position: relative; width: 1.35rem; height: 1.45rem; display: block; }
  .brand-roof { position: absolute; left: .31rem; top: .05rem; width: .67rem; height: .67rem;
                border-left: 2px solid currentColor; border-top: 2px solid currentColor; transform: rotate(45deg); }
  .brand-building { position: absolute; left: .33rem; top: .48rem; width: .68rem; height: .58rem;
                    border: 2px solid currentColor; border-bottom: 0; border-radius: .08rem .08rem 0 0; }
  .brand-window { position: absolute; left: .22rem; top: .18rem; width: .12rem; height: .16rem;
                  background: currentColor; border-radius: .03rem; box-shadow: .22rem 0 0 currentColor; }
  .brand-air { position: absolute; left: .02rem; bottom: .02rem; width: .62rem; height: .12rem;
               border-top: 2px solid currentColor; border-radius: 50%; transform: skewX(-25deg);
               box-shadow: .42rem .05rem 0 -.01rem currentColor; }
  .brand-name { font-family: Fraunces, Georgia, serif; font-weight: 600; font-size: 1.1rem; line-height: 1.15; }
  .brand-sub { font-size: .74rem; }

  /* Key Finding Box */
  .finding { padding: 1rem 1.25rem; margin: .4rem 0 1.4rem; border-radius: 0 .75rem .75rem 0;
             box-shadow: 0 1px 3px rgba(0, 0, 0, .04); }
  .finding-label { font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
  .finding-text { font-family: Fraunces, Georgia, serif; font-size: 1.22rem; line-height: 1.42; margin-top: .25rem; }
  .finding-note { font-size: .84rem; margin-top: .35rem; line-height: 1.5; }

  /* AQI Legend */
  .legend { display: flex; flex-wrap: wrap; gap: .45rem 1.2rem; font-size: .82rem; margin: .6rem 0 0; padding: 0; list-style: none; }
  .legend li { display: inline-flex; align-items: center; gap: .45rem; }
  .swatch { width: .75rem; height: .75rem; border-radius: 50%; flex: none; }

  /* Cluster Archetype Card */
  .archetype { padding: .9rem 1.1rem; border-radius: .7rem; margin-bottom: .65rem;
               box-shadow: 0 1px 3px rgba(0, 0, 0, .03); }
  .archetype-head { display: flex; align-items: center; gap: .55rem; font-weight: 600; font-size: .95rem; }
  .archetype-stats { display: flex; flex-wrap: wrap; gap: .3rem 1.1rem; font-size: .84rem; margin-top: .35rem; }
  .archetype-note { font-size: .82rem; margin-top: .3rem; line-height: 1.45; }

  /* Footer */
  .footnote { font-size: .78rem; margin-top: 3.5rem; padding-top: 1.2rem; line-height: 1.6; }

  /* Responsive Adjustments */
  @media (max-width: 640px) {
    .lede { font-size: .96rem; }
    .page-title { font-size: 1.85rem; }
  }
</style>
"""

_LOGO = (
    '<span class="brand-icon" aria-hidden="true">'
    '<span class="brand-roof"></span><span class="brand-building"><span class="brand-window"></span></span>'
    '<span class="brand-air"></span></span>'
)


def inject_css(dark: bool = False) -> None:
    """Apply the complete, high-contrast theme palette across all surfaces, navigation, and widgets."""
    if dark:
        # Sleek Charcoal / OLED Palette
        surface = "#131312"
        sidebar = "#181816"
        card_bg = "#1E1D1B"
        control = "#24231F"
        text_primary = "#ECEAE4"
        text_secondary = "#A6A39C"
        text_muted = "#76736C"
        border_subtle = "#302E2A"
        border_strong = "#44413C"
        primary_accent = "#7DB8CB"
        finding_bg = "rgba(125, 184, 203, 0.08)"
        finding_border = "#7DB8CB"
        finding_label = "#7DB8CB"
        card_shadow = "0 1px 3px rgba(0, 0, 0, 0.35)"
        popover_bg = "#1E1D1B"
        delta_bg = "#24231F"
        delta_text = "#ECEAE4"
        tab_inactive = "#76736C"
    else:
        # Crisp, Clean White & Slate Palette (High-Contrast Light Theme)
        surface = "#FAFAFA"
        sidebar = "#FFFFFF"
        card_bg = "#FFFFFF"
        control = "#FFFFFF"
        text_primary = "#0F172A"       # Slate 900 (High-Contrast)
        text_secondary = "#334155"     # Slate 700
        text_muted = "#64748B"         # Slate 500
        border_subtle = "#E2E8F0"      # Slate 200
        border_strong = "#CBD5E1"      # Slate 300
        primary_accent = "#1F5F74"     # Ocean Deep Teal
        finding_bg = "#F8FAFC"
        finding_border = "#1F5F74"
        finding_label = "#0F766E"
        card_shadow = "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.04)"
        popover_bg = "#FFFFFF"
        delta_bg = "#F1F5F9"
        delta_text = "#334155"
        tab_inactive = "#475569"

    tokens = (
        f"--background-color:{surface};"
        f"--secondary-background-color:{card_bg};"
        f"--text-color:{text_primary};"
        f"--primary-color:{primary_accent};"
        f"--border-color:{border_subtle};"
    )

    theme_css = f"""
<style>
  /* App Root & Main View Container */
  .stApp {{ {tokens} background-color: {surface} !important; color: {text_primary} !important; }}
  [data-testid='stAppViewContainer'] {{ background-color: {surface} !important; color: {text_primary} !important; }}
  [data-testid='stMain'] {{ background-color: {surface} !important; }}

  /* Top Navigation & App Header */
  header[data-testid="stHeader"],
  [data-testid='stHeader'] {{
    background-color: {sidebar} !important;
    border-bottom: 1px solid {border_subtle} !important;
    z-index: 99 !important;
  }}
  header[data-testid="stHeader"] * {{
    color: {text_primary} !important;
  }}
  header[data-testid="stHeader"] svg {{
    fill: {text_secondary} !important;
  }}
  [data-testid="stTopNav"] button,
  [data-testid="stTopNav"] a,
  [data-testid="stTopNav"] span,
  [data-testid="stTopNav"] div,
  [data-testid="stHeaderNav"] button,
  [data-testid="stHeaderNav"] a,
  nav[aria-label="Global"] button,
  nav[aria-label="Global"] a {{
    color: {text_primary} !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
  }}
  [data-testid="stTopNav"] svg,
  [data-testid="stHeaderNav"] svg,
  nav[aria-label="Global"] svg {{
    fill: {text_secondary} !important;
    stroke: {text_secondary} !important;
  }}

  /* Sidebar Surface & Divider */
  [data-testid='stSidebar'] {{
    background-color: {sidebar} !important;
    color: {text_primary} !important;
    border-right: 1px solid {border_subtle} !important;
    box-shadow: 1px 0 3px rgba(0, 0, 0, 0.02) !important;
  }}
  [data-testid='stSidebar'] [data-testid='stWidgetLabel'],
  [data-testid='stSidebar'] label {{
    color: {text_secondary} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
  }}
  [data-testid='stSidebar'] [data-testid='stCaptionContainer'] {{
    color: {text_muted} !important;
  }}

  /* Typography Overrides */
  .eyebrow {{ color: {primary_accent} !important; }}
  .page-title {{ color: {text_primary} !important; }}
  .lede {{ color: {text_secondary} !important; }}
  .brand {{ color: {text_primary} !important; }}
  .brand-sub {{ color: {text_muted} !important; }}
  .legend {{ color: {text_secondary} !important; }}
  .legend .range {{ color: {text_muted} !important; }}
  .footnote {{ border-top: 1px solid {border_subtle} !important; color: {text_muted} !important; }}

  /* Findings Box */
  .finding {{
    background: {finding_bg} !important;
    border: 1px solid {border_subtle} !important;
    border-left: 4px solid {finding_border} !important;
    color: {text_primary} !important;
    box-shadow: {card_shadow} !important;
  }}
  .finding-label {{ color: {finding_label} !important; }}
  .finding-text {{ color: {text_primary} !important; }}
  .finding-note {{ color: {text_muted} !important; }}

  /* Archetype Cards */
  .archetype {{
    background-color: {card_bg} !important;
    border: 1px solid {border_subtle} !important;
    color: {text_primary} !important;
    box-shadow: {card_shadow} !important;
  }}
  .archetype-head {{ color: {text_primary} !important; }}
  .archetype-stats {{ color: {text_secondary} !important; }}
  .archetype-note {{ color: {text_muted} !important; }}

  /* Metric Cards & Container Boxes */
  [data-testid='stVerticalBlockBorderWrapper'] {{
    background-color: {card_bg} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 0.75rem !important;
    box-shadow: {card_shadow} !important;
  }}

  /* All Graphs & Charts: Thin Outline Border Cards */
  [data-testid='stPlotlyChart'],
  .stPlotlyChart {{
    background-color: {card_bg} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 0.75rem !important;
    box-shadow: {card_shadow} !important;
    padding: 0.6rem 0.5rem 0.25rem 0.5rem !important;
    overflow: hidden !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
  }}
  [data-testid='stPlotlyChart']:hover,
  .stPlotlyChart:hover {{
    border-color: {border_strong} !important;
  }}

  [data-testid='stDeckGlChart'],
  .stDeckGlChart {{
    background-color: {card_bg} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 0.75rem !important;
    box-shadow: {card_shadow} !important;
    overflow: hidden !important;
  }}

  [data-testid='stMetric'] {{
    background-color: {card_bg} !important;
  }}
  [data-testid='stMetricLabel'] {{
    color: {text_muted} !important;
    font-weight: 600 !important;
    font-size: 0.76rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
  }}
  [data-testid='stMetricValue'] {{
    color: {text_primary} !important;
    font-weight: 700 !important;
  }}

  /* Metric Delta Badge (High Contrast Fix) */
  [data-testid='stMetricDelta'] {{
    background-color: {delta_bg} !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
  }}
  [data-testid='stMetricDelta'] * {{
    color: {delta_text} !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
  }}
  [data-testid='stMetricDelta'] svg {{
    fill: {delta_text} !important;
  }}

  /* Form Controls: Selectbox, Inputs & Number Inputs */
  [data-baseweb='select'],
  [data-baseweb='select'] > div,
  [data-baseweb='select'] > div:first-child {{
    background-color: {control} !important;
    border: 1px solid {border_strong} !important;
    border-radius: 0.5rem !important;
  }}
  [data-baseweb='select'] * {{
    color: {text_primary} !important;
    background-color: transparent !important;
  }}
  [data-baseweb='select'] svg {{
    fill: {text_secondary} !important;
  }}
  [data-baseweb='popover'],
  [data-baseweb='menu'],
  ul[role='listbox'] {{
    background-color: {popover_bg} !important;
    color: {text_primary} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 0.5rem !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.06) !important;
  }}
  li[role='option'],
  li[role='option'] * {{
    background-color: {popover_bg} !important;
    color: {text_primary} !important;
  }}
  li[role='option']:hover,
  li[role='option'][aria-selected='true'] {{
    background-color: {"#24231F" if dark else "#F1F5F9"} !important;
    color: {text_primary} !important;
  }}

  /* Number Inputs */
  [data-testid='stNumberInput'] input {{
    background-color: {control} !important;
    color: {text_primary} !important;
    border-color: {border_strong} !important;
  }}
  [data-testid='stNumberInput'] button {{
    background-color: {"#1E1D1B" if dark else "#F8FAFC"} !important;
    color: {text_secondary} !important;
    border-color: {border_strong} !important;
  }}

  /* Sliders */
  [data-testid='stSlider'] label {{
    color: {text_secondary} !important;
  }}
  [data-testid='stSlider'] [data-baseweb='slider'] div {{
    color: {text_primary} !important;
  }}

  /* Pills & Segmented Controls */
  [data-testid='stPills'] button {{
    background-color: {control} !important;
    color: {text_secondary} !important;
    border: 1px solid {border_strong} !important;
    border-radius: 9999px !important;
    font-weight: 500 !important;
  }}
  [data-testid='stPills'] button[aria-selected='true'] {{
    background-color: {primary_accent} !important;
    color: #FFFFFF !important;
    border-color: {primary_accent} !important;
  }}
  [data-testid='stSegmentedControl'] {{
    background-color: {"#1E1D1B" if dark else "#F1F5F9"} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 0.5rem !important;
    padding: 2px !important;
  }}
  [data-testid='stSegmentedControl'] button {{
    background-color: transparent !important;
    color: {text_muted} !important;
    border: none !important;
    border-radius: 0.375rem !important;
    font-weight: 500 !important;
  }}
  [data-testid='stSegmentedControl'] button[aria-selected='true'] {{
    background-color: {card_bg} !important;
    color: {text_primary} !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
  }}

  /* Buttons */
  [data-testid='stBaseButton-secondary'] {{
    background-color: {control} !important;
    color: {text_primary} !important;
    border: 1px solid {border_strong} !important;
    border-radius: 0.5rem !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
  }}
  [data-testid='stBaseButton-secondary']:hover {{
    background-color: {"#24231F" if dark else "#F8FAFC"} !important;
    border-color: {primary_accent} !important;
    color: {primary_accent} !important;
  }}
  [data-testid='stBaseButton-primary'] {{
    background-color: {primary_accent} !important;
    color: #FFFFFF !important;
    border: 1px solid {primary_accent} !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
  }}
  [data-testid='stBaseButton-primary']:hover {{
    background-color: {"#68A3B6" if dark else "#174D63"} !important;
  }}

  /* Dataframe Table Surface */
  [data-testid='stDataFrame'] {{
    background-color: {card_bg} !important;
    color: {text_primary} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 0.5rem !important;
  }}

  /* Tabs Styling (High Contrast Fix) */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {{
    border-bottom: 1px solid {border_subtle} !important;
    gap: 12px !important;
  }}
  [data-testid="stTabs"] [data-baseweb="tab"] {{
    color: {tab_inactive} !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 8px 16px !important;
    opacity: 1 !important;
  }}
  [data-testid="stTabs"] [data-baseweb="tab"] * {{
    color: {tab_inactive} !important;
    font-weight: 600 !important;
  }}
  [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {{
    color: {primary_accent} !important;
    font-weight: 700 !important;
    border-bottom: 2.5px solid {primary_accent} !important;
  }}
  [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] * {{
    color: {primary_accent} !important;
  }}
  [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    background-color: {primary_accent} !important;
  }}

  /* Scrollbars */
  ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
  ::-webkit-scrollbar-track {{ background: {surface}; }}
  ::-webkit-scrollbar-thumb {{ background: {border_strong}; border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: {text_muted}; }}
</style>
"""
    st.html(_BASE_CSS + theme_css)


def brand() -> None:
    st.html(
        f'<div class="brand"><span class="brand-mark">{_LOGO}</span>'
        '<div><div class="brand-name">Paying for Clean Air?</div>'
        '<div class="brand-sub">Rental prices × urban air quality</div></div></div>'
    )


def page_header(eyebrow: str, title: str, lede: str) -> None:
    st.html(
        f'<p class="eyebrow">{escape(eyebrow)}</p>'
        f'<h1 class="page-title">{escape(title)}</h1>'
        f'<p class="lede">{escape(lede)}</p>'
    )


def finding(label: str, text: str, note: str = "") -> None:
    """A highlighted takeaway. `text` may contain trusted inline HTML (we build it ourselves)."""
    note_html = f'<div class="finding-note">{escape(note)}</div>' if note else ""
    st.html(f'<div class="finding"><div class="finding-label">{escape(label)}</div><div class="finding-text">{text}</div>{note_html}</div>')


def aqi_legend() -> None:
    items, lower = [], 0
    for upper, label, color in AQI_BANDS:
        rng = f"{lower}+" if upper == float("inf") else f"{lower}–{int(upper)}"
        items.append(f'<li><span class="swatch" style="background:{color}"></span>{label} <span class="range">{rng}</span></li>')
        lower = int(upper) + 1 if upper != float("inf") else lower
    st.html(f'<ul class="legend" aria-label="AQI colour scale">{"".join(items)}</ul>')


def archetype_card(name: str, color: str, stats: list[str], note: str) -> None:
    st.html(
        f'<div class="archetype"><div class="archetype-head"><span class="swatch" style="background:{color}"></span>{escape(name)}</div>'
        f'<div class="archetype-stats num">{"".join(f"<span>{escape(s)}</span>" for s in stats)}</div>'
        f'<div class="archetype-note">{escape(note)}</div></div>'
    )


def footnote() -> None:
    st.html(
        '<div class="footnote">University lab project. Listings are synthetic, modelled on Inside Airbnb data; '
        "prices converted to INR at January 2024 rates. AQI bands follow the US EPA scale. "
        "Live readings come from the Open-Meteo Air Quality API. Use the sidebar toggle to switch themes.</div>"
    )
