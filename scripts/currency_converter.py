"""
Currency conversion utilities for converting 30-city Airbnb prices to Indian Rupees (INR).
Uses static exchange rates (base date: 2024-01-01) with a fallback synthetic rate map.
"""

from __future__ import annotations

import warnings
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Static exchange-rate table (1 unit of foreign currency → INR)
# Base date: 2024-01-01
# ---------------------------------------------------------------------------
EXCHANGE_RATES_TO_INR: dict[str, float] = {
    "USD": 83.12,
    "EUR": 90.45,
    "GBP": 105.32,
    "THB": 2.37,
    "AUD": 54.21,
    "CAD": 61.88,
    "CHF": 97.15,
    "SGD": 62.44,
    "HKD": 10.63,
    "NOK": 8.05,
    "SEK": 7.98,
    "JPY": 0.56,
    "TWD": 2.65,
    "BRL": 16.97,
    "ARS": 0.10,
    "CLP": 0.097,
    "ZAR": 4.48,
    "TRY": 2.87,
    "INR": 1.0,
    "DKK": 12.14,
    "PHP": 1.49,
    "IDR": 0.0054,
    "MXN": 4.91,
    "PLN": 20.81,
    "CZK": 3.74,
    "HUF": 0.23,
    "RON": 18.22,
    "ILS": 22.51,
    "AED": 22.63,
    "SAR": 22.16,
    # Additional currencies required by CITY_CURRENCY_MAP
    "COP": 0.021,
    "CNY": 11.58,
    "HUF": 0.23,
}

# ---------------------------------------------------------------------------
# City → currency code mapping (45 cities)
# ---------------------------------------------------------------------------
CITY_CURRENCY_MAP: dict[str, str] = {
    "Amsterdam": "EUR",
    "Bangkok": "THB",
    "Barcelona": "EUR",
    "Beijing": "CNY",
    "Berlin": "EUR",
    "Bogota": "COP",
    "Brisbane": "AUD",
    "Brussels": "EUR",
    "Budapest": "HUF",
    "Buenos Aires": "ARS",
    "Cape Town": "ZAR",
    "Chicago": "USD",
    "Copenhagen": "DKK",
    "Dallas": "USD",
    "Delhi": "INR",
    "Dublin": "EUR",
    "Edinburgh": "GBP",
    "Goa": "INR",
    "Hawaii": "USD",
    "Hong Kong": "HKD",
    "Istanbul": "TRY",
    "Lisbon": "EUR",
    "London": "GBP",
    "Madrid": "EUR",
    "Milan": "EUR",
    "Montreal": "CAD",
    "Mumbai": "INR",
    "Munich": "EUR",
    "New York": "USD",
    "Oslo": "NOK",
    "Ottawa": "CAD",
    "Paris": "EUR",
    "Rome": "EUR",
    "Sao Paulo": "BRL",
    "Santiago": "CLP",
    "Shanghai": "CNY",
    "Singapore": "SGD",
    "Stockholm": "SEK",
    "Sydney": "AUD",
    "Taipei": "TWD",
    "Tokyo": "JPY",
    "Toronto": "CAD",
    "Valencia": "EUR",
    "Venice": "EUR",
    "Zurich": "CHF",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert_to_inr(price: float, currency_code: str) -> float:
    """Convert a price from the given currency to Indian Rupees (INR).

    Parameters
    ----------
    price : float
        The monetary amount in the source currency.
    currency_code : str
        ISO 4217 currency code (e.g. ``"USD"``, ``"EUR"``).

    Returns
    -------
    float
        Equivalent amount in INR using the static exchange-rate table.
        If *currency_code* is not found in ``EXCHANGE_RATES_TO_INR``, the
        original *price* is returned unchanged and a warning is printed.

    Notes
    -----
    Exchange rates are fixed at 2024-01-01 and are **not** fetched live.
    """
    rate = EXCHANGE_RATES_TO_INR.get(currency_code)
    if rate is None:
        warnings.warn(
            f"Currency code '{currency_code}' not found in EXCHANGE_RATES_TO_INR. "
            "Returning original price without conversion.",
            UserWarning,
            stacklevel=2,
        )
        print(
            f"[currency_converter] WARNING: Unknown currency '{currency_code}'. "
            "Price returned as-is."
        )
        return float(price)
    return float(price) * rate


def convert_city_prices(
    df: pd.DataFrame,
    city: str,
    price_col: str = "price",
) -> pd.DataFrame:
    """Add a ``price_inr`` column to a city-level Airbnb DataFrame.

    Looks up the city's local currency from ``CITY_CURRENCY_MAP`` and applies
    :func:`convert_to_inr` element-wise on *price_col*, storing the result in
    a new ``price_inr`` column.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at minimum the column specified by *price_col*.
    city : str
        City name matching a key in ``CITY_CURRENCY_MAP``.
    price_col : str, optional
        Name of the column holding local-currency prices.  Defaults to
        ``"price"``.

    Returns
    -------
    pd.DataFrame
        The input DataFrame with an additional ``price_inr`` column.  The
        original DataFrame is **not** modified in-place; a copy is returned.

    Raises
    ------
    KeyError
        If *price_col* does not exist in *df*.
    """
    df = df.copy()

    currency_code = CITY_CURRENCY_MAP.get(city)
    if currency_code is None:
        warnings.warn(
            f"City '{city}' not found in CITY_CURRENCY_MAP. "
            "Defaulting to INR (1:1 conversion).",
            UserWarning,
            stacklevel=2,
        )
        currency_code = "INR"

    df["price_inr"] = df[price_col].apply(
        lambda p: convert_to_inr(float(p), currency_code)
        if pd.notna(p)
        else float("nan")
    )
    return df


def get_exchange_rate(currency_code: str) -> Optional[float]:
    """Return the INR exchange rate for the given currency code.

    Parameters
    ----------
    currency_code : str
        ISO 4217 currency code (e.g. ``"USD"``, ``"JPY"``).

    Returns
    -------
    float or None
        The INR equivalent of 1 unit of *currency_code*, or ``None`` if the
        code is not present in ``EXCHANGE_RATES_TO_INR``.
    """
    return EXCHANGE_RATES_TO_INR.get(currency_code)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    usd_amount = 100.0
    eur_amount = 50.0

    inr_from_usd = convert_to_inr(usd_amount, "USD")
    inr_from_eur = convert_to_inr(eur_amount, "EUR")

    print(f"USD {usd_amount:.2f}  →  INR {inr_from_usd:.2f}  "
          f"(rate: {EXCHANGE_RATES_TO_INR['USD']})")
    print(f"EUR {eur_amount:.2f}  →  INR {inr_from_eur:.2f}  "
          f"(rate: {EXCHANGE_RATES_TO_INR['EUR']})")
