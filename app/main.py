"""
Paying for Clean Air? Airbnb pricing and urban air quality.
Streamlit dashboard. Run with:  streamlit run app/main.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import pydeck as pdk
import streamlit as st

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))

import live_aqi_service  # noqa: E402
import ui  # noqa: E402
from interactive_viz import (  # noqa: E402
    AQI_BANDS,
    archetype_colors,
    aqi_band,
    plot_aqi_city_ranking_interactive,
    plot_availability_vs_price_interactive,
    plot_city_price_boxplot_interactive,
    plot_cluster_comparison_bar,
    plot_correlation_heatmap_interactive,
    plot_feature_importance_interactive,
    plot_kmeans_3d_clusters_interactive,
    plot_neighbourhood_price,
    plot_price_distribution_interactive,
    plot_price_vs_aqi_interactive,
    plot_room_type_by_city,
    plot_room_type_interactive,
    regression_summary,
    within_city_aqi_summary,
)

st.set_page_config(
    page_title="Paying for Clean Air?",
    page_icon=":material/air:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.session_state.setdefault("dark_mode", False)
ui.inject_css(dark=st.session_state["dark_mode"])

ALL = "All cities"
DATA_PATH = ROOT / "data" / "processed" / "merged_listings.csv"
CLUSTERED_PATH = ROOT / "data" / "processed" / "clustered_listings.csv"
MODELS_DIR = ROOT / "models"


def chart(fig) -> None:
    dark = st.session_state["dark_mode"]
    fig.update_layout(template="plotly_dark" if dark else "plotly_white")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#ECEAE4" if dark else "#0F172A",
            family="Geist, -apple-system, BlinkMacSystemFont, sans-serif",
        ),
        margin=dict(l=10, r=12, t=36 if fig.layout.showlegend else 14, b=10),
    )
    if not dark:
        fig.update_xaxes(
            gridcolor="rgba(0,0,0,0.06)",
            zerolinecolor="rgba(0,0,0,0.12)",
            tickfont=dict(color="#475569"),
            title_font=dict(color="#0F172A"),
        )
        fig.update_yaxes(
            gridcolor="rgba(0,0,0,0.06)",
            zerolinecolor="rgba(0,0,0,0.12)",
            tickfont=dict(color="#475569"),
            title_font=dict(color="#0F172A"),
        )
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                font_color="#0F172A",
                bordercolor="#E2E8F0",
                font_size=12,
            ),
        )
    if hasattr(fig.layout, "scene") and fig.layout.scene is not None:
        grid_col = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.08)"
        bg_col = "rgba(0,0,0,0)"
        fig.update_layout(
            scene=dict(
                xaxis=dict(gridcolor=grid_col, backgroundcolor=bg_col),
                yaxis=dict(gridcolor=grid_col, backgroundcolor=bg_col),
                zaxis=dict(gridcolor=grid_col, backgroundcolor=bg_col),
            )
        )
    st.plotly_chart(fig, width="stretch", theme=None, config={"displaylogo": False})


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading listings…")
def load_data() -> pd.DataFrame | None:
    if not DATA_PATH.exists():
        return None
    df = pd.read_csv(DATA_PATH)
    for col in ("aqi", "price_inr", "latitude", "longitude"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # ~6% of rows have an AQI value but no category label; derive it from the value.
    df["aqi_category"] = df["aqi_category"].fillna(df["aqi"].map(lambda v: aqi_band(v)[0] if pd.notna(v) else None))
    return df


@st.cache_resource(show_spinner="Loading models…")
def load_models():
    model_path = MODELS_DIR / "xgboost_price_pipeline.joblib"
    metrics_path = MODELS_DIR / "xgboost_metrics.json"
    model = joblib.load(model_path) if model_path.exists() else None
    metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else None
    return model, metrics


@st.cache_data(show_spinner=False)
def load_clusters() -> pd.DataFrame | None:
    return pd.read_csv(CLUSTERED_PATH) if CLUSTERED_PATH.exists() else None


@st.cache_data(ttl=900, show_spinner=False)
def live_aqi(city: str):
    live_aqi_service._LIVE_CACHE.pop(city, None)  # the service caches forever; we refresh every 15 min
    return live_aqi_service.fetch_live_aqi_for_city(city)


df_raw = load_data()
if df_raw is None:
    st.error(f"Dataset not found at `{DATA_PATH.relative_to(ROOT)}`. Run `python scripts/data_merger.py` first.", icon=":material/error:")
    st.stop()

CITIES = sorted(df_raw["city"].dropna().unique().tolist())
ROOM_TYPES = sorted(df_raw["room_type"].dropna().unique().tolist())
AQI_MAX = int(df_raw["aqi"].max())
PRICE_MAX = int(df_raw["price_inr"].max() // 500 + 1) * 500
DEFAULTS = {"f_city": ALL, "f_rooms": ROOM_TYPES, "f_aqi": (0, AQI_MAX), "f_price": (0, PRICE_MAX)}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reset_filters() -> None:
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Sidebar: brand + filters (shared by every page)
# ---------------------------------------------------------------------------
with st.sidebar:
    ui.brand()
    st.toggle("Dark mode", key="dark_mode", help="Switch the dashboard between light and dark themes.")
    st.selectbox("City", [ALL] + CITIES, key="f_city")
    st.pills("Room type", ROOM_TYPES, selection_mode="multi", key="f_rooms")
    st.slider("AQI", 0, AQI_MAX, key="f_aqi", help="US EPA scale: 0–50 good, 51–100 moderate, 101+ unhealthy for some or all.")
    st.slider("Nightly price (₹)", 0, PRICE_MAX, step=500, key="f_price", format="₹%d")
    st.button("Reset filters", icon=":material/restart_alt:", on_click=reset_filters, width="stretch",
              disabled=all(st.session_state[k] == v for k, v in DEFAULTS.items()))

city = st.session_state["f_city"]
rooms = st.session_state["f_rooms"] or ROOM_TYPES  # nothing selected means no room filter
lo_aqi, hi_aqi = st.session_state["f_aqi"]
lo_price, hi_price = st.session_state["f_price"]

df = df_raw
if city != ALL:
    df = df[df["city"] == city]
df = df[
    df["room_type"].isin(rooms)
    & df["aqi"].between(lo_aqi, hi_aqi)
    & df["price_inr"].between(lo_price, hi_price)
]
scope = "Global view · 45 cities" if city == ALL else city


def require_rows() -> bool:
    if df.empty:
        with st.container(border=True):
            st.markdown("**No listings match these filters.**")
            st.caption("Widen the AQI or price range, or pick another city.")
            st.button("Reset filters", on_click=reset_filters, key="reset_empty", icon=":material/restart_alt:")
        return False
    return True


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def overview() -> None:
    ui.page_header(
        scope,
        "Is clean air priced in?" if city == ALL else f"Clean air and prices in {city}",
        "Short-term rental prices set against the air quality around each listing. "
        "Use the filters on the left to narrow the market; every number on this page updates with them.",
    )
    if not require_rows():
        return

    band, _ = aqi_band(df["aqi"].mean())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Listings", f"{len(df):,}", border=True, help="Listings matching the current filters.")
    c2.metric("Median nightly price", f"₹{df['price_inr'].median():,.0f}", border=True)
    c3.metric("Mean AQI", f"{df['aqi'].mean():.1f}", band, delta_color="off", delta_arrow="off", border=True)
    c4.metric("Clean-air share", f"{(df['aqi'] <= 50).mean() * 100:.1f}%", "of listings at AQI ≤ 50", delta_color="off", delta_arrow="off", border=True)

    fit = regression_summary(df)
    if fit:
        per10 = fit["slope"] * 10
        direction = "lower" if per10 < 0 else "higher"
        sig = "statistically significant" if fit["p"] < 0.05 else "not statistically significant"
        p_text = "< 0.001" if fit["p"] < 0.001 else f"= {fit['p']:.3f}"
        ui.finding(
            "Pooled association",
            f"Every 10 extra AQI points goes with a nightly price about <b>₹{abs(per10):,.0f} {direction}</b>.",
            f"Linear fit over {fit['n']:,} listings · r = {fit['r']:.2f} · {sig} (p {p_text}). "
            "This pooled comparison mixes within-city patterns with differences between cities; it is not causal.",
        )

    within, city_estimates = within_city_aqi_summary(df)
    with st.container(border=True):
        st.subheader("Comparing listings within cities")
        st.caption(
            "This comparison subtracts each city's average AQI and price first. "
            "It asks whether listings with higher-than-usual AQI in their own city also have higher or lower-than-usual prices."
        )
        if within is not None:
            per10 = within["slope_per_10_aqi"]
            direction = "lower" if per10 < 0 else "higher"
            st.metric(
                "Within-city price difference per 10 AQI points",
                f"₹{abs(per10):,.0f} {direction}",
                help="Descriptive pooled slope after removing each city's average. This is an association, not a causal effect.",
            )
            st.caption(
                f"Uses {within['listings']:,} listings across {within['cities']} cities with AQI variation. "
                "Unlike the pooled result above, between-city price levels do not determine this slope."
            )
        else:
            st.info("There is not enough variation across multiple cities in the current filtered data for a pooled within-city comparison.")
        if not city_estimates.empty:
            st.markdown("**Per-city estimates**")
            shown = city_estimates.copy()
            shown["Price difference per 10 AQI points (₹)"] = shown.pop("slope_per_10_aqi").map(lambda v: f"{v:+,.0f}")
            shown = shown.rename(columns={"city": "City", "listings": "Listings"})
            st.dataframe(shown, hide_index=True, width="stretch")
        st.caption(
            "City estimates are shown only where at least three listings and two distinct AQI values are available. "
            "These simple comparisons do not control for room type, neighborhood, or other listing differences."
        )

    if city != ALL:
        live = live_aqi(city)
        if live and live.get("us_aqi") is not None:
            lband, _ = aqi_band(live["us_aqi"])
            with st.container(border=True):
                l1, l2, l3 = st.columns([1, 1, 2])
                l1.metric("Live AQI now", live["us_aqi"], lband, delta_color="off", delta_arrow="off")
                l2.metric("PM2.5", f"{live.get('pm2_5', '—')} µg/m³")
                l3.caption(f"Current reading for {city} from the Open-Meteo Air Quality API ({live.get('time', '')}). "
                           "The dataset AQI above is the historical value attached to each listing.")

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.subheader("Price against air quality")
        st.caption("Each dot is a listing, coloured by AQI band. Dashed line: linear fit.")
        chart(plot_price_vs_aqi_interactive(df))
    with right:
        st.subheader("Mean AQI by city")
        st.caption("Cleanest at the top." + ("" if city == ALL else f" {city} highlighted; filters other than city apply."))
        ranking_df = df_raw[df_raw["room_type"].isin(rooms)] if city != ALL else df
        chart(plot_aqi_city_ranking_interactive(ranking_df, highlight=None if city == ALL else city))


def map_page() -> None:
    ui.page_header(scope, "Where the listings are", "Each point is a listing, coloured by its AQI band. "
                   "In 3D, column height is the nightly price. Hover for details; right-drag to tilt and rotate.")
    if not require_rows():
        return

    mode = st.segmented_control("View", ["2D points", "3D price columns"], default="2D points", label_visibility="collapsed")
    is_3d = mode == "3D price columns"
    m = df.dropna(subset=["latitude", "longitude"]).copy()
    if len(m) > 6000:  # ponytail: sample to keep WebGL smooth in the global view
        m = m.sample(6000, random_state=42)

    def rgba(v):
        h = aqi_band(v)[1].lstrip("#")
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [215]

    m["color"] = m["aqi"].map(rgba)
    m["price_label"] = m["price_inr"].map(lambda v: f"₹{v:,.0f}" if pd.notna(v) else "—")
    m["aqi_label"] = m["aqi"].map(lambda v: f"{v:.0f}" if pd.notna(v) else "—")

    city_view = city != ALL
    view = pdk.ViewState(
        latitude=float(m["latitude"].mean()) if city_view else 25.0,
        longitude=float(m["longitude"].mean()) if city_view else 10.0,
        zoom=11 if city_view else 1.3,
        pitch=50 if is_3d else 0,
        bearing=-15 if is_3d else 0,
    )
    if is_3d:
        layer = pdk.Layer("ColumnLayer", data=m, get_position=["longitude", "latitude"], get_elevation="price_inr",
                          elevation_scale=0.08 if city_view else 12.0, radius=45 if city_view else 35000,
                          get_fill_color="color", extruded=True, pickable=True, auto_highlight=True)
    else:
        layer = pdk.Layer("ScatterplotLayer", data=m, get_position=["longitude", "latitude"], get_fill_color="color",
                          get_radius=40 if city_view else 600, radius_min_pixels=2.5, radius_max_pixels=9,
                          stroked=False, pickable=True, auto_highlight=True)

    dark = st.session_state["dark_mode"]
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_style=pdk.map_styles.CARTO_DARK if dark else pdk.map_styles.CARTO_LIGHT,
            tooltip={
                "html": "<b>{neighbourhood}, {city}</b><br/>{room_type}<br/>{price_label} / night · AQI {aqi_label} ({aqi_category})",
                "style": {"fontFamily": "Geist, sans-serif", "fontSize": "12px", "padding": "8px 12px", "borderRadius": "8px",
                          "backgroundColor": "#1E1D1B" if dark else "#FFFFFF", "color": "#ECEAE4" if dark else "#0F172A",
                          "border": "1px solid #302E2A" if dark else "1px solid #E2E8F0", "boxShadow": "0 4px 14px rgba(0,0,0,0.12)"},
            },
        ),
        height=560,
    )
    ui.aqi_legend()
    if len(m) < len(df):
        st.caption(f"Showing a random sample of {len(m):,} of {len(df):,} listings for smooth rendering.")


def rooms_page() -> None:
    ui.page_header(scope, "Room types and prices", "How the kind of stay shapes the nightly rate, and how widely prices vary within each city.")
    if not require_rows():
        return
    left, right = st.columns([1, 1.2], gap="large")
    with left:
        st.subheader("Median price by room type")
        chart(plot_room_type_interactive(df))
        if city == ALL:
            st.subheader("Room types in the largest markets")
            st.caption("The eight cities with the most listings.")
            chart(plot_room_type_by_city(df))
        else:
            st.subheader(f"Neighbourhoods in {city}")
            st.caption("Top 15 by median price; bar colour is the area's mean AQI.")
            chart(plot_neighbourhood_price(df, city))
    with right:
        st.subheader("Price spread by city")
        st.caption("Box shows the middle 50% of listings; ordered by median price.")
        chart(plot_city_price_boxplot_interactive(df))


def drivers_page() -> None:
    ui.page_header(scope, "What moves the price", "Relationships between price, air quality and listing features in the filtered data.")
    if not require_rows():
        return
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Correlations")
        st.caption("Pearson r between numeric features. Blue is positive, red negative.")
        chart(plot_correlation_heatmap_interactive(df))
    with right:
        st.subheader("Availability against price")
        st.caption("Days a listing is bookable per year, by room type. Dashed line: linear fit.")
        chart(plot_availability_vs_price_interactive(df))
    st.subheader("Price distribution by AQI band")
    st.caption("Overlapping histograms; where bands shift right, cleaner or dirtier air coincides with higher prices.")
    chart(plot_price_distribution_interactive(df))


def summarise(d: pd.DataFrame) -> dict:
    return {
        "aqi": d["aqi"].mean(),
        "price": d["price_inr"].median(),
        "clean": (d["aqi"] <= 50).mean() * 100,
        "entire": (d["room_type"] == "Entire home/apt").mean() * 100,
        "n": len(d),
    }


def swap_cities() -> None:
    st.session_state["cmp_a"], st.session_state["cmp_b"] = st.session_state["cmp_b"], st.session_state["cmp_a"]


def compare_page() -> None:
    ui.page_header("Head to head", "Compare two cities", "Air quality, prices and the best-rated clean-air stays, side by side. "
                   "Uses all listings in each city; sidebar filters don't apply here.")
    st.session_state.setdefault("cmp_a", "Delhi" if "Delhi" in CITIES else CITIES[0])
    st.session_state.setdefault("cmp_b", "London" if "London" in CITIES else CITIES[-1])

    a_col, swap_col, b_col = st.columns([1, 0.12, 1], vertical_alignment="bottom")
    a_col.selectbox("City A", CITIES, key="cmp_a")
    swap_col.button("", icon=":material/swap_horiz:", on_click=swap_cities, help="Swap cities", width="stretch")
    b_col.selectbox("City B", CITIES, key="cmp_b")

    names = [st.session_state["cmp_a"], st.session_state["cmp_b"]]
    data = [df_raw[df_raw["city"] == n] for n in names]
    sums = [summarise(d) for d in data]

    for i, col in enumerate(st.columns(2, gap="large")):
        s, o = sums[i], sums[1 - i]
        with col:
            st.subheader(names[i])
            m1, m2, m3 = st.columns(3)
            m1.metric("Mean AQI", f"{s['aqi']:.1f}", f"{s['aqi'] - o['aqi']:+.1f} vs {names[1 - i]}", delta_color="inverse", border=True)
            m2.metric("Median price", f"₹{s['price']:,.0f}", f"{(s['price'] / o['price'] - 1) * 100:+.0f}%", delta_color="off", border=True)
            m3.metric("Clean-air share", f"{s['clean']:.0f}%", f"{s['clean'] - o['clean']:+.0f} pts", border=True)

            d = data[i]
            clean = d[d["aqi"] <= 50]
            pool = clean if not clean.empty else d.nsmallest(20, "aqi")
            top = pool.sort_values(["review_scores_rating", "number_of_reviews", "price_inr"], ascending=[False, False, True]).head(5)
            st.markdown("**Top-rated clean-air stays**" if not clean.empty else "**Top-rated stays with the lowest AQI**")
            st.dataframe(
                top[["neighbourhood", "room_type", "price_inr", "aqi", "review_scores_rating", "number_of_reviews"]],
                column_config={
                    "neighbourhood": "Neighbourhood",
                    "room_type": "Room",
                    "price_inr": st.column_config.NumberColumn("Price", format="₹%,d"),
                    "aqi": st.column_config.NumberColumn("AQI", format="%d"),
                    "review_scores_rating": st.column_config.NumberColumn("Rating", format="%.2f"),
                    "number_of_reviews": st.column_config.NumberColumn("Reviews", format="%d"),
                },
                hide_index=True,
                width="stretch",
            )


ARCHETYPE_NOTES = {
    "Eco-Luxury": "Clean air bundled with premium entire homes; the highest rates in the market.",
    "Urban Budget": "Highest pollution exposure, priced well below the clean-air segments.",
    "Balanced": "The core urban market: moderate prices and air within the 'good' band.",
    "Standard": "Highly available calendars, typical of professional multi-listing hosts.",
}


def models_page() -> None:
    ui.page_header("Machine learning", "Predicting price, finding segments",
                   "A gradient-boosted model estimates nightly price from listing features, and K-Means groups listings into market segments.")
    model, metrics = load_models()

    tab_pred, tab_seg = st.tabs([":material/query_stats: Price model", ":material/scatter_plot: Market segments"])

    with tab_pred:
        if metrics:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Test R²", f"{metrics['r2_test']:.3f}", f"train {metrics['r2_train']:.3f}", delta_color="off", delta_arrow="off", border=True,
                      help="Share of price variance explained on held-out listings.")
            k2.metric("Test RMSE", f"₹{metrics['rmse_test']:,.0f}", border=True)
            k3.metric("Test MAE", f"₹{metrics['mae_test']:,.0f}", border=True)
            k4.metric("Model", "XGBoost", "250 trees, depth 6", delta_color="off", delta_arrow="off", border=True)
        else:
            st.info("Model metrics not found. Run `python scripts/ml_pipeline.py` to train the model.", icon=":material/info:")

        left, right = st.columns([1, 1.1], gap="large")
        with left:
            st.subheader("What the model relies on")
            if metrics and "feature_importances" in metrics:
                st.caption("Log scale: city dominates, so the smaller drivers would otherwise be invisible.")
                chart(plot_feature_importance_interactive(metrics["feature_importances"]))
                imp = metrics["feature_importances"]
                st.markdown(
                    f"Location explains almost everything (**{imp.get('city', 0):.1f}%**): a Zurich listing and a Mumbai listing "
                    f"differ far more than any amenity can. Among the rest, room type ({imp.get('room_type', 0):.2f}%) and "
                    f"AQI ({imp.get('aqi', 0):.2f}%) carry the most weight."
                )
        with right:
            st.subheader("What-if simulator")
            st.caption("Change a listing's details and air quality to see the predicted rate move.")
            with st.container(border=True):
                s1, s2 = st.columns(2)
                sim_city = s1.selectbox("City", CITIES, index=CITIES.index("Paris") if "Paris" in CITIES else 0, key="sim_city")
                sim_room = s2.selectbox("Room type", ROOM_TYPES, index=ROOM_TYPES.index("Entire home/apt") if "Entire home/apt" in ROOM_TYPES else 0, key="sim_room")
                s3, s4 = st.columns(2)
                sim_rating = s3.slider("Guest rating", 3.0, 5.0, 4.85, 0.05, key="sim_rating")
                sim_avail = s4.slider("Days available / year", 1, 365, 180, 5, key="sim_avail")
                s5, s6 = st.columns(2)
                sim_nights = s5.number_input("Minimum stay (nights)", 1, 30, 2, key="sim_nights")
                sim_reviews = s6.number_input("Review count", 0, 500, 45, key="sim_reviews")
                sim_aqi = st.slider("Air quality (AQI)", 0, 250, 45, 5, key="sim_aqi", help="The variable under test. Baseline is pristine air, AQI 25.")

            if model is None:
                st.warning("Model file not found. Run `python scripts/ml_pipeline.py` to train it.", icon=":material/warning:")
            else:
                row = pd.DataFrame([{
                    "city": sim_city, "room_type": sim_room, "minimum_nights": sim_nights, "availability_365": sim_avail,
                    "number_of_reviews": sim_reviews, "review_scores_rating": sim_rating, "aqi": sim_aqi,
                }])
                pred = float(model.predict(row)[0])
                base = float(model.predict(row.assign(aqi=25))[0])
                delta = pred - base
                pct = delta / base * 100 if base else 0
                p1, p2 = st.columns(2)
                p1.metric("Predicted nightly rate", f"₹{pred:,.0f}", border=True)
                p2.metric("vs. pristine air (AQI 25)", f"{delta:+,.0f} ₹", f"{pct:+.1f}%", border=True)

    with tab_seg:
        clusters = load_clusters()
        if clusters is None or "archetype" not in clusters:
            st.info("Cluster data not found. Run `python scripts/ml_pipeline.py` to build it.", icon=":material/info:")
            return
        profile = (
            clusters.groupby("archetype", as_index=False)
            .agg(price_inr=("price_inr", "mean"), aqi=("aqi", "mean"), rating=("review_scores_rating", "mean"), count=("listing_id", "count"))
            .sort_values("price_inr", ascending=False)
        )
        profile["short_name"] = profile["archetype"].str.replace(r"^Cluster \d+ \(|\s*\(.*\)$|\)$", "", regex=True).str.strip()
        colors = archetype_colors(profile["archetype"].tolist())

        st.subheader("Listings in price × AQI × rating space")
        st.caption(f"K-Means with k = {len(profile)} over {len(clusters):,} listings (2,500 shown). Drag to rotate.")
        chart(plot_kmeans_3d_clusters_interactive(clusters))

        left, right = st.columns([1.1, 1], gap="large")
        with left:
            st.subheader("Segments compared")
            chart(plot_cluster_comparison_bar(profile))
        with right:
            st.subheader("The four segments")
            for _, r in profile.iterrows():
                note = next((v for k, v in ARCHETYPE_NOTES.items() if k in r["archetype"]), "")
                ui.archetype_card(
                    r["short_name"],
                    colors[r["archetype"]],
                    [f"₹{r['price_inr']:,.0f} avg", f"AQI {r['aqi']:.1f}", f"{r['rating']:.2f} rating", f"{r['count']:,} listings"],
                    note,
                )


def data_page() -> None:
    ui.page_header(scope, "The data", "Every listing matching the current filters. Click a column header to sort; download the filtered set as CSV.")
    if not require_rows():
        return
    cols = ["city", "neighbourhood", "room_type", "price", "price_inr", "aqi", "aqi_category", "review_scores_rating", "number_of_reviews", "availability_365", "minimum_nights"]
    st.dataframe(
        df[cols],
        column_config={
            "city": "City",
            "neighbourhood": "Neighbourhood",
            "room_type": "Room",
            "price": st.column_config.NumberColumn("Local price", format="%.2f", help="Price in the listing's local currency."),
            "price_inr": st.column_config.NumberColumn("Price (₹)", format="₹%,d"),
            "aqi": st.column_config.NumberColumn("AQI", format="%d"),
            "aqi_category": "AQI band",
            "review_scores_rating": st.column_config.NumberColumn("Rating", format="%.2f"),
            "number_of_reviews": st.column_config.NumberColumn("Reviews", format="%d"),
            "availability_365": st.column_config.NumberColumn("Days available", format="%d"),
            "minimum_nights": st.column_config.NumberColumn("Min. nights", format="%d"),
        },
        hide_index=True,
        width="stretch",
        height=560,
    )
    st.download_button(
        f"Download {len(df):,} rows (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="clean_air_listings.csv",
        mime="text/csv",
        icon=":material/download:",
    )
    with st.expander("Data dictionary"):
        st.markdown(
            "- **price_inr**: nightly price converted to Indian rupees at January 2024 rates.\n"
            "- **aqi**: US EPA Air Quality Index attached to the listing's location (0 = cleanest).\n"
            "- **aqi_category**: EPA band for that AQI value.\n"
            "- **review_scores_rating**: average guest rating out of 5.\n"
            "- **availability_365**: days the listing is bookable in the next year."
        )


pages = {
    "Explore": [
        st.Page(overview, title="Overview", icon=":material/insights:", default=True),
        st.Page(map_page, title="Map", icon=":material/map:", url_path="map"),
        st.Page(rooms_page, title="Room types", icon=":material/bed:", url_path="room-types"),
    ],
    "Analyse": [
        st.Page(drivers_page, title="Price drivers", icon=":material/ssid_chart:", url_path="drivers"),
        st.Page(compare_page, title="Compare cities", icon=":material/compare_arrows:", url_path="compare"),
        st.Page(models_page, title="Models", icon=":material/model_training:", url_path="models"),
    ],
    "Data": [st.Page(data_page, title="Data", icon=":material/table_view:", url_path="data")],
}
st.navigation(pages, position="top").run()
ui.footnote()
