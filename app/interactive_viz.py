"""
interactive_viz.py
==================
Plotly figures for the 'Paying for Clean Air?' dashboard.

Figures carry data colours only; backgrounds, fonts and text colours come from the Streamlit
theme (render with ``st.plotly_chart(fig, theme="streamlit")``), so every chart follows light and
dark mode automatically. AQI is always drawn with the single scale defined in ``AQI_BANDS``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# ---------------------------------------------------------------------------
# AQI scale (US EPA bands), shared by charts, the map and the UI.
# ---------------------------------------------------------------------------
AQI_BANDS = [
    # (upper bound, label, colour)
    (50, "Good", "#3E9C5B"),
    (100, "Moderate", "#D9A520"),
    (150, "Unhealthy for Sensitive Groups", "#E07B2E"),
    (200, "Unhealthy", "#C8453A"),
    (300, "Very Unhealthy", "#8456A6"),
    (float("inf"), "Hazardous", "#6E2433"),
]
AQI_COLORS = {label: color for _, label, color in AQI_BANDS}
AQI_ORDER = [label for _, label, _ in AQI_BANDS]
AQI_CONTINUOUS = [[0.0, "#3E9C5B"], [0.25, "#D9A520"], [0.5, "#E07B2E"], [0.75, "#C8453A"], [1.0, "#8456A6"]]

ACCENT = "#1F5F74"
HIGHLIGHT = "#C0603A"


def aqi_band(value: float | None) -> tuple[str, str]:
    """Return (label, colour) for an AQI value; ('No data', grey) for missing values."""
    if value is None or pd.isna(value):
        return "No data", "#8A8780"
    for upper, label, color in AQI_BANDS:
        if value <= upper:
            return label, color
    return AQI_BANDS[-1][1], AQI_BANDS[-1][2]


def _style(fig: go.Figure, height: int = 420, legend: bool = True) -> go.Figure:
    """House style: transparent canvas, quiet grid, top-left legend, compact margins."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=12, t=36 if legend else 12, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text="", bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(font_size=12),
        bargap=0.25,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, ticks="outside", ticklen=4)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    return fig


def _empty(message: str = "No data for the current filters", height: int = 320) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=13), opacity=0.6)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _style(fig, height=height, legend=False)


def regression_summary(df: pd.DataFrame, x: str = "aqi", y: str = "price_inr") -> dict | None:
    """Linear fit of y on x; None when there is too little variation to fit."""
    sub = df[[x, y]].dropna()
    if len(sub) < 3 or sub[x].nunique() < 2:
        return None
    r = stats.linregress(sub[x], sub[y])
    return {"slope": r.slope, "intercept": r.intercept, "r": r.rvalue, "p": r.pvalue, "n": len(sub)}


def within_city_aqi_summary(df: pd.DataFrame) -> tuple[dict | None, pd.DataFrame]:
    """Estimate the pooled AQI-price slope after removing each city's mean.

    City centering compares listings relative to their own city's averages,
    so differences in average prices between cities do not drive the slope.
    Per-city slopes are returned for context; they are descriptive estimates.
    """
    sub = df[["city", "aqi", "price_inr"]].dropna().copy()
    if sub.empty:
        return None, pd.DataFrame(columns=["city", "slope_per_10_aqi", "listings"])

    sub["aqi_centered"] = sub["aqi"] - sub.groupby("city")["aqi"].transform("mean")
    sub["price_centered"] = sub["price_inr"] - sub.groupby("city")["price_inr"].transform("mean")
    usable = sub["aqi_centered"].pow(2).sum()
    if sub["city"].nunique() < 2 or usable == 0:
        pooled = None
    else:
        slope = (sub["aqi_centered"] * sub["price_centered"]).sum() / usable
        pooled = {
            "slope_per_10_aqi": float(slope * 10),
            "listings": int(len(sub)),
            "cities": int(sub.loc[sub["aqi_centered"] != 0, "city"].nunique()),
        }

    city_rows = []
    for city_name, group in sub.groupby("city"):
        if len(group) < 3 or group["aqi"].nunique() < 2:
            continue
        fit = stats.linregress(group["aqi"], group["price_inr"])
        city_rows.append({
            "city": city_name,
            "slope_per_10_aqi": float(fit.slope * 10),
            "listings": int(len(group)),
        })
    estimates = pd.DataFrame(city_rows)
    if not estimates.empty:
        estimates = estimates.sort_values("slope_per_10_aqi")
    return pooled, estimates


def _fit_line(fig: go.Figure, fit: dict, x_min: float, x_max: float, name: str = "Linear fit") -> None:
    xs = np.array([x_min, x_max])
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=fit["intercept"] + fit["slope"] * xs,
            mode="lines",
            name=name,
            line=dict(color="#C8453A", width=2.5, dash="dash"),
            hoverinfo="skip",
        )
    )


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
def plot_price_vs_aqi_interactive(df: pd.DataFrame) -> go.Figure:
    """Price against AQI, coloured by AQI band, with the linear fit."""
    sub = df[["aqi", "price_inr", "city", "neighbourhood", "room_type", "aqi_category"]].dropna(subset=["aqi", "price_inr"])
    if sub.empty:
        return _empty()
    if len(sub) > 4000:  # ponytail: random sample keeps hover snappy; fit below still uses all rows
        sub = sub.sample(4000, random_state=42)

    fig = px.scatter(
        sub,
        x="aqi",
        y="price_inr",
        color="aqi_category",
        color_discrete_map=AQI_COLORS,
        category_orders={"aqi_category": AQI_ORDER},
        opacity=0.55,
        custom_data=["city", "neighbourhood", "room_type"],
        labels={"aqi": "AQI", "price_inr": "Nightly price (₹)"},
    )
    fig.update_traces(
        marker=dict(size=6, line=dict(width=0)),
        hovertemplate="<b>%{customdata[1]}, %{customdata[0]}</b><br>%{customdata[2]}<br>₹%{y:,.0f} · AQI %{x}<extra></extra>",
        selector=dict(mode="markers"),
    )
    fit = regression_summary(df)
    if fit:
        _fit_line(fig, fit, sub["aqi"].min(), sub["aqi"].max())
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
    return _style(fig, height=440)


def plot_aqi_city_ranking_interactive(df: pd.DataFrame, highlight: str | None = None) -> go.Figure:
    """Mean AQI per city, cleanest first, bars coloured by AQI band."""
    city = (
        df.groupby("city", as_index=False)
        .agg(mean_aqi=("aqi", "mean"), listings=("listing_id", "count"), median_price=("price_inr", "median"))
        .sort_values("mean_aqi", ascending=False)  # plotly draws the first row at the bottom
    )
    if city.empty:
        return _empty()
    colors = [aqi_band(v)[1] for v in city["mean_aqi"]]
    opacity = [1.0 if highlight in (None, c) else 0.35 for c in city["city"]]
    fig = go.Figure(
        go.Bar(
            x=city["mean_aqi"],
            y=city["city"],
            orientation="h",
            marker=dict(color=colors, opacity=opacity),
            customdata=np.stack([city["listings"], city["median_price"]], axis=-1),
            hovertemplate="<b>%{y}</b><br>Mean AQI %{x:.1f}<br>%{customdata[0]:,} listings · median ₹%{customdata[1]:,.0f}<extra></extra>",
        )
    )
    fig.add_vline(x=50, line=dict(dash="dot", width=1, color="rgba(128,128,128,0.8)"))
    fig.add_annotation(x=50, y=1.0, yref="paper", text="Good ≤ 50", showarrow=False, xanchor="left", yanchor="bottom", font=dict(size=11), opacity=0.7)
    fig.update_xaxes(title_text="Mean AQI")
    fig.update_yaxes(showgrid=False, title_text="")
    return _style(fig, height=max(380, len(city) * 20 + 60), legend=False)


def plot_room_type_interactive(df: pd.DataFrame) -> go.Figure:
    """Median price by room type: one bar each, with listing counts."""
    grp = df.groupby("room_type", as_index=False).agg(median=("price_inr", "median"), listings=("listing_id", "count"))
    if grp.empty:
        return _empty()
    grp = grp.sort_values("median")
    fig = go.Figure(
        go.Bar(
            x=grp["median"],
            y=grp["room_type"],
            orientation="h",
            marker_color=ACCENT,
            text=[f"₹{v:,.0f}" for v in grp["median"]],
            textposition="outside",
            cliponaxis=False,
            customdata=grp["listings"],
            hovertemplate="<b>%{y}</b><br>Median ₹%{x:,.0f}<br>%{customdata:,} listings<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Median nightly price (₹)", tickprefix="₹", tickformat=",.0f")
    fig.update_yaxes(showgrid=False, title_text="")
    return _style(fig, height=300, legend=False)


def plot_room_type_by_city(df: pd.DataFrame, top_n: int = 8) -> go.Figure:
    """Median price by room type for the cities with the most listings."""
    top = df["city"].value_counts().nlargest(top_n).index
    grp = df[df["city"].isin(top)].groupby(["city", "room_type"], as_index=False)["price_inr"].median()
    if grp.empty:
        return _empty()
    order = grp.groupby("city")["price_inr"].max().sort_values(ascending=False).index.tolist()
    fig = px.bar(
        grp,
        x="city",
        y="price_inr",
        color="room_type",
        barmode="group",
        category_orders={"city": order},
        labels={"price_inr": "Median nightly price (₹)", "city": "", "room_type": "Room type"},
    )
    fig.update_traces(hovertemplate="<b>%{x}</b> · %{fullData.name}<br>₹%{y:,.0f}<extra></extra>")
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
    return _style(fig, height=400)


def plot_city_price_boxplot_interactive(df: pd.DataFrame) -> go.Figure:
    """Price spread per city, ordered by median."""
    if df.empty:
        return _empty()
    order = df.groupby("city")["price_inr"].median().sort_values().index.tolist()
    fig = go.Figure()
    for c in order:
        vals = df.loc[df["city"] == c, "price_inr"].dropna()
        fig.add_trace(
            go.Box(
                x=vals,
                name=c,
                orientation="h",
                marker_color=ACCENT,
                line=dict(width=1.2),
                fillcolor="rgba(31,95,116,0.25)",
                boxpoints=False,
                hoverinfo="x+name",
            )
        )
    fig.update_xaxes(title_text="Nightly price (₹)", tickprefix="₹", tickformat=",.0f", showgrid=True, gridcolor="rgba(128,128,128,0.18)")
    fig.update_yaxes(showgrid=False)
    return _style(fig, height=max(380, len(order) * 20 + 60), legend=False)


def plot_neighbourhood_price(df: pd.DataFrame, city: str, top_n: int = 15) -> go.Figure:
    """Median price per neighbourhood in one city, bars coloured by that area's mean AQI."""
    sub = df[df["city"] == city]
    grp = (
        sub.groupby("neighbourhood", as_index=False)
        .agg(median=("price_inr", "median"), aqi=("aqi", "mean"), listings=("listing_id", "count"))
        .sort_values("median")
        .tail(top_n)
    )
    if grp.empty:
        return _empty()
    fig = go.Figure(
        go.Bar(
            x=grp["median"],
            y=grp["neighbourhood"],
            orientation="h",
            marker_color=[aqi_band(v)[1] for v in grp["aqi"]],
            customdata=np.stack([grp["aqi"], grp["listings"]], axis=-1),
            hovertemplate="<b>%{y}</b><br>Median ₹%{x:,.0f}<br>Mean AQI %{customdata[0]:.0f} · %{customdata[1]:,} listings<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Median nightly price (₹)", tickprefix="₹", tickformat=",.0f")
    fig.update_yaxes(showgrid=False)
    return _style(fig, height=max(320, len(grp) * 24 + 60), legend=False)


def plot_price_distribution_interactive(df: pd.DataFrame) -> go.Figure:
    """Price distribution split by AQI band."""
    sub = df.dropna(subset=["price_inr", "aqi_category"])
    if sub.empty:
        return _empty()
    present = [c for c in AQI_ORDER if c in set(sub["aqi_category"])]
    fig = px.histogram(
        sub,
        x="price_inr",
        color="aqi_category",
        color_discrete_map=AQI_COLORS,
        category_orders={"aqi_category": present},
        nbins=60,
        barmode="overlay",
        opacity=0.6,
        labels={"price_inr": "Nightly price (₹)", "count": "Listings"},
    )
    fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
    fig.update_yaxes(title_text="Listings")
    return _style(fig, height=380)


def plot_availability_vs_price_interactive(df: pd.DataFrame) -> go.Figure:
    """Calendar availability against price, by room type, with the linear fit."""
    sub = df.dropna(subset=["availability_365", "price_inr"])
    if sub.empty:
        return _empty()
    plot = sub.sample(3000, random_state=42) if len(sub) > 3000 else sub
    fig = px.scatter(
        plot,
        x="availability_365",
        y="price_inr",
        color="room_type",
        opacity=0.5,
        custom_data=["city", "neighbourhood"],
        labels={"availability_365": "Days available per year", "price_inr": "Nightly price (₹)", "room_type": "Room type"},
    )
    fig.update_traces(
        marker=dict(size=5, line=dict(width=0)),
        hovertemplate="<b>%{customdata[1]}, %{customdata[0]}</b><br>%{x} days · ₹%{y:,.0f}<extra></extra>",
        selector=dict(mode="markers"),
    )
    fit = regression_summary(sub, "availability_365", "price_inr")
    if fit:
        _fit_line(fig, fit, sub["availability_365"].min(), sub["availability_365"].max())
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
    return _style(fig, height=400)


_FEATURE_LABELS = {
    "price_inr": "Price",
    "aqi": "AQI",
    "minimum_nights": "Min. nights",
    "availability_365": "Availability",
    "number_of_reviews": "Reviews",
    "review_scores_rating": "Rating",
}


def plot_correlation_heatmap_interactive(df: pd.DataFrame) -> go.Figure:
    """Pearson correlations between the numeric listing features (lower triangle only)."""
    cols = [c for c in _FEATURE_LABELS if c in df.columns]
    corr = df[cols].dropna().corr()
    if corr.empty:
        return _empty()
    mask = np.triu(np.ones(corr.shape, dtype=bool), k=1)
    z = corr.where(~mask)
    labels = [_FEATURE_LABELS[c] for c in cols]
    fig = go.Figure(
        go.Heatmap(
            z=z.values,
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            colorscale=[[0, "#B65C4A"], [0.5, "rgba(128,128,128,0.08)"], [1, "#1F5F74"]],
            text=z.round(2).values,
            texttemplate="%{text}",
            hovertemplate="%{y} × %{x}: %{z:.3f}<extra></extra>",
            colorbar=dict(thickness=10, len=0.8, outlinewidth=0),
            xgap=2,
            ygap=2,
        )
    )
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False, ticks="")
    return _style(fig, height=400, legend=False)


def plot_feature_importance_interactive(importance: dict) -> go.Figure:
    """XGBoost feature importance, AQI highlighted."""
    labels = {
        "city": "City",
        "room_type": "Room type",
        "aqi": "AQI",
        "review_scores_rating": "Guest rating",
        "availability_365": "Availability",
        "number_of_reviews": "Review count",
        "minimum_nights": "Minimum stay",
    }
    items = sorted(importance.items(), key=lambda kv: kv[1])
    names = [labels.get(k, k) for k, _ in items]
    values = [v for _, v in items]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker_color=[HIGHLIGHT if n == "AQI" else ACCENT for n in names],
            text=[f"{v:.2f}%" for v in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.2f}%<extra></extra>",
        )
    )
    fig.update_xaxes(type="log", title_text="Share of importance (%, log scale)")
    fig.update_yaxes(showgrid=False)
    return _style(fig, height=320, legend=False)


ARCHETYPE_COLORS = ["#3E9C5B", "#C8453A", "#1F5F74", "#C9A15A", "#7A4E7E"]


def archetype_colors(names: list[str]) -> dict[str, str]:
    return {n: ARCHETYPE_COLORS[i % len(ARCHETYPE_COLORS)] for i, n in enumerate(sorted(names))}


def plot_kmeans_3d_clusters_interactive(df: pd.DataFrame) -> go.Figure:
    """Listings in price × AQI × rating space, coloured by K-Means archetype."""
    if df.empty or "archetype" not in df:
        return _empty()
    plot_df = df.sample(n=2500, random_state=42) if len(df) > 2500 else df
    fig = px.scatter_3d(
        plot_df,
        x="aqi",
        y="price_inr",
        z="review_scores_rating",
        color="archetype",
        color_discrete_map=archetype_colors(df["archetype"].dropna().unique().tolist()),
        opacity=0.7,
        labels={"aqi": "AQI", "price_inr": "Price (₹)", "review_scores_rating": "Rating"},
        hover_data={"city": True, "room_type": True},
    )
    fig.update_traces(marker=dict(size=3))
    fig = _style(fig, height=560)
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), scene=dict(bgcolor="rgba(0,0,0,0)"))
    return fig


def plot_cluster_comparison_bar(profile: pd.DataFrame) -> go.Figure:
    """Mean price and mean AQI per archetype, side by side as two small panels."""
    from plotly.subplots import make_subplots

    p = profile.sort_values("price_inr", ascending=True)
    names = p["short_name"]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06, subplot_titles=("Mean price (₹)", "Mean AQI"))
    fig.add_trace(
        go.Bar(x=p["price_inr"], y=names, orientation="h", marker_color=ACCENT, text=[f"₹{v:,.0f}" for v in p["price_inr"]], textposition="inside", hovertemplate="%{y}: ₹%{x:,.0f}<extra></extra>"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=p["aqi"], y=names, orientation="h", marker_color=[aqi_band(v)[1] for v in p["aqi"]], text=[f"{v:.0f}" for v in p["aqi"]], textposition="inside", hovertemplate="%{y}: AQI %{x:.1f}<extra></extra>"),
        row=1,
        col=2,
    )
    fig.update_annotations(font_size=12)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showticklabels=False, showgrid=False, ticks="")
    return _style(fig, height=300, legend=False)
