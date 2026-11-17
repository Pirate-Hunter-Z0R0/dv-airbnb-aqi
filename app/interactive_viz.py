"""
interactive_viz.py
==================
Interactive Plotly visualizations for the 'Paying for Clean Air?' dashboard.
Provides responsive, zoomable, and hoverable charts matching Inside Airbnb styling.
Supports both Light and Dark themes dynamically with explicit background and font styling.
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


def _get_theme_colors(template: str):
    is_dark = (template == "plotly_dark")
    return {
        "paper_bg": "#121417" if is_dark else "#ffffff",
        "plot_bg": "#121417" if is_dark else "#ffffff",
        "text_col": "#f1f5f9" if is_dark else "#0f172a",
        "grid_col": "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)",
        "line_col": "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.15)",
        "is_dark": is_dark,
    }


def plot_price_vs_aqi_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive Scatter plot of Price (INR) vs AQI with OLS regression trendline."""
    tc = _get_theme_colors(template)
    sub = df[["aqi", "price_inr", "city", "neighbourhood", "room_type", "aqi_category"]].dropna()

    if sub.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False, font=dict(color=tc["text_col"]))
        fig.update_layout(paper_bgcolor=tc["paper_bg"], plot_bgcolor=tc["plot_bg"])
        return fig

    # Regression statistics
    slope, intercept, r_value, p_value, _ = stats.linregress(sub["aqi"], sub["price_inr"])

    fig = px.scatter(
        sub,
        x="aqi",
        y="price_inr",
        color="aqi_category",
        color_discrete_map=_AQI_COLOR_MAP,
        opacity=0.7,
        hover_data={"city": True, "neighbourhood": True, "room_type": True, "aqi": True, "price_inr": ":,.0f"},
        labels={"aqi": "Air Quality Index (AQI)", "price_inr": "Nightly Price (₹ INR)", "aqi_category": "Air Quality"},
        template=template,
    )

    # Add linear regression trendline in front using Scattergl
    x_range = np.linspace(sub["aqi"].min(), sub["aqi"].max(), 100)
    y_pred = slope * x_range + intercept
    fig.add_trace(
        go.Scattergl(
            x=x_range,
            y=y_pred,
            mode="lines",
            name="OLS Fit",
            line=dict(color="#e74c3c", width=3.5, dash="dash"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        margin=dict(l=50, r=30, t=35, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            title=dict(text=""),
            font=dict(color=tc["text_col"]),
        ),
        hovermode="closest",
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    return fig


def plot_aqi_city_ranking_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive horizontal bar chart of mean AQI per city with color grading."""
    tc = _get_theme_colors(template)
    city_aqi = (
        df.groupby("city", as_index=False)
        .agg(mean_aqi=("aqi", "mean"), listing_count=("listing_id", "count"))
        .sort_values("mean_aqi", ascending=True)
    )

    if city_aqi.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False, font=dict(color=tc["text_col"]))
        fig.update_layout(paper_bgcolor=tc["paper_bg"], plot_bgcolor=tc["plot_bg"])
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
        template=template,
    )

    fig.add_vline(x=50, line_dash="dash", line_color="#27ae60", annotation_text="Clean Air (≤50)", annotation_font_color=tc["text_col"])
    fig.add_vline(x=100, line_dash="dash", line_color="#d35400", annotation_text="Moderate (≤100)", annotation_font_color=tc["text_col"])

    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        margin=dict(l=50, r=40, t=25, b=50),
        coloraxis_showscale=False,
        height=max(420, len(city_aqi) * 22),
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    return fig


def plot_room_type_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive grouped bar chart: Mean price by Room Type and City (Top 10)."""
    tc = _get_theme_colors(template)
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
        template=template,
    )

    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        margin=dict(l=50, r=20, t=25, b=50),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
            title=dict(text="City", font=dict(color=tc["text_col"])),
            font=dict(color=tc["text_col"]),
        ),
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    return fig


def plot_city_price_boxplot_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive horizontal boxplot of prices per city sorted by median."""
    tc = _get_theme_colors(template)
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
        template=template,
    )

    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        showlegend=False,
        margin=dict(l=60, r=40, t=25, b=50),
        height=max(450, len(order) * 22),
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1.2,
        linecolor=tc["line_col"],
        showgrid=True,
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1.2,
        linecolor=tc["line_col"],
        showgrid=False,
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    return fig


def plot_price_distribution_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive Histogram of Nightly Prices with Marginal Boxplots segmented by AQI category."""
    tc = _get_theme_colors(template)
    sub = df.dropna(subset=["price_inr", "aqi_category"])

    fig = px.histogram(
        sub,
        x="price_inr",
        color="aqi_category",
        color_discrete_map=_AQI_COLOR_MAP,
        nbins=50,
        marginal="box",
        labels={"price_inr": "Nightly Price (₹ INR)", "aqi_category": "Air Quality"},
        template=template,
    )

    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        barmode="overlay",
        height=430,
        margin=dict(l=50, r=40, t=35, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            title=dict(text=""),
            font=dict(color=tc["text_col"]),
        ),
    )
    fig.update_traces(opacity=0.7)
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    return fig


def plot_availability_vs_price_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive Scatter plot of Availability (days/year) vs Price (INR) with OLS trendline."""
    tc = _get_theme_colors(template)
    cols = ["availability_365", "price_inr", "room_type", "city", "neighbourhood"]
    sub = df[[c for c in cols if c in df.columns]].dropna(subset=["availability_365", "price_inr"])

    if sub.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False, font=dict(color=tc["text_col"]))
        fig.update_layout(paper_bgcolor=tc["paper_bg"], plot_bgcolor=tc["plot_bg"])
        return fig

    # Regression statistics
    slope, intercept, r_value, p_value, _ = stats.linregress(sub["availability_365"], sub["price_inr"])
    sig_str = "***" if p_value < 0.001 else ("**" if p_value < 0.01 else ("*" if p_value < 0.05 else "ns"))

    color_col = "room_type" if "room_type" in sub.columns else None

    fig = px.scatter(
        sub,
        x="availability_365",
        y="price_inr",
        color=color_col,
        color_discrete_sequence=px.colors.qualitative.Set2,
        opacity=0.6,
        hover_data={"city": True, "neighbourhood": True, "room_type": True, "availability_365": True, "price_inr": ":,.0f"},
        labels={"availability_365": "Availability (days/year)", "price_inr": "Nightly Price (₹ INR)", "room_type": "Room Type"},
        template=template,
    )

    # Add linear regression trendline in front using Scattergl
    x_range = np.linspace(sub["availability_365"].min(), sub["availability_365"].max(), 100)
    y_pred = slope * x_range + intercept
    fig.add_trace(
        go.Scattergl(
            x=x_range,
            y=y_pred,
            mode="lines",
            name="OLS Fit",
            line=dict(color="#c0392b", width=3.5, dash="dash"),
            hoverinfo="skip",
        )
    )

    # Correlation annotation in bottom right corner
    fig.add_annotation(
        text=f"<b>r = {r_value:.3f}</b> ({sig_str})",
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.04,
        showarrow=False,
        font=dict(size=11, color=tc["text_col"]),
        bgcolor="rgba(25, 28, 33, 0.85)" if tc["is_dark"] else "rgba(255, 255, 255, 0.9)",
        bordercolor="rgba(128, 128, 128, 0.4)",
        borderwidth=1,
        borderpad=5,
    )

    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        height=430,
        margin=dict(l=50, r=40, t=35, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            title=dict(text=""),
            font=dict(color=tc["text_col"]),
        ),
        hovermode="closest",
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=tc["line_col"],
        gridcolor=tc["grid_col"],
        tickfont=dict(color=tc["text_col"]),
        title_font=dict(color=tc["text_col"]),
        mirror=False,
    )
    return fig


def plot_correlation_heatmap_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Interactive Heatmap of correlation matrix."""
    tc = _get_theme_colors(template)
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
        labels=dict(color="Correlation"),
        template=template,
    )
    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        margin=dict(l=50, r=40, t=25, b=50),
    )
    return fig


def plot_feature_importance_interactive(importance_dict: dict, template: str = "plotly_dark") -> go.Figure:
    """Horizontal bar chart of XGBoost Feature Importances."""
    tc = _get_theme_colors(template)
    
    # Prettify labels
    name_map = {
        "city": "City Location (45 Global Metros)",
        "room_type": "Room Type (Entire/Private/Shared)",
        "aqi": "Air Quality Index (AQI)",
        "review_scores_rating": "Guest Review Rating",
        "availability_365": "Annual Calendar Availability",
        "number_of_reviews": "Total Reviews Count",
        "minimum_nights": "Minimum Stay Requirement",
    }
    
    features = [name_map.get(k, k) for k in list(importance_dict.keys())[::-1]]
    values = list(importance_dict.values())[::-1]
    
    # Highlight AQI with a distinctive accent color
    colors = ["#ff5a5f" if "AQI" in f else ("#3b82f6" if tc["is_dark"] else "#2563eb") for f in features]
    
    fig = go.Figure(
        go.Bar(
            x=values,
            y=features,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{v:.2f}%" for v in values],
            textposition="outside",
            cliponaxis=False,
        )
    )
    fig.update_layout(
        template=template,
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        xaxis=dict(
            title="Relative Importance Weight (%)",
            gridcolor=tc["grid_col"],
            zerolinecolor=tc["line_col"],
        ),
        yaxis=dict(gridcolor=tc["grid_col"]),
        margin=dict(l=10, r=40, t=30, b=40),
        height=350,
    )
    return fig


def plot_kmeans_3d_clusters_interactive(df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """3D Plotly Scatter Plot of K-Means Listing Archetypes."""
    tc = _get_theme_colors(template)
    
    # Sample down to 2,000 points if dataframe is large for smooth 60fps WebGL 3D rendering
    plot_df = df.sample(n=min(len(df), 2500), random_state=42) if len(df) > 2500 else df
    
    color_map = {
        "Eco-Luxury Havens (Clean Air & High Rate)": "#2ecc71",
        "Urban Budget Commuters (High AQI / Budget)": "#e74c3c",
        "Cluster 1 (Balanced Urban Segment)": "#3498db",
        "Standard High-Availability Rentals": "#f39c12",
    }
    
    fig = px.scatter_3d(
        plot_df,
        x="aqi",
        y="price_inr",
        z="review_scores_rating",
        color="archetype",
        color_discrete_map=color_map,
        labels={
            "aqi": "Air Quality (AQI)",
            "price_inr": "Nightly Price (₹ INR)",
            "review_scores_rating": "Review Rating (1-5)",
            "archetype": "Market Archetype",
        },
        hover_data={"city": True, "room_type": True, "availability_365": True},
        opacity=0.72,
        template=template,
    )
    fig.update_traces(marker=dict(size=3.5))
    fig.update_layout(
        paper_bgcolor=tc["paper_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        scene=dict(
            xaxis=dict(title="Air Quality (AQI)", backgroundcolor=tc["plot_bg"], gridcolor=tc["grid_col"]),
            yaxis=dict(title="Nightly Price (₹)", backgroundcolor=tc["plot_bg"], gridcolor=tc["grid_col"]),
            zaxis=dict(title="Rating", backgroundcolor=tc["plot_bg"], gridcolor=tc["grid_col"]),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=0, r=0, t=10, b=20),
        height=550,
    )
    return fig


def plot_cluster_comparison_bar(profile_df: pd.DataFrame, template: str = "plotly_dark") -> go.Figure:
    """Grouped bar chart comparing Cluster Mean Price vs Mean AQI."""
    tc = _get_theme_colors(template)
    
    # Sort by price descending
    df_sorted = profile_df.sort_values(by="price_inr", ascending=False).copy()
    
    # Shorten names for clean x-axis
    df_sorted["short_name"] = df_sorted["archetype"].apply(
        lambda s: s.split("(")[0].strip() if "(" in str(s) else str(s)
    )
    
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_sorted["short_name"],
            y=df_sorted["price_inr"],
            name="Mean Price (₹ INR)",
            marker_color="#ff5a5f",
            yaxis="y",
            text=[f"₹{p:,.0f}" for p in df_sorted["price_inr"]],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_sorted["short_name"],
            y=df_sorted["aqi"],
            name="Mean AQI (Pollution)",
            marker_color="#f59e0b" if tc["is_dark"] else "#d97706",
            yaxis="y2",
            text=[f"AQI {a:.1f}" for a in df_sorted["aqi"]],
            textposition="auto",
        )
    )
    fig.update_layout(
        template=template,
        paper_bgcolor=tc["paper_bg"],
        plot_bgcolor=tc["plot_bg"],
        font=dict(color=tc["text_col"], family="Inter, sans-serif"),
        barmode="group",
        yaxis=dict(
            title=dict(text="Mean Nightly Price (₹ INR)", font=dict(color="#ff5a5f")),
            tickfont=dict(color="#ff5a5f"),
            gridcolor=tc["grid_col"],
        ),
        yaxis2=dict(
            title=dict(text="Mean AQI Index", font=dict(color="#d97706")),
            tickfont=dict(color="#d97706"),
            overlaying="y",
            side="right",
            gridcolor="rgba(0,0,0,0)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        height=380,
    )
    return fig

