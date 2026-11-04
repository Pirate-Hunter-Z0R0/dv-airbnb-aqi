"""
interactive_viz.py
==================
Interactive Plotly visualizations for the 'Paying for Clean Air?' dashboard.
Provides responsive, zoomable, and hoverable charts matching Inside Airbnb styling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

_AQI_COLOR_MAP = {
    "Good": "#2ecc71",
    "Moderate": "#f1c40f",
    "Unhealthy for Sensitive Groups": "#e67e22",
    "Unhealthy": "#e74c3c",
    "Very Unhealthy": "#8e44ad",
    "Hazardous": "#7f0000",
}


def plot_price_vs_aqi_interactive(df: pd.DataFrame) -> go.Figure:
    """Interactive Scatter plot of Price (INR) vs AQI with OLS regression trendline."""
    sub = df[["aqi", "price_inr", "city", "neighbourhood", "room_type", "aqi_category"]].dropna()

    if sub.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig

    # Regression statistics
    slope, intercept, r_value, p_value, _ = stats.linregress(sub["aqi"], sub["price_inr"])
    p_str = "< 0.001" if p_value < 0.001 else f"= {p_value:.3f}"

    fig = px.scatter(
        sub,
        x="aqi",
        y="price_inr",
        color="aqi_category",
        color_discrete_map=_AQI_COLOR_MAP,
        hover_data={"city": True, "neighbourhood": True, "room_type": True, "aqi": True, "price_inr": ":,.0f"},
        labels={"aqi": "Air Quality Index (AQI)", "price_inr": "Nightly Price (₹ INR)", "aqi_category": "Air Quality"},
        title=f"Airbnb Price vs. Air Quality Index (r = {r_value:.3f}, p {p_str})",
    )

    # Add linear regression trendline
    x_range = np.linspace(sub["aqi"].min(), sub["aqi"].max(), 100)
    y_pred = slope * x_range + intercept
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode="lines",
            name="OLS Fit",
            line=dict(color="#e74c3c", width=2.5, dash="dash"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        margin=dict(l=50, r=40, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="closest",
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    return fig


def plot_aqi_city_ranking_interactive(df: pd.DataFrame) -> go.Figure:
    """Interactive horizontal bar chart of mean AQI per city with color grading."""
    city_aqi = (
        df.groupby("city", as_index=False)
        .agg(mean_aqi=("aqi", "mean"), listing_count=("listing_id", "count"))
        .sort_values("mean_aqi", ascending=True)
    )

    if city_aqi.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig

    fig = px.bar(
        city_aqi,
        x="mean_aqi",
        y="city",
        orientation="h",
        color="mean_aqi",
        color_continuous_scale=["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"],
        labels={"mean_aqi": "Mean AQI", "city": "City", "listing_count": "Listings"},
        hover_data={"listing_count": True, "mean_aqi": ":.1f"},
        title="Mean Air Quality Index (AQI) by City",
    )

    fig.add_vline(x=50, line_dash="dash", line_color="#27ae60", annotation_text="Clean Air (≤50)")
    fig.add_vline(x=100, line_dash="dash", line_color="#d35400", annotation_text="Moderate (≤100)")

    fig.update_layout(
        margin=dict(l=50, r=40, t=60, b=50),
        coloraxis_showscale=False,
        height=max(400, len(city_aqi) * 22),
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    return fig


def plot_room_type_interactive(df: pd.DataFrame) -> go.Figure:
    """Interactive grouped bar chart: Mean price by Room Type and City (Top 10)."""
    top_cities = df["city"].value_counts().nlargest(10).index.tolist()
    sub = df[df["city"].isin(top_cities)]

    grp = (
        sub.groupby(["city", "room_type"], as_index=False)["price_inr"]
        .mean()
        .rename(columns={"price_inr": "mean_price_inr"})
    )

    fig = px.bar(
        grp,
        x="room_type",
        y="mean_price_inr",
        color="city",
        barmode="group",
        labels={"room_type": "Room Type", "mean_price_inr": "Mean Nightly Price (₹ INR)", "city": "City"},
        title="Mean Nightly Price by Room Type (Top 10 Cities)",
    )

    fig.update_layout(
        margin=dict(l=50, r=40, t=95, b=60),
        title=dict(y=0.96, x=0.01, xanchor="left", yanchor="top"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            title=dict(text=""),
        ),
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    return fig


def plot_city_price_boxplot_interactive(df: pd.DataFrame) -> go.Figure:
    """Interactive horizontal boxplot of prices per city sorted by median."""
    order = (
        df.groupby("city")["price_inr"]
        .median()
        .sort_values(ascending=True)
        .index.tolist()
    )

    fig = px.box(
        df,
        x="price_inr",
        y="city",
        category_orders={"city": order},
        color="city",
        labels={"price_inr": "Nightly Price (₹ INR)", "city": "City"},
        title="Nightly Price Distribution by City (INR)",
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=60, r=40, t=60, b=60),
        height=max(450, len(order) * 24),
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1.2,
        linecolor="rgba(160, 170, 185, 0.6)",
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.15)",
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1.2,
        linecolor="rgba(160, 170, 185, 0.6)",
        showgrid=False,
        mirror=False,
    )
    return fig


def plot_price_distribution_interactive(df: pd.DataFrame) -> go.Figure:
    """Interactive Histogram of Nightly Prices segmented by AQI category."""
    sub = df.dropna(subset=["price_inr", "aqi_category"])
    
    fig = px.histogram(
        sub,
        x="price_inr",
        color="aqi_category",
        color_discrete_map=_AQI_COLOR_MAP,
        nbins=50,
        marginal="box",
        labels={"price_inr": "Nightly Price (₹ INR)", "aqi_category": "Air Quality"},
        title="Nightly Price Distribution Across Air Quality Categories",
    )

    fig.update_layout(
        barmode="overlay",
        margin=dict(l=50, r=40, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_traces(opacity=0.7)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="rgba(128,128,128,0.3)", mirror=False)
    return fig


def plot_correlation_heatmap_interactive(df: pd.DataFrame) -> go.Figure:
    """Interactive Heatmap of correlation matrix."""
    num_cols = [
        "price_inr", "aqi", "minimum_nights",
        "availability_365", "number_of_reviews", "review_scores_rating"
    ]
    sub = df[[c for c in num_cols if c in df.columns]].dropna()
    corr = sub.corr().round(3)

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Feature Correlation Matrix",
        labels=dict(color="Correlation"),
    )
    fig.update_layout(
        margin=dict(l=50, r=40, t=60, b=50),
    )
    return fig
