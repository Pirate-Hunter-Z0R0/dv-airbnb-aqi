"""
Paying for Clean Air? Airbnb Pricing and Urban Air Quality
Streamlit Dashboard — Inside Airbnb Style Redesign
"""

import sys
import os
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

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
    plot_correlation_heatmap_interactive,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Inside Airbnb | Paying for Clean Air?",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — Inside Airbnb Aesthetic (Theme-Aware / Dark & Light Safe)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Base page styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Responsive light/dark mode CSS tokens */
        :root {
            --card-bg: #f8f9fa;
            --card-border: rgba(0, 0, 0, 0.08);
            --card-text: #1a1a1a;
            --card-sub: #555555;
            --tag-bg: #ffffff;
            --tag-border: #e0e0e0;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --card-bg: #1e232a;
                --card-border: rgba(255, 255, 255, 0.12);
                --card-text: #f3f4f6;
                --card-sub: #9ca3af;
                --tag-bg: #2b313a;
                --tag-border: rgba(255, 255, 255, 0.18);
            }
        }

        /* Top Navigation Header */
        .inside-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 24px;
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            margin-bottom: 24px;
        }
        .inside-logo {
            font-size: 1.5rem;
            font-weight: 800;
            color: #ff385c;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .inside-logo span {
            color: var(--card-text);
            font-weight: 500;
            font-size: 1.05rem;
            border-left: 1px solid var(--card-sub);
            padding-left: 12px;
            margin-left: 4px;
        }
        .header-tag {
            font-size: 0.85rem;
            font-weight: 600;
            background-color: var(--tag-bg);
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid var(--tag-border);
            color: var(--card-text);
        }

        /* Hero Banner */
        .hero-banner {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 28px 32px;
            margin-bottom: 24px;
        }
        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            color: var(--card-text);
            letter-spacing: -0.7px;
            margin-bottom: 8px;
        }
        .hero-sub {
            font-size: 1.0rem;
            color: var(--card-sub);
            max-width: 900px;
            line-height: 1.6;
        }

        /* Big Number Stat Cards */
        .stat-card {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            text-align: left;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }
        .stat-card:hover {
            border-color: rgba(255, 56, 92, 0.4);
        }
        .stat-val {
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--card-text);
            line-height: 1.1;
            margin-bottom: 4px;
        }
        .stat-val.highlight {
            color: #00a699;
        }
        .stat-val.accent {
            color: #ff385c;
        }
        .stat-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--card-sub);
        }
        .stat-note {
            font-size: 0.78rem;
            color: var(--card-sub);
            opacity: 0.8;
            margin-top: 6px;
        }

        /* Section Headings */
        .section-header {
            margin-top: 32px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--card-border);
        }
        .section-header h2 {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--card-text);
            margin: 0;
        }
        .section-header p {
            color: var(--card-sub);
            font-size: 0.92rem;
            margin-top: 4px;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--card-sub);
            border-radius: 0px;
            padding: 8px 16px;
        }
        .stTabs [aria-selected="true"] {
            color: #ff385c !important;
            border-bottom: 3px solid #ff385c !important;
        }

        /* Matplotlib Figure Container */
        [data-testid="stImage"], [data-testid="stPlotlyChart"], [data-testid="stArrowVegaLiteChart"] {
            background-color: transparent !important;
        }

        /* Footer */
        .inside-footer {
            margin-top: 60px;
            padding: 24px 20px;
            border-top: 1px solid var(--card-border);
            background-color: var(--card-bg);
            border-radius: 8px;
            text-align: center;
            color: var(--card-sub);
            font-size: 0.85rem;
            line-height: 1.6;
        }
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
    # Ensure AQI and price are numeric
    df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")
    df["price_inr"] = pd.to_numeric(df["price_inr"], errors="coerce")
    return df


df_raw = load_data()

# ---------------------------------------------------------------------------
# Top Header (Inside Airbnb Style)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="inside-header">
        <div class="inside-logo">
            Inside Airbnb <span>Paying for Clean Air?</span>
        </div>
        <div class="header-tag">
            45 Global Cities · Urban Air Quality & Short-Term Rentals
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# City Selector & Filter Bar
# ---------------------------------------------------------------------------
cities_list = ["All Cities (Global View)"] + sorted(df_raw["city"].dropna().unique().tolist())

col_sel, col_room = st.columns([1.5, 1.5])
with col_sel:
    selected_city = st.selectbox("📍 Select City", cities_list, index=0)

with col_room:
    available_room_types = sorted(df_raw["room_type"].dropna().unique().tolist())
    selected_rooms = st.multiselect("🏠 Room Type", available_room_types, default=available_room_types)

# Expandable / manual input filter section
max_p = int(df_raw["price_inr"].max() if not df_raw["price_inr"].isna().all() else 100000)

col_aqi_min, col_aqi_max, col_price_min, col_price_max = st.columns(4)

with col_aqi_min:
    aqi_min = st.number_input("🌫️ Min AQI", min_value=0, max_value=500, value=0, step=5)
with col_aqi_max:
    aqi_max = st.number_input("🌫️ Max AQI", min_value=0, max_value=500, value=250, step=5)
with col_price_min:
    price_min = st.number_input("💵 Min Price (₹)", min_value=0, max_value=max_p, value=0, step=500)
with col_price_max:
    price_max = st.number_input("💵 Max Price (₹)", min_value=0, max_value=max_p, value=max_p, step=1000)

# Safety check for min > max
if aqi_min > aqi_max:
    aqi_min, aqi_max = aqi_max, aqi_min
if price_min > price_max:
    price_min, price_max = price_max, price_min

# Apply Filters
df = df_raw.copy()

if selected_city != "All Cities (Global View)":
    df = df[df["city"] == selected_city]

if selected_rooms:
    df = df[df["room_type"].isin(selected_rooms)]

df = df[(df["aqi"] >= aqi_min) & (df["aqi"] <= aqi_max)]
df = df[(df["price_inr"] >= price_min) & (df["price_inr"] <= price_max)]

if df.empty:
    st.warning("⚠️ No listings match the selected filters. Please expand your criteria.")
    st.stop()

# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------
display_name = selected_city if selected_city != "All Cities (Global View)" else "45 Global Metropolitan Areas"

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-title">{display_name}</div>
        <div class="hero-sub">
            Investigating how urban air quality (AQI) intersects with short-term rental nightly prices. 
            Do hosts in clean-air zones command a price premium? Explore spatial distributions, room type segmentation, and econometric modeling below.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Big Number Metric Callout Cards
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

total_listings = len(df)
entire_home_pct = (df["room_type"] == "Entire home/apt").mean() * 100
median_price = df["price_inr"].median()
mean_aqi = df["aqi"].mean()
clean_air_pct = (df["aqi"] <= 50).mean() * 100

with col1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Total Listings</div>
            <div class="stat-val accent">{total_listings:,}</div>
            <div class="stat-note">in current view</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Entire Homes</div>
            <div class="stat-val">{entire_home_pct:.1f}%</div>
            <div class="stat-note">residential pressure</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Median Price</div>
            <div class="stat-val highlight">₹{median_price:,.0f}</div>
            <div class="stat-note">per night (INR)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    aqi_color = "#008489" if mean_aqi <= 50 else ("#f1c40f" if mean_aqi <= 100 else "#ff385c")
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Mean AQI</div>
            <div class="stat-val" style="color: {aqi_color};">{mean_aqi:.1f}</div>
            <div class="stat-note">{"Good" if mean_aqi <= 50 else ("Moderate" if mean_aqi <= 100 else "Unhealthy")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Clean Air Ratio</div>
            <div class="stat-val">{clean_air_pct:.1f}%</div>
            <div class="stat-note">listings in AQI ≤ 50</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Section Tabs (Inside Airbnb Exploration)
# ---------------------------------------------------------------------------
tab_map, tab_hypothesis, tab_room, tab_stats, tab_compare, tab_data = st.tabs(
    [
        "🗺️ Spatial Map",
        "🌿 The Clean Air Premium",
        "🏠 Room Types & Housing",
        "📈 Econometrics & Stats",
        "⚖️ City Comparison",
        "📋 Data & Methodology",
    ]
)

# ---------------------------------------------------------------------------
# Tab 1: Spatial Map (Interactive PyDeck Map)
# ---------------------------------------------------------------------------
with tab_map:
    st.markdown(
        """
        <div class="section-header">
            <h2>Spatial Distribution of Listings & Air Quality</h2>
            <p>Each point represents a listing, color-coded by local air quality category. Zoom and pan to inspect geographic density.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    map_df = df.dropna(subset=["latitude", "longitude"]).copy()

    # Color by AQI category
    def get_color(aqi_val):
        if aqi_val <= 50:
            return [46, 204, 113, 180]    # Green
        elif aqi_val <= 100:
            return [241, 196, 15, 180]   # Yellow
        elif aqi_val <= 150:
            return [230, 126, 34, 180]   # Orange
        else:
            return [231, 76, 60, 180]    # Red

    map_df["color"] = map_df["aqi"].apply(get_color)

    # Choose map view center and zoom
    lat_center = float(map_df["latitude"].mean()) if not map_df.empty else 20.0
    lon_center = float(map_df["longitude"].mean()) if not map_df.empty else 0.0
    
    is_city_view = (selected_city != "All Cities (Global View)")
    zoom_level = 11.5 if is_city_view else 1.8

    view_state = pdk.ViewState(
        latitude=lat_center,
        longitude=lon_center,
        zoom=zoom_level,
        pitch=0,
    )

    # Use pixel-based radius scaling so points never collide into huge blobs
    # radius_min_pixels prevents points from vanishing when zoomed out
    # radius_max_pixels prevents points from expanding into large giant discs
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius=30 if is_city_view else 500,
        radius_min_pixels=3 if not is_city_view else 4,
        radius_max_pixels=6 if not is_city_view else 10,
        stroked=True,
        get_line_color=[255, 255, 255, 140],
        get_line_width=1,
        pickable=True,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>City:</b> {city}<br/>"
                        "<b>Neighbourhood:</b> {neighbourhood}<br/>"
                        "<b>Room:</b> {room_type}<br/>"
                        "<b>Nightly Price:</b> ₹{price_inr}<br/>"
                        "<b>AQI:</b> {aqi} ({aqi_category})",
                "style": {"backgroundColor": "#222", "color": "white", "fontSize": "12px", "padding": "8px"},
            },
        )
    )

    # Legend
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.markdown("🟢 **Good (AQI 0–50)**")
    col_l2.markdown("🟡 **Moderate (AQI 51–100)**")
    col_l3.markdown("🟠 **Unhealthy for SG (AQI 101–150)**")
    col_l4.markdown("🔴 **Unhealthy / Hazardous (AQI 151+)**")

# ---------------------------------------------------------------------------
# Tab 2: The Clean Air Premium (Hypothesis Testing)
# ---------------------------------------------------------------------------
with tab_hypothesis:
    st.markdown(
        """
        <div class="section-header">
            <h2>Paying for Clean Air? Price vs. AQI Correlation</h2>
            <p>Testing H₁: Listings situated in cleaner environments command higher reservation rates. Hover over markers for interactive listing inspect.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_left, c_right = st.columns([1.1, 1])
    with c_left:
        fig_scatter_interactive = plot_price_vs_aqi_interactive(df)
        st.plotly_chart(fig_scatter_interactive, use_container_width=True)

    with c_right:
        fig_aqi_rank_interactive = plot_aqi_city_ranking_interactive(df)
        st.plotly_chart(fig_aqi_rank_interactive, use_container_width=True)

    st.markdown(
        """
        <div class="section-header">
            <h2>City-by-City Regression Analysis</h2>
            <p>Evaluating localized sensitivity to air quality across primary hubs.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    fig_facets = plot_aqi_price_regression_by_city(df)
    st.pyplot(fig_facets)

# ---------------------------------------------------------------------------
# Tab 3: Room Types & Housing
# ---------------------------------------------------------------------------
with tab_room:
    st.markdown(
        """
        <div class="section-header">
            <h2>Room Type Breakdown & Residential Impact</h2>
            <p>Inside Airbnb monitors how Entire Homes versus Private Rooms shape urban living costs and availability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        fig_room_interactive = plot_room_type_interactive(df)
        st.plotly_chart(fig_room_interactive, use_container_width=True)
    with c2:
        fig_box_interactive = plot_city_price_boxplot_interactive(df)
        st.plotly_chart(fig_box_interactive, use_container_width=True)

    if selected_city != "All Cities (Global View)":
        st.markdown(
            f"""
            <div class="section-header">
                <h2>Neighbourhood Pricing in {selected_city}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_neigh = plot_neighbourhood_price(df, selected_city)
        st.pyplot(fig_neigh)

# ---------------------------------------------------------------------------
# Tab 4: Econometrics & Stats
# ---------------------------------------------------------------------------
with tab_stats:
    st.markdown(
        """
        <div class="section-header">
            <h2>Multivariate OLS Regression & Feature Correlations</h2>
            <p>Controlling for minimum nights, reviews, ratings, and availability to isolate the true AQI coefficient.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_s1, c_s2 = st.columns([1, 1.2])
    with c_s1:
        fig_corr_interactive = plot_correlation_heatmap_interactive(df)
        st.plotly_chart(fig_corr_interactive, use_container_width=True)

    with c_s2:
        fig_ols = plot_ols_summary_table(df)
        st.pyplot(fig_ols)

    st.markdown(
        """
        <div class="section-header">
            <h2>Price Distribution & Supply Availability</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        fig_dist_interactive = plot_price_distribution_interactive(df)
        st.plotly_chart(fig_dist_interactive, use_container_width=True)
    with c_d2:
        fig_avail = plot_availability_vs_price(df)
        st.pyplot(fig_avail)

# ---------------------------------------------------------------------------
# Tab 5: City Comparison (Best Airbnb with Best Air Quality)
# ---------------------------------------------------------------------------
with tab_compare:
    st.markdown(
        """
        <div class="section-header">
            <h2>Head-to-Head City Comparison</h2>
            <p>Compare Airbnb offerings and urban air quality metrics between any two cities, and uncover top-rated stays in clean-air zones.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_cities = sorted(df_raw["city"].dropna().unique().tolist())
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        default_city_a = "Amsterdam" if "Amsterdam" in all_cities else all_cities[0]
        city_a = st.selectbox("🏙️ City A", all_cities, index=all_cities.index(default_city_a))
    with col_c2:
        default_city_b = "Zurich" if "Zurich" in all_cities else all_cities[-1]
        city_b = st.selectbox("🏙️ City B", all_cities, index=all_cities.index(default_city_b))

    df_a = df_raw[df_raw["city"] == city_a].copy()
    df_b = df_raw[df_raw["city"] == city_b].copy()

    # Metrics comparison
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.markdown(f"### {city_a}")
        m_c1, m_c2, m_c3 = st.columns(3)
        m_c1.metric("Mean AQI", f"{df_a['aqi'].mean():.1f}")
        m_c2.metric("Median Price", f"₹{df_a['price_inr'].median():,.0f}")
        m_c3.metric("Clean Air %", f"{(df_a['aqi'] <= 50).mean()*100:.1f}%")
        
    with stat_col2:
        st.markdown(f"### {city_b}")
        m_b1, m_b2, m_b3 = st.columns(3)
        m_b1.metric("Mean AQI", f"{df_b['aqi'].mean():.1f}")
        m_b2.metric("Median Price", f"₹{df_b['price_inr'].median():,.0f}")
        m_b3.metric("Clean Air %", f"{(df_b['aqi'] <= 50).mean()*100:.1f}%")

    st.markdown("---")
    st.markdown("### 🏆 Top-Rated Airbnb Stays in Clean Air Zones (AQI ≤ 50)")

    col_best_a, col_best_b = st.columns(2)

    with col_best_a:
        st.markdown(f"#### Best Stays in **{city_a}**")
        # Clean air first (AQI <= 50 or lowest AQI), sorted by rating and review count
        clean_a = df_a[df_a["aqi"] <= 50]
        if clean_a.empty:
            clean_a = df_a.sort_values("aqi").head(20)
        
        top_stays_a = clean_a.sort_values(
            by=["review_scores_rating", "number_of_reviews", "price_inr"],
            ascending=[False, False, True],
        ).head(5)

        st.dataframe(
            top_stays_a[["neighbourhood", "room_type", "price_inr", "aqi", "review_scores_rating", "number_of_reviews"]],
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

    with col_best_b:
        st.markdown(f"#### Best Stays in **{city_b}**")
        clean_b = df_b[df_b["aqi"] <= 50]
        if clean_b.empty:
            clean_b = df_b.sort_values("aqi").head(20)

        top_stays_b = clean_b.sort_values(
            by=["review_scores_rating", "number_of_reviews", "price_inr"],
            ascending=[False, False, True],
        ).head(5)

        st.dataframe(
            top_stays_b[["neighbourhood", "room_type", "price_inr", "aqi", "review_scores_rating", "number_of_reviews"]],
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
# Tab 5: Data & Methodology
# ---------------------------------------------------------------------------
with tab_data:
    st.markdown(
        """
        <div class="section-header">
            <h2>Data Dictionary & Raw Sample Explorer</h2>
            <p>All prices converted to Indian Rupees (INR) using baseline exchange rates. Air quality indices sourced and synthesized for 30 cities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        df[["city", "neighbourhood", "room_type", "price", "price_inr", "aqi", "aqi_category", "number_of_reviews", "review_scores_rating"]]
        .head(100),
        use_container_width=True,
    )

    # Download Button
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_bytes,
        file_name="clean_air_airbnb_filtered.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="inside-footer">
        <b>Inside Airbnb: Paying for Clean Air?</b> — University Lab Research Project.<br/>
        Data sourced and modeled across 30 global metropolitan centers. Nightly tariffs standardized to INR (Jan 2024 exchange baseline).<br/>
        Inspired by the non-commercial open data advocacy work of <a href="http://insideairbnb.com" target="_blank" style="color: #ff385c; text-decoration: none; font-weight:600;">Inside Airbnb</a>.
    </div>
    """,
    unsafe_allow_html=True,
)
