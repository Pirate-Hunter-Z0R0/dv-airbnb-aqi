"""
backend/server.py
=================
Lightweight high-performance FastAPI service for 'Paying for Clean Air?'.
Serves processed listings, aggregate statistics, city comparisons, and regression analytics.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from scipy import stats

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "processed" / "merged_listings.csv"

app = FastAPI(
    title="Clean Air Airbnb API",
    description="Backend API powering the Inside Airbnb interactive frontend",
    version="1.0.0",
)

# Enable CORS for the local React/Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset into memory
df_raw = pd.DataFrame()


@app.on_event("startup")
def load_dataset():
    global df_raw
    if DATA_PATH.exists():
        df_raw = pd.read_csv(DATA_PATH)
        df_raw["aqi"] = pd.to_numeric(df_raw["aqi"], errors="coerce")
        df_raw["price_inr"] = pd.to_numeric(df_raw["price_inr"], errors="coerce")
        df_raw["latitude"] = pd.to_numeric(df_raw["latitude"], errors="coerce")
        df_raw["longitude"] = pd.to_numeric(df_raw["longitude"], errors="coerce")
        print(f"Loaded {len(df_raw):,} records across {df_raw['city'].nunique()} cities.")
    else:
        print(f"WARNING: Dataset not found at {DATA_PATH}")


def filter_dataframe(
    city: Optional[str] = None,
    room_types: Optional[list[str]] = None,
    min_aqi: Optional[float] = None,
    max_aqi: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> pd.DataFrame:
    df = df_raw.copy()
    if city and city != "All Cities (Global View)":
        df = df[df["city"] == city]
    if room_types is not None and not isinstance(room_types, (Query, type(Ellipsis))):
        if isinstance(room_types, (list, tuple, set)):
            df = df[df["room_type"].isin(room_types)]
    if min_aqi is not None:
        df = df[df["aqi"] >= min_aqi]
    if max_aqi is not None:
        df = df[df["aqi"] <= max_aqi]
    if min_price is not None:
        df = df[df["price_inr"] >= min_price]
    if max_price is not None:
        df = df[df["price_inr"] <= max_price]
    return df


@app.get("/api/meta")
def get_metadata():
    """Return available cities, room types, price/aqi limits."""
    return {
        "cities": ["All Cities (Global View)"] + sorted(df_raw["city"].dropna().unique().tolist()),
        "room_types": sorted(df_raw["room_type"].dropna().unique().tolist()),
        "aqi_range": {
            "min": int(df_raw["aqi"].min() if not df_raw.empty else 0),
            "max": int(df_raw["aqi"].max() if not df_raw.empty else 300),
        },
        "price_range": {
            "min": int(df_raw["price_inr"].min() if not df_raw.empty else 0),
            "max": int(df_raw["price_inr"].max() if not df_raw.empty else 100000),
        },
    }


@app.get("/api/stats")
def get_stats(
    city: Optional[str] = None,
    room_type: Optional[list[str]] = Query(default=None),
    min_aqi: Optional[float] = None,
    max_aqi: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    """Aggregate KPIs matching current view filters."""
    room_list = room_type if isinstance(room_type, list) else None
    df = filter_dataframe(city, room_list, min_aqi, max_aqi, min_price, max_price)
    if df.empty:
        return {
            "total_listings": 0,
            "entire_home_pct": 0,
            "median_price": 0,
            "mean_aqi": 0,
            "clean_air_pct": 0,
        }

    return {
        "total_listings": int(len(df)),
        "entire_home_pct": round(float((df["room_type"] == "Entire home/apt").mean() * 100), 1),
        "median_price": round(float(df["price_inr"].median()), 0),
        "mean_aqi": round(float(df["aqi"].mean()), 1),
        "clean_air_pct": round(float((df["aqi"] <= 50).mean() * 100), 1),
    }


@app.get("/api/listings")
def get_listings(
    city: Optional[str] = None,
    room_type: Optional[list[str]] = Query(None),
    min_aqi: Optional[float] = None,
    max_aqi: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 1500,
):
    """Return map point coordinates & listing metadata."""
    df = filter_dataframe(city, room_type, min_aqi, max_aqi, min_price, max_price)
    sub = df.dropna(subset=["latitude", "longitude"]).head(limit)
    return sub[
        [
            "listing_id",
            "city",
            "neighbourhood",
            "room_type",
            "price_inr",
            "aqi",
            "aqi_category",
            "latitude",
            "longitude",
            "review_scores_rating",
            "number_of_reviews",
        ]
    ].to_dict(orient="records")


@app.get("/api/charts/aqi-ranking")
def get_city_aqi_ranking():
    """Return ranked mean AQI by city for bar charts."""
    grp = (
        df_raw.groupby("city", as_index=False)
        .agg(mean_aqi=("aqi", "mean"), listing_count=("listing_id", "count"), median_price=("price_inr", "median"))
        .sort_values("mean_aqi", ascending=True)
    )
    grp["mean_aqi"] = grp["mean_aqi"].round(1)
    grp["median_price"] = grp["median_price"].round(0)
    return grp.to_dict(orient="records")


@app.get("/api/charts/correlation")
def get_correlation():
    """Return correlation matrix."""
    cols = ["price_inr", "aqi", "minimum_nights", "availability_365", "number_of_reviews", "review_scores_rating"]
    sub = df_raw[cols].dropna()
    corr = sub.corr().round(3)
    return {"labels": cols, "matrix": corr.values.tolist()}


@app.get("/api/charts/scatter")
def get_scatter(
    city: Optional[str] = None,
    limit: int = 800,
):
    """Return points for AQI vs Price scatter plus regression line."""
    df = filter_dataframe(city)
    sub = df[["aqi", "price_inr", "city", "neighbourhood", "room_type", "aqi_category"]].dropna()

    if len(sub) > limit:
        sub = sub.sample(n=limit, random_state=42)

    slope, intercept, r_val, p_val, _ = stats.linregress(sub["aqi"], sub["price_inr"])

    return {
        "points": sub.to_dict(orient="records"),
        "regression": {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_value": float(r_val),
            "p_value": float(p_val),
        },
    }


@app.get("/api/compare")
def compare_cities(city_a: str, city_b: str):
    """Return comparative metrics and top clean-air stays for two cities."""
    df_a = df_raw[df_raw["city"] == city_a].copy()
    df_b = df_raw[df_raw["city"] == city_b].copy()

    def get_summary(df):
        if df.empty:
            return {}
        return {
            "total_listings": int(len(df)),
            "mean_aqi": round(float(df["aqi"].mean()), 1),
            "median_price": round(float(df["price_inr"].median()), 0),
            "clean_air_pct": round(float((df["aqi"] <= 50).mean() * 100), 1),
            "entire_home_pct": round(float((df["room_type"] == "Entire home/apt").mean() * 100), 1),
        }

    def get_top_stays(df):
        clean = df[df["aqi"] <= 50]
        if clean.empty:
            clean = df.sort_values("aqi").head(25)
        top = clean.sort_values(
            by=["review_scores_rating", "number_of_reviews", "price_inr"],
            ascending=[False, False, True],
        ).head(5)
        return top[
            ["neighbourhood", "room_type", "price_inr", "aqi", "review_scores_rating", "number_of_reviews"]
        ].to_dict(orient="records")

    return {
        "city_a": {"name": city_a, "summary": get_summary(df_a), "top_stays": get_top_stays(df_a)},
        "city_b": {"name": city_b, "summary": get_summary(df_b), "top_stays": get_top_stays(df_b)},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
