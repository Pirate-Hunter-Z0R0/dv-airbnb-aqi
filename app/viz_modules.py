"""
viz_modules.py
==============
Chart-generation functions for the "Paying for Clean Air?" Streamlit dashboard.

Each public function accepts a pandas DataFrame (already filtered by the
caller) and returns a matplotlib Figure object ready to be passed to
``st.pyplot()``.  No function calls ``plt.show()``; that is the caller's
responsibility.

Dependencies
------------
matplotlib, seaborn, pandas, numpy, scipy, statsmodels
"""

from __future__ import annotations

import warnings
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import statsmodels.api as sm

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Global seaborn theme (applied once at import time)
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid", palette="muted")

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
_AQI_PALETTE = {
    "Good":            "#2ecc71",
    "Moderate":        "#f1c40f",
    "Unhealthy for SG":"#e67e22",
    "Unhealthy":       "#e74c3c",
    "Very Unhealthy":  "#8e44ad",
    "Hazardous":       "#7f0000",
}

_ROOM_PALETTE = sns.color_palette("Set2", 8)


def _aqi_color(val: float) -> str:
    """Return a hex colour string for a given AQI value."""
    if val <= 50:
        return _AQI_PALETTE["Good"]
    elif val <= 100:
        return _AQI_PALETTE["Moderate"]
    elif val <= 150:
        return _AQI_PALETTE["Unhealthy for SG"]
    elif val <= 200:
        return _AQI_PALETTE["Unhealthy"]
    elif val <= 300:
        return _AQI_PALETTE["Very Unhealthy"]
    return _AQI_PALETTE["Hazardous"]


# ---------------------------------------------------------------------------
# 1. Scatter: Price vs AQI
# ---------------------------------------------------------------------------

def plot_price_vs_aqi_scatter(
    df: pd.DataFrame,
    hue_col: str = "aqi_category",
) -> plt.Figure:
    """Scatter plot of nightly Airbnb price (INR) against AQI.

    Parameters
    ----------
    df:
        DataFrame containing at least ``aqi``, ``price_inr``, and the column
        named by *hue_col*.
    hue_col:
        Column used to colour the scatter points (default ``aqi_category``).

    Returns
    -------
    matplotlib.figure.Figure
    """
    cols = ["aqi", "price_inr"]
    if hue_col in df.columns:
        cols.append(hue_col)
    sub = df[cols].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    # Colour palette order
    cat_order = [k for k in _AQI_PALETTE if k in sub[hue_col].unique()] if hue_col in sub.columns else None
    palette   = {k: _AQI_PALETTE[k] for k in cat_order} if cat_order else "muted"

    sns.scatterplot(
        data=sub,
        x="aqi",
        y="price_inr",
        hue=hue_col if hue_col in sub.columns else None,
        hue_order=cat_order,
        palette=palette,
        alpha=0.55,
        edgecolors="white",
        linewidth=0.4,
        s=40,
        ax=ax,
    )

    # Regression line
    slope, intercept, r_val, p_val, _ = stats.linregress(sub["aqi"], sub["price_inr"])
    x_line = np.linspace(sub["aqi"].min(), sub["aqi"].max(), 300)
    ax.plot(x_line, slope * x_line + intercept, color="#c0392b", lw=2, ls="--", label="OLS fit")

    # Annotation: r and p
    sig = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "ns"))
    annot = f"r = {r_val:.3f}  ({sig})\np = {p_val:.2e}"
    ax.text(
        0.97, 0.97, annot,
        transform=ax.transAxes,
        ha="right", va="top",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="grey", alpha=0.85),
    )

    # AQI scale legend
    scale_txt = (
        "AQI Scale:\n"
        "0–50   Good\n"
        "51–100  Moderate\n"
        "101–150 Unhealthy for SG\n"
        "151–200 Unhealthy\n"
        "201–300 Very Unhealthy\n"
        "301+   Hazardous"
    )
    ax.text(
        0.01, 0.97, scale_txt,
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=7.5,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow", ec="grey", alpha=0.85),
    )

    ax.set_xlabel("AQI (Air Quality Index)", fontsize=12)
    ax.set_ylabel("Nightly Price (INR)", fontsize=12)
    ax.set_title("Airbnb Price vs. Air Quality Index", fontsize=14, fontweight="bold")
    ax.legend(title=hue_col.replace("_", " ").title(), loc="upper left",
              bbox_to_anchor=(0.01, 0.72), fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Horizontal boxplot: Price by city
# ---------------------------------------------------------------------------

def plot_city_price_boxplot(
    df: pd.DataFrame,
    sort_by: str = "median_price",
) -> plt.Figure:
    """Horizontal box plot of nightly price (INR) for each city.

    Boxes are coloured by the city's dominant AQI bucket
    (Good / Moderate / Unhealthy).

    Parameters
    ----------
    df:
        DataFrame with columns ``city``, ``price_inr``, and optionally ``aqi``.
    sort_by:
        ``"median_price"`` (default) or ``"city"`` to control sort order.

    Returns
    -------
    matplotlib.figure.Figure
    """
    sub = df[["city", "price_inr"] + (["aqi"] if "aqi" in df.columns else [])].dropna(subset=["city", "price_inr"])

    medians = sub.groupby("city")["price_inr"].median().sort_values(ascending=False)
    city_order = medians.index.tolist() if sort_by == "median_price" else sorted(medians.index)

    # City AQI bucket colour
    if "aqi" in sub.columns:
        city_aqi = sub.groupby("city")["aqi"].mean()
        def _bucket_color(city: str) -> str:
            aqi = city_aqi.get(city, 100)
            if aqi <= 50:
                return _AQI_PALETTE["Good"]
            elif aqi <= 100:
                return _AQI_PALETTE["Moderate"]
            return _AQI_PALETTE["Unhealthy"]
        colors = [_bucket_color(c) for c in city_order]
    else:
        colors = ["#3498db"] * len(city_order)

    fig, ax = plt.subplots(figsize=(12, max(6, len(city_order) * 0.55)))

    bp = ax.boxplot(
        [sub.loc[sub["city"] == c, "price_inr"].values for c in city_order],
        vert=False,
        patch_artist=True,
        notch=False,
        widths=0.55,
        flierprops=dict(marker="o", markersize=2, alpha=0.3, linestyle="none"),
        medianprops=dict(color="black", linewidth=1.5),
    )

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.78)

    ax.set_yticks(range(1, len(city_order) + 1))
    ax.set_yticklabels(city_order, fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.set_xlabel("Nightly Price (INR)", fontsize=12)
    ax.set_title("Nightly Price Distribution by City (INR)", fontsize=14, fontweight="bold")

    # Legend
    patches = [
        mpatches.Patch(color=_AQI_PALETTE["Good"],      label="AQI ≤ 50 (Good)"),
        mpatches.Patch(color=_AQI_PALETTE["Moderate"],  label="AQI 51–100 (Moderate)"),
        mpatches.Patch(color=_AQI_PALETTE["Unhealthy"], label="AQI > 100 (Unhealthy+)"),
    ]
    ax.legend(handles=patches, loc="lower right", fontsize=8)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 3. Bar chart: Mean AQI by city (coloured by AQI level)
# ---------------------------------------------------------------------------

def plot_aqi_map_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Bar chart of mean AQI per city, coloured by AQI category.

    Note: This uses a bar chart rather than a geographic map because the
    dashboard has no folium dependency.

    Parameters
    ----------
    df:
        DataFrame with columns ``city`` and ``aqi``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    sub = df[["city", "aqi"]].dropna()
    city_aqi = sub.groupby("city")["aqi"].mean().sort_values()

    colors = [_aqi_color(v) for v in city_aqi.values]

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(city_aqi.index, city_aqi.values, color=colors, edgecolor="white", linewidth=0.6)

    # Value labels
    for bar, val in zip(bars, city_aqi.values):
        ax.text(
            val + 1, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}",
            va="center", ha="left", fontsize=8,
        )

    # Reference lines
    for threshold, label in [(50, "Good"), (100, "Moderate"), (150, "USG"), (200, "Unhealthy")]:
        ax.axvline(threshold, color="grey", lw=0.8, ls="--", alpha=0.6)
        ax.text(threshold + 1, len(city_aqi) - 0.5, label, fontsize=7, color="grey")

    ax.set_xlabel("Mean AQI", fontsize=12)
    ax.set_title("Mean AQI by City", fontsize=14, fontweight="bold")

    # Colour legend
    patches = [mpatches.Patch(color=c, label=l) for l, c in _AQI_PALETTE.items()]
    ax.legend(handles=patches, loc="lower right", fontsize=8, title="AQI Category")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 4. Grouped bar: Mean price by room type × city (top-10 cities)
# ---------------------------------------------------------------------------

def plot_room_type_price(df: pd.DataFrame) -> plt.Figure:
    """Grouped bar chart of mean nightly price by room type for the top-10
    cities (by listing count).

    Parameters
    ----------
    df:
        DataFrame with columns ``room_type``, ``city``, ``price_inr``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    sub = df[["room_type", "city", "price_inr"]].dropna()
    top10 = sub["city"].value_counts().head(10).index.tolist()
    sub = sub[sub["city"].isin(top10)]

    pivot = sub.groupby(["room_type", "city"])["price_inr"].mean().unstack("city").fillna(0)
    pivot = pivot[top10]  # maintain city order

    fig, ax = plt.subplots(figsize=(13, 6))
    pivot.plot(kind="bar", ax=ax, colormap="tab10", edgecolor="white", linewidth=0.5, width=0.8)

    ax.set_xlabel("Room Type", fontsize=12)
    ax.set_ylabel("Mean Nightly Price (INR)", fontsize=12)
    ax.set_title("Mean Price by Room Type and City (Top 10 Cities)", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
    ax.legend(title="City", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=7)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 5. Correlation heatmap
# ---------------------------------------------------------------------------

def plot_correlation_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Seaborn heatmap of the Pearson correlation matrix for key features.

    Columns included (where available):
    ``price_inr``, ``aqi``, ``minimum_nights``, ``availability_365``,
    ``number_of_reviews``, ``review_scores_rating``.

    Parameters
    ----------
    df:
        DataFrame containing any subset of the above columns.

    Returns
    -------
    matplotlib.figure.Figure
    """
    desired = [
        "price_inr", "aqi", "minimum_nights",
        "availability_365", "number_of_reviews", "review_scores_rating",
    ]
    cols = [c for c in desired if c in df.columns]
    sub  = df[cols].dropna()
    corr = sub.corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1, vmax=1,
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        annot_kws={"size": 9},
    )
    ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=30)
    ax.tick_params(axis="y", rotation=0)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 6. Faceted regression: AQI vs Price by city (top-N)
# ---------------------------------------------------------------------------

def plot_aqi_price_regression_by_city(
    df: pd.DataFrame,
    top_n: int = 9,
) -> plt.Figure:
    """3×3 grid of scatter + regression panels, one per top-N city.

    Parameters
    ----------
    df:
        DataFrame with columns ``city``, ``aqi``, ``price_inr``.
    top_n:
        Number of cities to show (max 9, default 9).

    Returns
    -------
    matplotlib.figure.Figure
    """
    sub    = df[["city", "aqi", "price_inr"]].dropna()
    top_n  = min(top_n, 9)
    cities = sub["city"].value_counts().head(top_n).index.tolist()

    ncols = 3
    nrows = int(np.ceil(top_n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 12), constrained_layout=True)
    axes = np.array(axes).flatten()

    for i, city in enumerate(cities):
        ax   = axes[i]
        data = sub[sub["city"] == city]
        ax.scatter(data["aqi"], data["price_inr"], alpha=0.4, s=18, color="#3498db", edgecolors="none")

        if len(data) >= 5:
            slope, intercept, r, p, _ = stats.linregress(data["aqi"], data["price_inr"])
            x_line = np.linspace(data["aqi"].min(), data["aqi"].max(), 200)
            ax.plot(x_line, slope * x_line + intercept, color="#e74c3c", lw=1.5, ls="--")
            sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
            ax.set_title(f"{city}\nr={r:.2f} {sig}", fontsize=9, fontweight="bold")
        else:
            ax.set_title(city, fontsize=9, fontweight="bold")

        ax.set_xlabel("AQI", fontsize=7)
        ax.set_ylabel("Price (INR)", fontsize=7)
        ax.tick_params(labelsize=7)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # Hide unused panels
    for j in range(len(cities), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("AQI vs Price Regression by City", fontsize=15, fontweight="bold", y=1.01)
    return fig


# ---------------------------------------------------------------------------
# 7. Price distribution: histogram + KDE
# ---------------------------------------------------------------------------

def plot_price_distribution(df: pd.DataFrame) -> plt.Figure:
    """Two-panel figure: log-scale price histogram (left) and KDE by AQI
    category (right).

    Parameters
    ----------
    df:
        DataFrame with columns ``price_inr`` and optionally ``aqi_category``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    sub = df[["price_inr"] + (["aqi_category"] if "aqi_category" in df.columns else [])].dropna(subset=["price_inr"])
    sub = sub[sub["price_inr"] > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Left: histogram (log x-axis)
    ax1.hist(
        sub["price_inr"],
        bins=60,
        color="#3498db",
        edgecolor="white",
        linewidth=0.4,
        alpha=0.85,
    )
    ax1.set_xscale("log")
    ax1.set_xlabel("Nightly Price (INR) — log scale", fontsize=11)
    ax1.set_ylabel("Count", fontsize=11)
    ax1.set_title("Price Histogram (Log Scale)", fontsize=12, fontweight="bold")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # Right: KDE by AQI category
    if "aqi_category" in sub.columns:
        cat_order = [k for k in _AQI_PALETTE if k in sub["aqi_category"].unique()]
        for cat in cat_order:
            d = sub.loc[sub["aqi_category"] == cat, "price_inr"]
            if len(d) >= 5:
                d.plot.kde(ax=ax2, label=cat, color=_AQI_PALETTE[cat], linewidth=2)
    else:
        sub["price_inr"].plot.kde(ax=ax2, color="#3498db", linewidth=2)

    ax2.set_xlabel("Nightly Price (INR)", fontsize=11)
    ax2.set_ylabel("Density", fontsize=11)
    ax2.set_title("Price KDE by AQI Category", fontsize=12, fontweight="bold")
    ax2.legend(title="AQI Category", fontsize=8)
    ax2.set_xlim(left=0)

    fig.suptitle("Price Distribution Analysis", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 8. Violin: Price by neighbourhood (single city)
# ---------------------------------------------------------------------------

def plot_neighbourhood_price(df: pd.DataFrame, city: str) -> plt.Figure:
    """Violin plot of nightly price by neighbourhood for one city.

    Parameters
    ----------
    df:
        DataFrame with columns ``city``, ``neighbourhood``, ``price_inr``.
    city:
        The city to visualise.

    Returns
    -------
    matplotlib.figure.Figure
    """
    sub = df[df["city"] == city][["neighbourhood", "price_inr"]].dropna()

    # Limit to top-15 neighbourhoods by listing count for readability
    top_neigh = sub["neighbourhood"].value_counts().head(15).index.tolist()
    sub = sub[sub["neighbourhood"].isin(top_neigh)]
    medians = sub.groupby("neighbourhood")["price_inr"].median().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(11, 5))

    if sub.empty or sub["neighbourhood"].nunique() < 2:
        ax.text(0.5, 0.5, "Not enough data for this city.",
                ha="center", va="center", transform=ax.transAxes, fontsize=13)
    else:
        sns.violinplot(
            data=sub,
            x="neighbourhood",
            y="price_inr",
            order=medians.index,
            palette="Set3",
            inner="box",
            cut=0,
            linewidth=0.8,
            ax=ax,
        )
        ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        ax.set_xlabel("Neighbourhood", fontsize=11)
        ax.set_ylabel("Nightly Price (INR)", fontsize=11)

    ax.set_title(f"Price by Neighbourhood — {city}", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 9. Scatter: Availability vs Price
# ---------------------------------------------------------------------------

def plot_availability_vs_price(df: pd.DataFrame) -> plt.Figure:
    """Scatter plot of availability_365 vs nightly price, coloured by room
    type, with a regression line.

    Parameters
    ----------
    df:
        DataFrame with columns ``availability_365``, ``price_inr``, and
        optionally ``room_type``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    cols = ["availability_365", "price_inr"]
    if "room_type" in df.columns:
        cols.append("room_type")
    sub = df[cols].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    hue = "room_type" if "room_type" in sub.columns else None
    sns.scatterplot(
        data=sub,
        x="availability_365",
        y="price_inr",
        hue=hue,
        palette="Set2",
        alpha=0.5,
        edgecolors="none",
        s=35,
        ax=ax,
    )

    # Regression line (all data)
    if len(sub) >= 5:
        slope, intercept, r_val, p_val, _ = stats.linregress(
            sub["availability_365"], sub["price_inr"]
        )
        x_line = np.linspace(sub["availability_365"].min(), sub["availability_365"].max(), 300)
        ax.plot(x_line, slope * x_line + intercept, color="#c0392b", lw=2, ls="--", label="OLS fit")
        sig = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "ns"))
        ax.text(
            0.97, 0.03,
            f"r = {r_val:.3f}  ({sig})",
            transform=ax.transAxes,
            ha="right", va="bottom",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="grey", alpha=0.85),
        )

    ax.set_xlabel("Availability (days/year)", fontsize=12)
    ax.set_ylabel("Nightly Price (INR)", fontsize=12)
    ax.set_title("Availability vs. Nightly Price", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    if hue:
        ax.legend(title="Room Type", fontsize=9)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 10. OLS summary table
# ---------------------------------------------------------------------------

def plot_ols_summary_table(df: pd.DataFrame) -> plt.Figure:
    """Fit an OLS regression and render the summary as a formatted matplotlib
    figure.

    Model: ``price_inr ~ aqi + minimum_nights + availability_365 +
    number_of_reviews + review_scores_rating``

    Parameters
    ----------
    df:
        DataFrame containing the model variables.

    Returns
    -------
    matplotlib.figure.Figure
    """
    desired_x = [
        "aqi", "minimum_nights", "availability_365",
        "number_of_reviews", "review_scores_rating",
    ]
    available_x = [c for c in desired_x if c in df.columns]
    cols = ["price_inr"] + available_x
    sub  = df[cols].dropna()

    fig, ax = plt.subplots(figsize=(10, 8), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")
    ax.axis("off")

    if len(sub) < 10 or not available_x:
        ax.text(
            0.5, 0.5,
            "Insufficient data for OLS regression.\nPlease widen your filters.",
            ha="center", va="center",
            fontsize=13, color="#c0392b",
            transform=ax.transAxes,
        )
        ax.set_title("OLS Regression: Price ~ AQI + Controls", fontsize=14, fontweight="bold")
        fig.tight_layout()
        return fig

    y = sub["price_inr"]
    X = sm.add_constant(sub[available_x])

    try:
        model  = sm.OLS(y, X).fit()
        summary_str = model.summary().as_text()
    except Exception as exc:
        summary_str = f"OLS fitting failed:\n{exc}"

    ax.text(
        0.01, 0.99,
        summary_str,
        transform=ax.transAxes,
        va="top", ha="left",
        fontsize=7.5,
        family="monospace",
        color="#111827",
        wrap=True,
    )
    ax.set_title(
        "OLS Regression: Price ~ AQI + Controls",
        fontsize=14, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    return fig
