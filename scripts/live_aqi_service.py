"""
live_aqi_service.py
===================
Real-time Air Quality fetcher using the free Open-Meteo Air Quality API.
Fetches real-time US AQI, PM2.5, and PM10 across 45 global cities.
Includes memory caching to avoid redundant HTTP requests during user interaction.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

# Representative latitude & longitude centers for all 45 cities
CITY_COORDINATES: Dict[str, Dict[str, float]] = {
    "Amsterdam":    {"lat": 52.3676, "lon": 4.9041},
    "Bangkok":      {"lat": 13.7563, "lon": 100.5018},
    "Barcelona":    {"lat": 41.3851, "lon": 2.1734},
    "Beijing":      {"lat": 39.9042, "lon": 116.4074},
    "Berlin":       {"lat": 52.5200, "lon": 13.4050},
    "Bogota":       {"lat": 4.7110,  "lon": -74.0721},
    "Brisbane":     {"lat": -27.4698,"lon": 153.0251},
    "Brussels":     {"lat": 50.8503, "lon": 4.3517},
    "Budapest":     {"lat": 47.4979, "lon": 19.0402},
    "Buenos Aires": {"lat": -34.6037,"lon": -58.3816},
    "Cape Town":    {"lat": -33.9249,"lon": 18.4241},
    "Chicago":      {"lat": 41.8781, "lon": -87.6298},
    "Copenhagen":   {"lat": 55.6761, "lon": 12.5683},
    "Dallas":       {"lat": 32.7767, "lon": -96.7970},
    "Delhi":        {"lat": 28.6139, "lon": 77.2090},
    "Dublin":       {"lat": 53.3498, "lon": -6.2603},
    "Edinburgh":    {"lat": 55.9533, "lon": -3.1883},
    "Goa":          {"lat": 15.2993, "lon": 74.1240},
    "Hawaii":       {"lat": 21.3069, "lon": -157.8583},
    "Hong Kong":    {"lat": 22.3193, "lon": 114.1694},
    "Istanbul":     {"lat": 41.0082, "lon": 28.9784},
    "Lisbon":       {"lat": 38.7169, "lon": -9.1399},
    "London":       {"lat": 51.5074, "lon": -0.1278},
    "Madrid":       {"lat": 40.4168, "lon": -3.7038},
    "Milan":        {"lat": 45.4654, "lon": 9.1859},
    "Montreal":     {"lat": 45.5017, "lon": -73.5673},
    "Mumbai":       {"lat": 19.0760, "lon": 72.8777},
    "Munich":       {"lat": 48.1351, "lon": 11.5820},
    "New York":     {"lat": 40.7128, "lon": -74.0060},
    "Oslo":         {"lat": 59.9139, "lon": 10.7522},
    "Ottawa":       {"lat": 45.4215, "lon": -75.6972},
    "Paris":        {"lat": 48.8566, "lon": 2.3522},
    "Rome":         {"lat": 41.9028, "lon": 12.4964},
    "Sao Paulo":    {"lat": -23.5505,"lon": -46.6333},
    "Santiago":     {"lat": -33.4489,"lon": -70.6693},
    "Shanghai":     {"lat": 31.2304, "lon": 121.4737},
    "Singapore":    {"lat": 1.3521,  "lon": 103.8198},
    "Stockholm":    {"lat": 59.3293, "lon": 18.0686},
    "Sydney":       {"lat": -33.8688,"lon": 151.2093},
    "Taipei":       {"lat": 25.0330, "lon": 121.5654},
    "Tokyo":        {"lat": 35.6762, "lon": 139.6503},
    "Toronto":      {"lat": 43.6532, "lon": -79.3832},
    "Valencia":     {"lat": 39.4699, "lon": -0.3763},
    "Venice":       {"lat": 45.4408, "lon": 12.3155},
    "Zurich":       {"lat": 47.3769, "lon": 8.5417},
}

_LIVE_CACHE: Dict[str, Dict[str, Any]] = {}


def fetch_live_aqi_for_city(city: str) -> Optional[Dict[str, Any]]:
    """Fetch live air quality for a single city from Open-Meteo."""
    if city in _LIVE_CACHE:
        return _LIVE_CACHE[city]

    coords = CITY_COORDINATES.get(city)
    if not coords:
        return None

    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={coords['lat']}&longitude={coords['lon']}&current=us_aqi,pm2_5,pm10"
    )

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            result = {
                "city": city,
                "us_aqi": current.get("us_aqi", None),
                "pm2_5": current.get("pm2_5", None),
                "pm10": current.get("pm10", None),
                "time": current.get("time", ""),
            }
            _LIVE_CACHE[city] = result
            return result
    except Exception as e:
        logger.warning("Failed to fetch live AQI for %s: %s", city, e)

    return None


def fetch_all_live_aqi() -> Dict[str, Dict[str, Any]]:
    """Batch fetch live air quality across all cities in parallel."""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_live_aqi_for_city, CITY_COORDINATES.keys()))

    return {r["city"]: r for r in results if r is not None}
