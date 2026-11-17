"""
ui.py
=====
Small presentational helpers for the Streamlit dashboard. Colours, fonts and radii live in
.streamlit/config.toml; the CSS here only adds layout details Streamlit has no option for, and
uses currentColor so it works unchanged in light and dark mode.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from interactive_viz import AQI_BANDS

_CSS = """
<style>
  .block-container { max-width: 1400px; padding-bottom: 4rem; }
  [data-testid="stMetricValue"], [data-testid="stDataFrame"], .num { font-variant-numeric: tabular-nums; }
  h1, h2, h3 { letter-spacing: -0.015em; text-wrap: balance; }

  .eyebrow { font-size: .74rem; font-weight: 600; letter-spacing: .09em; text-transform: uppercase; opacity: .62; margin: 0 0 .35rem; }
  .page-title { font-family: Fraunces, Georgia, serif; font-weight: 600; font-size: clamp(2rem, 3.4vw, 2.9rem);
                line-height: 1.08; letter-spacing: -0.025em; margin: 0 0 .6rem; text-wrap: balance; }
  .lede { font-size: 1.04rem; line-height: 1.6; max-width: 68ch; opacity: .78; margin: 0 0 1.6rem; text-wrap: pretty; }

  .brand { display: flex; align-items: center; gap: .7rem; margin: .2rem 0 1.1rem; }
  .brand-mark { width: 2.1rem; height: 2.1rem; border-radius: .6rem; display: grid; place-items: center;
                background: #1F5F74; color: #F6F4EF; flex: none; }
  .brand-name { font-family: Fraunces, Georgia, serif; font-weight: 600; font-size: 1.08rem; line-height: 1.15; }
  .brand-sub { font-size: .74rem; opacity: .6; }

  .finding { border-left: 3px solid #1F5F74; padding: .9rem 1.1rem; margin: .4rem 0 1.4rem;
             background: color-mix(in srgb, currentColor 4%, transparent); border-radius: 0 .6rem .6rem 0; }
  .finding-label { font-size: .72rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; opacity: .6; }
  .finding-text { font-family: Fraunces, Georgia, serif; font-size: 1.22rem; line-height: 1.4; margin-top: .2rem; }
  .finding-note { font-size: .82rem; opacity: .65; margin-top: .35rem; }

  .legend { display: flex; flex-wrap: wrap; gap: .4rem 1.1rem; font-size: .82rem; margin: .6rem 0 0; padding: 0; list-style: none; }
  .legend li { display: inline-flex; align-items: center; gap: .4rem; }
  .swatch { width: .72rem; height: .72rem; border-radius: 50%; flex: none; }
  .legend .range { opacity: .65; }

  .archetype { padding: .85rem 1rem; border-radius: .6rem; margin-bottom: .6rem;
               border: 1px solid color-mix(in srgb, currentColor 12%, transparent); }
  .archetype-head { display: flex; align-items: center; gap: .5rem; font-weight: 600; }
  .archetype-stats { display: flex; flex-wrap: wrap; gap: .2rem 1rem; font-size: .84rem; opacity: .8; margin-top: .3rem; }
  .archetype-note { font-size: .82rem; opacity: .65; margin-top: .25rem; }

  .footnote { font-size: .78rem; opacity: .55; margin-top: 3rem; padding-top: 1rem;
              border-top: 1px solid color-mix(in srgb, currentColor 12%, transparent); }

  @media (max-width: 640px) { .lede { font-size: .98rem; } }
</style>
"""

_LOGO = '<span aria-hidden="true" style="font-size:1.25rem;line-height:1">≋</span>'  # st.html strips inline SVG


def inject_css() -> None:
    st.html(_CSS)


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
        "Live readings come from the Open-Meteo Air Quality API. Switch light/dark mode from the ⋮ menu → Settings.</div>"
    )
