"""
Paying for Clean Air? Airbnb Pricing and Urban Air Quality
Streamlit Dashboard — Interactive Analytics with Coordinated Dark & Light Theme
"""

import sys
import os
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import statsmodels.api as sm
from scipy import stats

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))

from viz_modules import (
    plot_price_vs_aqi_scatter,
    plot_city_price_boxplot,
    plot_aqi_map_heatmap,
    plot_room_type_price,
    plot_correlation_heatmap,
    plot_aqi_price_regression_by_city,
    plot_price_distribution,
    plot_neighbourhood_price,
    plot_availability_vs_price,
    plot_ols_summary_table,
)
from interactive_viz import (
    plot_price_vs_aqi_interactive,
    plot_aqi_city_ranking_interactive,
    plot_room_type_interactive,
    plot_city_price_boxplot_interactive,
    plot_price_distribution_interactive,
    plot_availability_vs_price_interactive,
    plot_correlation_heatmap_interactive,
)
from live_aqi_service import fetch_live_aqi_for_city, CITY_COORDINATES

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Inside Airbnb | Clean Air Analytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme State Initialization (Supports 🌙 Dark Mode & ☀️ White/Light Theme)
# ---------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "🌙 Dark Mode"

# Sidebar Top: Brand Logo and Theme Switcher
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <svg width="32" height="34" viewBox="0 0 32 32" fill="#FF385C" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 1c2.008 0 3.463.963 4.751 3.269l.533 1.025c1.954 3.83 4.116 8.347 5.14 10.638 1.411 3.167 1.819 5.485 1.258 7.218-.68 2.1-2.458 3.55-4.877 3.978-2.613.462-5.011-.476-6.805-2.673-1.794 2.197-4.192 3.135-6.805 2.673-2.419-.428-4.197-1.878-4.877-3.978-.561-1.733-.153-4.051 1.258-7.218 1.024-2.291 3.186-6.808 5.14-10.638l.533-1.025C12.537 1.963 13.992 1 16 1zm0 2c-1.397 0-2.395.666-3.411 2.479l-.538 1.034C10.098 10.34 7.94 14.85 6.924 17.132c-1.196 2.684-1.464 4.475-1.047 5.761.472 1.458 1.761 2.502 3.593 2.827 2.197.389 4.292-.472 5.867-2.457l.663-.836.663.836c1.575 1.985 3.67 2.846 5.867 2.457 1.832-.325 3.121-1.369 3.593-2.827.417-1.286.149-3.077-1.047-5.761-1.016-2.282-3.174-6.792-5.127-10.619l-.538-1.034C18.395 3.666 17.397 3 16 3zm0 11c2.209 0 4 1.791 4 4 0 2.221-1.365 3.535-3.076 4.673l-.424.275-.5.312-.5-.312C13.84 21.84 12 20.25 12 18c0-2.209 1.791-4 4-4zm0 2c-1.105 0-2 .895-2 2 0 1.054 1.155 2.133 2 2.732.845-.599 2-1.678 2-2.732 0-1.105-.895-2-2-2z"/>
            </svg>
            <div>
                <div style="font-weight:800; font-size:1.18rem; color:#ff385c; line-height:1.15; letter-spacing:-0.5px;">inside airbnb</div>
                <div style="font-size:0.68rem; font-weight:700; color:var(--text-muted); letter-spacing:0.8px; text-transform:uppercase;">Clean Air Analytics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-category">Appearance & Theme</div>', unsafe_allow_html=True)
    selected_theme = st.radio(
        "Theme Mode",
        ["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state["theme_mode"] == "🌙 Dark Mode" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["theme_mode"] = selected_theme

is_dark = (st.session_state["theme_mode"] == "🌙 Dark Mode")
plotly_template = "plotly_dark" if is_dark else "plotly_white"

# ---------------------------------------------------------------------------
# Dynamic CSS Injection (Applied at top of app before controls are rendered)
# ---------------------------------------------------------------------------
if is_dark:
    css_tokens = """
        :root {
            --app-bg: #121417;
            --sidebar-bg: #191c21;
            --sidebar-border: #282c34;
            --card-bg: #1a1e24;
            --card-border: #2a2f38;
            --text-title: #ffffff;
            --text-body: #f1f5f9;
            --text-muted: #94a3b8;
            --active-pill: #2b3039;
            --active-pill-text: #ffffff;
            --input-bg: #1e2229;
            --input-border: #2a2f38;
            --radio-bg: #1e2229;
            --radio-border: #2a2f38;
            --radio-text: #f1f5f9;
            --badge-green-bg: rgba(34, 197, 94, 0.15);
            --badge-green-txt: #4ade80;
            --badge-red-bg: rgba(239, 68, 68, 0.15);
            --badge-red-txt: #f87171;
            --code-bg: #1e2229;
        }
    """
else:
    css_tokens = """
        :root {
            --app-bg: #f8fafc;
            --sidebar-bg: #ffffff;
            --sidebar-border: #e2e8f0;
            --card-bg: #ffffff;
            --card-border: #e2e8f0;
            --text-title: #0f172a;
            --text-body: #1e293b;
            --text-muted: #475569;
            --active-pill: #f1f5f9;
            --active-pill-text: #0f172a;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --radio-bg: #ffffff;
            --radio-border: #cbd5e1;
            --radio-text: #0f172a;
            --badge-green-bg: #dcfce7;
            --badge-green-txt: #15803d;
            --badge-red-bg: #fee2e2;
            --badge-red-txt: #b91c1c;
            --code-bg: #f8fafc;
        }
    """

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        {css_tokens}

        html, body, [class*="css"], .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--app-bg) !important;
            color: var(--text-body) !important;
        }}

        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--sidebar-border) !important;
            padding-top: 1rem !important;
        }}

        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 10px;
            margin-bottom: 14px;
            border-bottom: 1px solid var(--sidebar-border);
            padding-bottom: 14px;
        }}

        .main-logo-header {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--sidebar-border);
        }}

        .nav-category {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted) !important;
            margin-top: 14px;
            margin-bottom: 6px;
            padding-left: 6px;
        }}

        .sidebar-active-pill {{
            background-color: var(--active-pill);
            color: var(--active-pill-text);
            font-weight: 600;
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            margin-bottom: 12px;
            border: 1px solid var(--card-border);
        }}

        .dashboard-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
        }}

        .metric-header-title {{
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
        }}

        .big-metric-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--text-title);
            line-height: 1.1;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }}

        .metric-badge-green {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background-color: var(--badge-green-bg);
            color: var(--badge-green-txt);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 700;
        }}

        .metric-badge-red {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background-color: var(--badge-red-bg);
            color: var(--badge-red-txt);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 700;
        }}

        .metric-badge-sub {{
            color: var(--text-muted);
            font-size: 0.78rem;
            margin-left: 6px;
        }}

        .live-status-footer {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px solid var(--card-border);
        }}

        .live-dot {{
            width: 8px;
            height: 8px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
        }}

        .page-title {{
            font-size: 2.4rem;
            font-weight: 800;
            color: var(--text-title);
            letter-spacing: -0.8px;
            margin-bottom: 6px;
        }}

        .page-subtitle {{
            font-size: 0.96rem;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 6px;
        }}

        .page-timestamp {{
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .chart-header {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-title);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .chart-subcaption {{
            font-size: 0.82rem;
            color: var(--text-muted);
            font-weight: 400;
        }}

        /* Strict Radio Button Font & Contrast Rules */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label *,
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span,
        div[role="radiogroup"] label,
        div[role="radiogroup"] label * {{
            color: var(--radio-text) !important;
            font-weight: 500 !important;
        }}

        div[role="radiogroup"] > label {{
            background-color: var(--radio-bg) !important;
            border: 1px solid var(--radio-border) !important;
            border-radius: 8px !important;
            padding: 6px 12px !important;
            margin-bottom: 4px !important;
            font-size: 0.88rem !important;
        }}

        div[role="radiogroup"] > label[data-checked="true"],
        div[role="radiogroup"] > label:hover {{
            border-color: #ff385c !important;
            background-color: var(--active-pill) !important;
        }}

        /* Strict Widget Label Visibility Rules */
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] span {{
            color: var(--text-title) !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }}

        /* Robust Selectbox and Multiselect Inputs Styling (fixes dark mode white box issue) */
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-testid="stMultiSelect"] > div,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div {{
            background-color: var(--input-bg) !important;
            border-color: var(--input-border) !important;
            color: var(--text-body) !important;
        }}

        div[data-baseweb="select"] *,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {{
            color: var(--text-body) !important;
        }}

        span[data-baseweb="tag"] {{
            background-color: #ff385c !important;
            color: #ffffff !important;
            border-radius: 6px !important;
        }}
        span[data-baseweb="tag"] * {{
            color: #ffffff !important;
        }}

        /* Robust Number Inputs and +/- Buttons (fixes dark mode white box issue) */
        div[data-testid="stNumberInputContainer"],
        div[data-testid="stNumberInputContainer"] > div,
        div[data-testid="stNumberInputContainer"] input,
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
        div[data-testid="stNumberInput"] button {{
            background-color: var(--input-bg) !important;
            border-color: var(--input-border) !important;
            color: var(--text-body) !important;
        }}

        div[data-testid="stNumberInput"] button:hover {{
            background-color: var(--active-pill) !important;
            color: #ff385c !important;
        }}

        div[data-testid="stNumberInput"] input {{
            background-color: var(--input-bg) !important;
            border: 1px solid var(--input-border) !important;
            color: var(--text-body) !important;
            border-radius: 8px !important;
        }}

        div[data-testid="stNumberInput"] button svg {{
            fill: var(--text-body) !important;
        }}

        /* Dropdown popover menu styling */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        ul[data-baseweb="menu"],
        li[data-baseweb="menu-item"] {{
            background-color: var(--card-bg) !important;
            color: var(--text-body) !important;
            border-color: var(--card-border) !important;
        }}

        li[data-baseweb="menu-item"]:hover {{
            background-color: var(--active-pill) !important;
            color: #ff385c !important;
        }}

        /* Sidebar paragraphs and spans */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] small {{
            color: var(--text-body);
        }}

        .js-plotly-plot, .plot-container {{
            background-color: transparent !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_PATH = ROOT / "data" / "processed" / "merged_listings.csv"


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(f"Processed dataset not found at `{DATA_PATH}`. Please run `data_merger.py` first.")
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")
    df["price_inr"] = pd.to_numeric(df["price_inr"], errors="coerce")
    return df


df_raw = load_data()

# ---------------------------------------------------------------------------
# Sidebar Content & Filter Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    # 3. Live Dashboard Status
    st.markdown('<div class="nav-category">Live</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-active-pill">📡 Live Dashboard</div>', unsafe_allow_html=True)

    # 4. Navigation Topics
    st.markdown('<div class="nav-category">Topics & Analysis</div>', unsafe_allow_html=True)
    active_nav = st.radio(
        "Navigation",
        [
            "💎 Overview & Clean Air",
            "🗺️ Geospatial Point Map",
            "🏠 Room Types & Tariffs",
            "📈 Econometric Regressions",
            "⚖️ City Comparison",
            "📋 Data & Sources",
        ],
        index=0,
        label_visibility="collapsed",
    )

    # 5. Filters & Region Selection
    st.markdown('<div class="nav-category">Filters & Region</div>', unsafe_allow_html=True)
    cities_list = ["All Cities (Global View)"] + sorted(df_raw["city"].dropna().unique().tolist())
    selected_city = st.selectbox("City Selection", cities_list, index=0)

    available_room_types = sorted(df_raw["room_type"].dropna().unique().tolist())
    selected_rooms = st.multiselect("Room Types", available_room_types, default=available_room_types)

    # 6. Parameter Thresholds
    st.markdown('<div class="nav-category">Parameter Thresholds</div>', unsafe_allow_html=True)
    col_aq1, col_aq2 = st.columns(2)
    with col_aq1:
        min_aqi = st.number_input("Min AQI", min_value=0, max_value=500, value=0, step=5)
    with col_aq2:
        max_aqi = st.number_input("Max AQI", min_value=0, max_value=500, value=250, step=5)

    max_p = int(df_raw["price_inr"].max() if not df_raw["price_inr"].isna().all() else 100000)
    col_pr1, col_pr2 = st.columns(2)
    with col_pr1:
        min_price = st.number_input("Min Price (₹)", min_value=0, max_value=max_p, value=0, step=1000)
    with col_pr2:
        max_price = st.number_input("Max Price (₹)", min_value=0, max_value=max_p, value=max_p, step=2000)

    if min_aqi > max_aqi:
        min_aqi, max_aqi = max_aqi, min_aqi
    if min_price > max_price:
        min_price, max_price = max_price, min_price

    st.markdown('<div class="nav-category">Data Meta</div>', unsafe_allow_html=True)
    st.caption("📡 Source: Inside Airbnb & Open-Meteo Air Quality API")
    st.caption("💵 Rates: Jan 2024 Base Pegged to INR")

# ---------------------------------------------------------------------------
# Filter Data
# ---------------------------------------------------------------------------
df = df_raw.copy()
if selected_city != "All Cities (Global View)":
    df = df[df["city"] == selected_city]

if selected_rooms:
    df = df[df["room_type"].isin(selected_rooms)]

df = df[(df["aqi"] >= min_aqi) & (df["aqi"] <= max_aqi)]
df = df[(df["price_inr"] >= min_price) & (df["price_inr"] <= max_price)]

if df.empty:
    st.warning("⚠️ No listings found matching the selected filters. Please expand your criteria.")
    st.stop()

# ---------------------------------------------------------------------------
# Main Header with Brand Logo
# ---------------------------------------------------------------------------
now_str = datetime.now().strftime("%d %b %Y, %H:%M:%S")

st.markdown(
    """
    <div class="main-logo-header">
        <svg width="42" height="44" viewBox="0 0 32 32" fill="#FF385C" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 1c2.008 0 3.463.963 4.751 3.269l.533 1.025c1.954 3.83 4.116 8.347 5.14 10.638 1.411 3.167 1.819 5.485 1.258 7.218-.68 2.1-2.458 3.55-4.877 3.978-2.613.462-5.011-.476-6.805-2.673-1.794 2.197-4.192 3.135-6.805 2.673-2.419-.428-4.197-1.878-4.877-3.978-.561-1.733-.153-4.051 1.258-7.218 1.024-2.291 3.186-6.808 5.14-10.638l.533-1.025C12.537 1.963 13.992 1 16 1zm0 2c-1.397 0-2.395.666-3.411 2.479l-.538 1.034C10.098 10.34 7.94 14.85 6.924 17.132c-1.196 2.684-1.464 4.475-1.047 5.761.472 1.458 1.761 2.502 3.593 2.827 2.197.389 4.292-.472 5.867-2.457l.663-.836.663.836c1.575 1.985 3.67 2.846 5.867 2.457 1.832-.325 3.121-1.369 3.593-2.827.417-1.286.149-3.077-1.047-5.761-1.016-2.282-3.174-6.792-5.127-10.619l-.538-1.034C18.395 3.666 17.397 3 16 3zm0 11c2.209 0 4 1.791 4 4 0 2.221-1.365 3.535-3.076 4.673l-.424.275-.5.312-.5-.312C13.84 21.84 12 20.25 12 18c0-2.209 1.791-4 4-4zm0 2c-1.105 0-2 .895-2 2 0 1.054 1.155 2.133 2 2.732.845-.599 2-1.678 2-2.732 0-1.105-.895-2-2-2z"/>
        </svg>
        <div>
            <div style="font-size: 1.55rem; font-weight: 800; color: #FF385C; line-height: 1.1; letter-spacing: -0.5px;">inside airbnb</div>
            <div style="font-size: 0.72rem; font-weight: 700; color: var(--text-muted); letter-spacing: 0.8px; text-transform: uppercase;">Urban Air Quality & Housing Economics Laboratory</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Live Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="page-subtitle">Real-time listing prices, urban air quality index (AQI) correlations, and lodging distributions across 45 major world metropolitan centers. All metrics pegged to Indian Rupees (INR).</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="page-timestamp">⏱️ Updated {now_str} (your local time). Global monitoring data assimilating ground sensor feeds and satellite observations.</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# VIEW 1: Overview & Clean Air
# ---------------------------------------------------------------------------
if active_nav == "💎 Overview & Clean Air":
    st.markdown(f"### Urban Air Quality & Pricing Overview — {selected_city}")

    live_city_info = None
    if selected_city != "All Cities (Global View)":
        live_city_info = fetch_live_aqi_for_city(selected_city)

    col_c1, col_c2 = st.columns(2)

    total_listings = len(df)
    median_price = df["price_inr"].median()
    mean_aqi = df["aqi"].mean()
    clean_air_pct = (df["aqi"] <= 50).mean() * 100
    entire_home_pct = (df["room_type"] == "Entire home/apt").mean() * 100

    with col_c1:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="metric-header-title">Median Nightly Price (₹ INR) ⓘ</div>
                <div class="big-metric-value">₹{median_price:,.0f}</div>
                <div>
                    <span class="metric-badge-green">▲ {entire_home_pct:.1f}% Entire Homes</span>
                    <span class="metric-badge-sub">vs shared accommodations</span>
                </div>
                <div class="live-status-footer">
                    <span class="live-dot"></span> <b>Active</b> {total_listings:,} listings in current viewport
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c2:
        if live_city_info and live_city_info.get("us_aqi") is not None:
            live_val = live_city_info["us_aqi"]
            pm25 = live_city_info.get("pm2_5", "N/A")
            live_badge_class = "metric-badge-green" if live_val <= 50 else ("metric-badge-red" if live_val > 100 else "metric-badge-green")
            live_status = "Good (WHO Standard)" if live_val <= 50 else ("Moderate" if live_val <= 100 else "Unhealthy")
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="metric-header-title">Live Sensor AQI (Open-Meteo API) ⓘ</div>
                    <div class="big-metric-value">{live_val}</div>
                    <div>
                        <span class="{live_badge_class}">● PM2.5: {pm25} µg/m³</span>
                        <span class="metric-badge-sub">{live_status}</span>
                    </div>
                    <div class="live-status-footer">
                        <span class="live-dot"></span> <b>Live Feed</b> Ground stations & satellite assimilation
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            aqi_badge_class = "metric-badge-green" if mean_aqi <= 50 else ("metric-badge-red" if mean_aqi > 100 else "metric-badge-green")
            aqi_status_text = "Good (WHO Standard)" if mean_aqi <= 50 else ("Moderate" if mean_aqi <= 100 else "Unhealthy")
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="metric-header-title">Average Air Quality Index (AQI) ⓘ</div>
                    <div class="big-metric-value">{mean_aqi:.1f}</div>
                    <div>
                        <span class="{aqi_badge_class}">● {clean_air_pct:.1f}% Clean Air</span>
                        <span class="metric-badge-sub">{aqi_status_text}</span>
                    </div>
                    <div class="live-status-footer">
                        <span class="live-dot"></span> <b>Compliance</b> 45 global cities tracked
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Lower Section: Scatter and Horizontal Bar (theme=None preserves dark background)
    col_g1, col_g2 = st.columns([1.1, 1.0])
    with col_g1:
        st.markdown(
            '<div class="chart-header"><span>Nightly Price vs. AQI Elasticity</span>'
            '<span class="chart-subcaption">OLS Fit & Pearson Correlation</span></div>',
            unsafe_allow_html=True,
        )
        fig_scatter = plot_price_vs_aqi_interactive(df, template=plotly_template)
        st.plotly_chart(fig_scatter, use_container_width=True, theme=None)

    with col_g2:
        st.markdown(
            '<div class="chart-header"><span>Global City AQI Benchmark Ranking</span>'
            '<span class="chart-subcaption">Mean Urban AQI</span></div>',
            unsafe_allow_html=True,
        )
        fig_rank = plot_aqi_city_ranking_interactive(df, template=plotly_template)
        st.plotly_chart(fig_rank, use_container_width=True, theme=None)

# ---------------------------------------------------------------------------
# VIEW 2: Geospatial Point Map
# ---------------------------------------------------------------------------
elif active_nav == "🗺️ Geospatial Point Map":
    st.markdown("### Spatial Distribution of Listings & Urban Air Quality")
    st.caption("Each point represents a listing, color-coded by AQI tier with pixel-clamped density bounds.")

    map_df = df.dropna(subset=["latitude", "longitude"]).copy()

    def get_color(aqi_val):
        if aqi_val <= 50:
            return [34, 197, 94, 210]    # Green #22c55e
        elif aqi_val <= 100:
            return [234, 179, 8, 210]    # Yellow #eab308
        elif aqi_val <= 150:
            return [249, 115, 22, 210]   # Orange #f97316
        else:
            return [239, 68, 68, 210]    # Red #ef4444

    map_df["color"] = map_df["aqi"].apply(get_color)

    is_city_view = (selected_city != "All Cities (Global View)")
    lat_center = float(map_df["latitude"].mean()) if not map_df.empty else 20.0
    lon_center = float(map_df["longitude"].mean()) if not map_df.empty else 0.0
    zoom_level = 11.5 if is_city_view else 1.8

    view_state = pdk.ViewState(
        latitude=lat_center,
        longitude=lon_center,
        zoom=zoom_level,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius=30 if is_city_view else 500,
        radius_min_pixels=3 if not is_city_view else 4,
        radius_max_pixels=6 if not is_city_view else 10,
        stroked=True,
        get_line_color=[255, 255, 255, 140] if is_dark else [40, 40, 40, 160],
        get_line_width=1,
        pickable=True,
    )

    current_map_style = pdk.map_styles.CARTO_DARK if is_dark else pdk.map_styles.CARTO_LIGHT
    tooltip_bg = "#191c21" if is_dark else "#ffffff"
    tooltip_color = "#ffffff" if is_dark else "#0f172a"
    tooltip_border = "1px solid #2a2f38" if is_dark else "1px solid #cbd5e1"

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style=current_map_style,
            tooltip={
                "html": "<b>City:</b> {city}<br/>"
                        "<b>Neighbourhood:</b> {neighbourhood}<br/>"
                        "<b>Room:</b> {room_type}<br/>"
                        "<b>Price:</b> ₹{price_inr}<br/>"
                        "<b>AQI:</b> {aqi} ({aqi_category})",
                "style": {
                    "backgroundColor": tooltip_bg,
                    "color": tooltip_color,
                    "fontSize": "12px",
                    "padding": "8px 12px",
                    "borderRadius": "6px",
                    "border": tooltip_border,
                },
            },
        )
    )

    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.markdown("🟢 **Good (AQI ≤ 50)**")
    col_l2.markdown("🟡 **Moderate (AQI 51–100)**")
    col_l3.markdown("🟠 **Unhealthy for SG (101–150)**")
    col_l4.markdown("🔴 **Hazardous (151+)**")

# ---------------------------------------------------------------------------
# VIEW 3: Room Types & Housing
# ---------------------------------------------------------------------------
elif active_nav == "🏠 Room Types & Tariffs":
    st.markdown("### Lodging Classification & Residential Impact")
    col_r1, col_r2 = st.columns([1.1, 1.0])
    with col_r1:
        st.markdown(
            '<div class="chart-header"><span>Mean Nightly Price by Room Type</span>'
            '<span class="chart-subcaption">Top 10 Cities</span></div>',
            unsafe_allow_html=True,
        )
        fig_room = plot_room_type_interactive(df, template=plotly_template)
        st.plotly_chart(fig_room, use_container_width=True, theme=None)

    with col_r2:
        st.markdown(
            '<div class="chart-header"><span>Nightly Price Distribution by City</span>'
            '<span class="chart-subcaption">Median-ranked Boxplots</span></div>',
            unsafe_allow_html=True,
        )
        fig_box = plot_city_price_boxplot_interactive(df, template=plotly_template)
        st.plotly_chart(fig_box, use_container_width=True, theme=None)

    if selected_city != "All Cities (Global View)":
        st.markdown(f"#### Neighbourhood Pricing in {selected_city}")
        fig_neigh = plot_neighbourhood_price(df, selected_city)
        st.pyplot(fig_neigh)

# ---------------------------------------------------------------------------
# VIEW 4: Econometric Regressions
# ---------------------------------------------------------------------------
elif active_nav == "📈 Econometric Regressions":
    st.markdown("### Multivariate OLS Modeling & Feature Interdependencies")
    c_s1, c_s2 = st.columns([1.0, 1.2])
    with c_s1:
        st.markdown(
            '<div class="chart-header"><span>Feature Correlation Matrix</span>'
            '<span class="chart-subcaption">Pearson Coefficients</span></div>',
            unsafe_allow_html=True,
        )
        fig_corr = plot_correlation_heatmap_interactive(df, template=plotly_template)
        st.plotly_chart(fig_corr, use_container_width=True, theme=None)

    with c_s2:
        st.markdown(
            '<div class="chart-header"><span>Ordinary Least Squares (OLS) Summary</span>'
            '<span class="chart-subcaption">Multivariate Estimation</span></div>',
            unsafe_allow_html=True,
        )
        desired_x = [
            "aqi", "minimum_nights", "availability_365",
            "number_of_reviews", "review_scores_rating",
        ]
        available_x = [c for c in desired_x if c in df.columns]
        ols_df = df[["price_inr"] + available_x].dropna()

        if len(ols_df) >= 15 and available_x:
            y = ols_df["price_inr"]
            X = sm.add_constant(ols_df[available_x])
            try:
                ols_model = sm.OLS(y, X).fit()
                ols_text = ols_model.summary().as_text()
                r2_val = ols_model.rsquared
                f_pval = ols_model.f_pvalue

                st.markdown(
                    f"""
                    <div style="background-color:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:12px; margin-bottom:10px;">
                        <b>R-squared:</b> <code>{r2_val:.4f}</code> &nbsp;|&nbsp; 
                        <b>F-statistic p-value:</b> <code>{f_pval:.3e}</code> &nbsp;|&nbsp; 
                        <b>Observations:</b> <code>{int(ols_model.nobs):,}</code>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.code(ols_text, language="text")
            except Exception as e:
                st.error(f"Regression calculation error: {e}")
        else:
            st.info("Insufficient data points in current filter range for OLS estimation.")

    # Two perfectly aligned interactive Plotly charts
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        st.markdown(
            '<div class="chart-header"><span>Nightly Price Distribution Across AQI Tiers</span>'
            '<span class="chart-subcaption">Histogram & Marginal Boxplot</span></div>',
            unsafe_allow_html=True,
        )
        fig_dist = plot_price_distribution_interactive(df, template=plotly_template)
        st.plotly_chart(fig_dist, use_container_width=True, theme=None)

    with c_d2:
        st.markdown(
            '<div class="chart-header"><span>Availability (365 Days) vs. Price Elasticity</span>'
            '<span class="chart-subcaption">Supply Saturation & OLS Trend</span></div>',
            unsafe_allow_html=True,
        )
        fig_avail = plot_availability_vs_price_interactive(df, template=plotly_template)
        st.plotly_chart(fig_avail, use_container_width=True, theme=None)

# ---------------------------------------------------------------------------
# VIEW 5: City Comparison
# ---------------------------------------------------------------------------
elif active_nav == "⚖️ City Comparison":
    st.markdown("### Head-to-Head City Comparison Module")
    all_cities = sorted(df_raw["city"].dropna().unique().tolist())
    
    col_a, col_b = st.columns(2)
    with col_a:
        def_a = "Delhi" if "Delhi" in all_cities else all_cities[0]
        city_a = st.selectbox("Select City A", all_cities, index=all_cities.index(def_a))
    with col_b:
        def_b = "London" if "London" in all_cities else all_cities[-1]
        city_b = st.selectbox("Select City B", all_cities, index=all_cities.index(def_b))

    df_a = df_raw[df_raw["city"] == city_a].copy()
    df_b = df_raw[df_raw["city"] == city_b].copy()

    col_stat_a, col_stat_b = st.columns(2)
    with col_stat_a:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <h3 style="color:var(--text-title); margin-top:0;">{city_a}</h3>
                <p style="color:var(--text-body);"><b>Mean AQI:</b> {df_a['aqi'].mean():.1f} | <b>Median Nightly:</b> ₹{df_a['price_inr'].median():,.0f} | <b>Clean Air:</b> {(df_a['aqi'] <= 50).mean()*100:.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_stat_b:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <h3 style="color:var(--text-title); margin-top:0;">{city_b}</h3>
                <p style="color:var(--text-body);"><b>Mean AQI:</b> {df_b['aqi'].mean():.1f} | <b>Median Nightly:</b> ₹{df_b['price_inr'].median():,.0f} | <b>Clean Air:</b> {(df_b['aqi'] <= 50).mean()*100:.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 🏆 Top-Rated Airbnb Stays in Clean Air Zones (AQI ≤ 50)")
    c_tbl_a, c_tbl_b = st.columns(2)
    with c_tbl_a:
        st.markdown(f"**Best Stays in {city_a}**")
        clean_a = df_a[df_a["aqi"] <= 50]
        if clean_a.empty:
            clean_a = df_a.sort_values("aqi").head(20)
        top_a = clean_a.sort_values(by=["review_scores_rating", "number_of_reviews", "price_inr"], ascending=[False, False, True]).head(5)
        st.dataframe(
            top_a[["neighbourhood", "room_type", "price_inr", "aqi", "review_scores_rating", "number_of_reviews"]],
            column_config={
                "neighbourhood": "Neighbourhood",
                "room_type": "Room",
                "price_inr": st.column_config.NumberColumn("Price (₹)", format="₹%d"),
                "aqi": st.column_config.NumberColumn("AQI", format="%d"),
                "review_scores_rating": st.column_config.NumberColumn("Rating", format="%.2f ⭐"),
                "number_of_reviews": "Reviews",
            },
            hide_index=True,
            use_container_width=True,
        )

    with c_tbl_b:
        st.markdown(f"**Best Stays in {city_b}**")
        clean_b = df_b[df_b["aqi"] <= 50]
        if clean_b.empty:
            clean_b = df_b.sort_values("aqi").head(20)
        top_b = clean_b.sort_values(by=["review_scores_rating", "number_of_reviews", "price_inr"], ascending=[False, False, True]).head(5)
        st.dataframe(
            top_b[["neighbourhood", "room_type", "price_inr", "aqi", "review_scores_rating", "number_of_reviews"]],
            column_config={
                "neighbourhood": "Neighbourhood",
                "room_type": "Room",
                "price_inr": st.column_config.NumberColumn("Price (₹)", format="₹%d"),
                "aqi": st.column_config.NumberColumn("AQI", format="%d"),
                "review_scores_rating": st.column_config.NumberColumn("Rating", format="%.2f ⭐"),
                "number_of_reviews": "Reviews",
            },
            hide_index=True,
            use_container_width=True,
        )

# ---------------------------------------------------------------------------
# VIEW 6: Data & Sources
# ---------------------------------------------------------------------------
elif active_nav == "📋 Data & Sources":
    st.markdown("### Raw Sample Explorer & Data Dictionary")
    st.caption("Standardized to Indian Rupees (INR) using baseline exchange rates (Jan 2024 peg).")

    st.dataframe(
        df[["city", "neighbourhood", "room_type", "price", "price_inr", "aqi", "aqi_category", "number_of_reviews", "review_scores_rating"]].head(100),
        use_container_width=True,
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_bytes,
        file_name="clean_air_airbnb_filtered.csv",
        mime="text/csv",
    )
