"""
Data merging pipeline for the Clean Air Airbnb project.

Reads 30 city CSVs from data/raw/, standardizes schemas, applies INR
conversion, imputes missing values, and writes a merged processed CSV.
"""

from __future__ import annotations

import logging
import os
import pathlib
import sys
from typing import Optional

import numpy as np
import pandas as pd

# Allow running this script directly from the scripts/ directory.
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from currency_converter import CITY_CURRENCY_MAP, convert_city_prices  # noqa: E402

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------
EXPECTED_COLUMNS: list[str] = [
    "city",
    "listing_id",
    "neighbourhood",
    "room_type",
    "price",
    "minimum_nights",
    "availability_365",
    "number_of_reviews",
    "review_scores_rating",
    "aqi",
    "aqi_category",
    "latitude",
    "longitude",
]

# ---------------------------------------------------------------------------
# Synthetic median AQI values per city (used when real AQI data is absent)
# Source: representative annual medians (μg/m³ PM2.5 equivalents), 2023 est.
# ---------------------------------------------------------------------------
SYNTHETIC_AQI: dict[str, int] = {
    "Amsterdam": 35,
    "Bangkok": 105,
    "Barcelona": 42,
    "Beijing": 115,
    "Berlin": 38,
    "Bogota": 55,
    "Brisbane": 28,
    "Brussels": 40,
    "Budapest": 50,
    "Buenos Aires": 65,
    "Cape Town": 32,
    "Chicago": 46,
    "Copenhagen": 24,
    "Dallas": 52,
    "Delhi": 165,
    "Dublin": 25,
    "Edinburgh": 22,
    "Goa": 48,
    "Hawaii": 16,
    "Hong Kong": 82,
    "Istanbul": 75,
    "Lisbon": 38,
    "London": 42,
    "Madrid": 45,
    "Milan": 58,
    "Montreal": 28,
    "Mumbai": 92,
    "Munich": 32,
    "New York": 52,
    "Oslo": 22,
    "Ottawa": 26,
    "Paris": 48,
    "Rome": 54,
    "Sao Paulo": 88,
    "Santiago": 72,
    "Shanghai": 108,
    "Singapore": 60,
    "Stockholm": 20,
    "Sydney": 30,
    "Taipei": 78,
    "Tokyo": 45,
    "Toronto": 34,
    "Valencia": 40,
    "Venice": 35,
    "Zurich": 18,
}


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def standardize_schema(df: pd.DataFrame, city: str) -> pd.DataFrame:
    """Ensure the DataFrame conforms to the expected schema.

    Missing columns are added and filled with ``NaN``; the ``city`` column is
    set to *city*; leading/trailing whitespace is stripped from all object
    (string) columns.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame as loaded from a city CSV file.
    city : str
        City name to assign to every row in the ``city`` column.

    Returns
    -------
    pd.DataFrame
        A copy of *df* with the standardized schema applied.
    """
    df = df.copy()

    # Add any missing expected columns filled with NaN
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
            logger.debug("Added missing column '%s' for city '%s'.", col, city)

    # Enforce city name
    df["city"] = city

    # Strip whitespace from all string/object columns
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # Return only the expected columns (plus any extras that came with the file)
    ordered = [c for c in EXPECTED_COLUMNS if c in df.columns]
    extras = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    return df[ordered + extras]


def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values in the merged DataFrame using sensible defaults.

    Imputation strategy per column:

    * **price** – city-level median → global median
    * **aqi** – ``SYNTHETIC_AQI`` lookup by city → ``50`` as fallback
    * **review_scores_rating** – city-level median → ``4.0``
    * **minimum_nights** – ``1``
    * **availability_365** – ``180``
    * **number_of_reviews** – ``0``

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame (may span multiple cities) with potential NaN values.

    Returns
    -------
    pd.DataFrame
        DataFrame with NaN values filled according to the strategy above.
    """
    df = df.copy()

    def _log_imputed(col: str, before: int, after: int) -> None:
        imputed = before - after
        if imputed:
            logger.info("Imputed %d missing value(s) in column '%s'.", imputed, col)

    # ------------------------------------------------------------------
    # price
    # ------------------------------------------------------------------
    if "price" in df.columns:
        before = df["price"].isna().sum()
        df["price"] = df.groupby("city")["price"].transform(
            lambda s: s.fillna(s.median())
        )
        global_price_median = df["price"].median()
        df["price"] = df["price"].fillna(global_price_median)
        _log_imputed("price", before, df["price"].isna().sum())

    # ------------------------------------------------------------------
    # aqi
    # ------------------------------------------------------------------
    if "aqi" in df.columns:
        before = df["aqi"].isna().sum()
        df["aqi"] = df.apply(
            lambda row: SYNTHETIC_AQI.get(row["city"], 50)
            if pd.isna(row["aqi"])
            else row["aqi"],
            axis=1,
        )
        _log_imputed("aqi", before, df["aqi"].isna().sum())

    # ------------------------------------------------------------------
    # review_scores_rating
    # ------------------------------------------------------------------
    if "review_scores_rating" in df.columns:
        before = df["review_scores_rating"].isna().sum()
        df["review_scores_rating"] = df.groupby("city")["review_scores_rating"].transform(
            lambda s: s.fillna(s.median())
        )
        df["review_scores_rating"] = df["review_scores_rating"].fillna(4.0)
        _log_imputed("review_scores_rating", before, df["review_scores_rating"].isna().sum())

    # ------------------------------------------------------------------
    # minimum_nights
    # ------------------------------------------------------------------
    if "minimum_nights" in df.columns:
        before = df["minimum_nights"].isna().sum()
        df["minimum_nights"] = df["minimum_nights"].fillna(1)
        _log_imputed("minimum_nights", before, df["minimum_nights"].isna().sum())

    # ------------------------------------------------------------------
    # availability_365
    # ------------------------------------------------------------------
    if "availability_365" in df.columns:
        before = df["availability_365"].isna().sum()
        df["availability_365"] = df["availability_365"].fillna(180)
        _log_imputed("availability_365", before, df["availability_365"].isna().sum())

    # ------------------------------------------------------------------
    # number_of_reviews
    # ------------------------------------------------------------------
    if "number_of_reviews" in df.columns:
        before = df["number_of_reviews"].isna().sum()
        df["number_of_reviews"] = df["number_of_reviews"].fillna(0)
        _log_imputed("number_of_reviews", before, df["number_of_reviews"].isna().sum())

    return df


def load_city_csv(filepath: pathlib.Path, city: str) -> Optional[pd.DataFrame]:
    """Load, standardize, convert, and impute a single city CSV file.

    Steps applied in order:

    1. Read the CSV with ``pd.read_csv``.
    2. :func:`standardize_schema` – align columns and city name.
    3. :func:`convert_city_prices` – add ``price_inr`` column.
    4. :func:`impute_missing` – fill NaN values.
    5. Attach a ``source_file`` column with the filename (not full path).

    Parameters
    ----------
    filepath : pathlib.Path
        Absolute or relative path to the city's CSV file.
    city : str
        Human-readable city name inferred from the filename.

    Returns
    -------
    pd.DataFrame or None
        Processed DataFrame, or ``None`` if the file could not be loaded.
    """
    try:
        df = pd.read_csv(filepath, low_memory=False)
        logger.info("Loaded '%s' (%d rows, %d cols).", filepath.name, *df.shape)

        df = standardize_schema(df, city)
        df = convert_city_prices(df, city, price_col="price")
        df = impute_missing(df)
        df["source_file"] = filepath.name

        logger.info(
            "Processed city='%s': %d listings, price_inr range [%.2f, %.2f].",
            city,
            len(df),
            df["price_inr"].min() if "price_inr" in df.columns else float("nan"),
            df["price_inr"].max() if "price_inr" in df.columns else float("nan"),
        )
        return df

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load '%s': %s", filepath, exc, exc_info=True)
        return None


def merge_all_cities(
    raw_dir: str = "data/raw",
    output_path: str = "data/processed/merged_listings.csv",
) -> pd.DataFrame:
    """Merge all city CSV files from *raw_dir* into a single DataFrame.

    City names are inferred from filenames by:

    * Stripping the ``_listings.csv`` suffix (or just ``.csv`` if the suffix
      is absent).
    * Replacing underscores with spaces.
    * Title-casing the result.

    The merged DataFrame is saved to *output_path* (parent directories are
    created automatically).

    Parameters
    ----------
    raw_dir : str, optional
        Directory containing per-city CSV files.  Defaults to ``"data/raw"``.
    output_path : str, optional
        Destination path for the merged CSV.
        Defaults to ``"data/processed/merged_listings.csv"``.

    Returns
    -------
    pd.DataFrame
        Concatenated DataFrame of all successfully loaded city files.

    Raises
    ------
    FileNotFoundError
        If *raw_dir* does not exist.
    RuntimeError
        If no CSV files could be loaded successfully.
    """
    raw_path = pathlib.Path(raw_dir)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data directory not found: {raw_path.resolve()}")

    csv_files = sorted(raw_path.glob("*.csv"))
    if not csv_files:
        logger.warning("No CSV files found in '%s'.", raw_path.resolve())

    frames: list[pd.DataFrame] = []
    failed: list[str] = []

    for csv_file in csv_files:
        # Infer city name: "new_york_listings.csv" → "New York"
        stem = csv_file.stem  # filename without extension
        city_raw = stem.replace("_listings", "").replace("_", " ")
        city = city_raw.title()

        logger.info("--- Processing file: %s  (city: '%s') ---", csv_file.name, city)
        df = load_city_csv(csv_file, city)
        if df is not None:
            frames.append(df)
        else:
            failed.append(csv_file.name)

    if not frames:
        raise RuntimeError(
            "No city DataFrames could be loaded. "
            f"Failed files: {failed}"
        )

    merged = pd.concat(frames, ignore_index=True)
    merged.reset_index(drop=True, inplace=True)

    # Ensure output directory exists
    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    merged.to_csv(output_file, index=False)
    logger.info("Saved merged CSV → '%s'", output_file.resolve())

    # Summary statistics
    logger.info(
        "Merge complete: %d total listings across %d cities.",
        len(merged),
        merged["city"].nunique(),
    )
    logger.info("Columns: %s", list(merged.columns))
    if failed:
        logger.warning("Files that failed to load: %s", failed)

    numeric_cols = merged.select_dtypes(include=[np.number]).columns
    logger.info(
        "Numeric summary:\n%s",
        merged[numeric_cols].describe().to_string(),
    )

    return merged


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting data merge pipeline...")
    try:
        merged_df = merge_all_cities()
        print(f"\nMerge complete. Output shape: {merged_df.shape}")
        print(merged_df.head())
    except (FileNotFoundError, RuntimeError) as exc:
        logger.error("Pipeline failed: %s", exc)
        sys.exit(1)
