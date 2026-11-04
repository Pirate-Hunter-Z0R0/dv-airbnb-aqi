"""Quick smoke test for the clean-air-airbnb pipeline."""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "app"))

import matplotlib
matplotlib.use("Agg")
import pandas as pd

# --- currency_converter ---
from currency_converter import convert_to_inr, CITY_CURRENCY_MAP, EXCHANGE_RATES_TO_INR
print(f"[OK] currency_converter: {len(CITY_CURRENCY_MAP)} cities, {len(EXCHANGE_RATES_TO_INR)} currencies")
usd_rate = convert_to_inr(100, "USD")
print(f"     USD 100 = INR {usd_rate:.2f}")

# --- viz_modules ---
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
print("[OK] viz_modules: all 10 chart functions imported")

# --- processed data ---
data_path = os.path.join(ROOT, "data", "processed", "merged_listings.csv")
df = pd.read_csv(data_path)
print(f"[OK] merged_listings.csv: {len(df):,} rows x {df.shape[1]} cols, {df['city'].nunique()} cities")
print(f"     Columns: {list(df.columns)}")
print(f"     price_inr range: {df['price_inr'].min():.0f} - {df['price_inr'].max():.0f} INR")
print(f"     NaN count: {df.isnull().sum().sum()} remaining nulls")

# --- chart smoke test ---
import matplotlib.pyplot as plt
fig = plot_correlation_heatmap(df)
assert fig is not None, "correlation heatmap returned None"
print(f"[OK] plot_correlation_heatmap returned {type(fig).__name__}")
plt.close("all")

fig2 = plot_aqi_map_heatmap(df)
assert fig2 is not None
print(f"[OK] plot_aqi_map_heatmap returned {type(fig2).__name__}")
plt.close("all")

fig3 = plot_price_distribution(df)
assert fig3 is not None
print(f"[OK] plot_price_distribution returned {type(fig3).__name__}")
plt.close("all")

print()
print("=" * 40)
print("ALL CHECKS PASSED")
print("=" * 40)
