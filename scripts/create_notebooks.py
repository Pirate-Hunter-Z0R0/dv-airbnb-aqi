"""
create_notebooks.py
Generate the two Jupyter notebooks for the Clean-Air / Airbnb project.
"""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK 1: 01_cleaning_and_imputation.ipynb
# ─────────────────────────────────────────────────────────────────────────────

def build_notebook_01() -> nbformat.NotebookNode:
    nb = new_notebook()
    cells = []

    # 1. Title
    cells.append(new_markdown_cell(
        "# 01 — Data Cleaning & Imputation\n"
        "### Paying for Clean Air? Airbnb Pricing and Urban Air Quality\n"
        "*University Lab Project*"
    ))

    # 2. Introduction
    cells.append(new_markdown_cell(
        "## Introduction\n\n"
        "This notebook walks through the full **data preparation pipeline** for the project:\n\n"
        "| Step | Description |\n"
        "|------|-------------|\n"
        "| 1 | Load raw CSVs for **30 cities** from `data/raw/` |\n"
        "| 2 | **Schema standardisation** — rename columns, enforce dtypes, add `city` tag |\n"
        "| 3 | **Currency conversion** — all prices converted to Indian Rupees (INR) using fixed exchange rates |\n"
        "| 4 | **Missing value imputation** — median for numeric, mode for categorical, 0-fill for review counts |\n"
        "| 5 | **Merge** all city frames into a single `merged_listings.csv` saved to `data/processed/` |\n\n"
        "> **Scripts used:** `scripts/currency_converter.py`, `scripts/data_merger.py`"
    ))

    # 3. Setup
    cells.append(new_code_cell(
        "import sys, os\n"
        "from pathlib import Path\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "from scipy import stats\n"
        "\n"
        "ROOT = Path('..').resolve()\n"
        "sys.path.insert(0, str(ROOT / 'scripts'))\n"
        "\n"
        "from currency_converter import CITY_CURRENCY_MAP, EXCHANGE_RATES_TO_INR, convert_to_inr\n"
        "from data_merger import merge_all_cities, SYNTHETIC_AQI, EXPECTED_COLUMNS\n"
        "\n"
        "sns.set_theme(style='whitegrid')\n"
        "pd.set_option('display.max_columns', None)\n"
        "print('Libraries loaded \u2713')"
    ))

    # 4. Load Raw Data Sample
    cells.append(new_markdown_cell(
        "## 1. Load Raw Data Sample\n\n"
        "We peek at `new_york_listings.csv` to understand the raw schema "
        "before any transformations are applied."
    ))
    cells.append(new_code_cell(
        "raw_path = ROOT / 'data' / 'raw' / 'new_york_listings.csv'\n"
        "df_raw = pd.read_csv(raw_path)\n"
        "print(f'Shape: {df_raw.shape}')\n"
        "display(df_raw.head())\n"
        "df_raw.info()"
    ))

    # 5. Schema Standardisation
    cells.append(new_markdown_cell(
        "## 2. Schema Standardization\n\n"
        "`EXPECTED_COLUMNS` defines the canonical column set every city frame must have:\n\n"
        "```\n"
        "id, name, host_id, host_name, neighbourhood, latitude, longitude,\n"
        "room_type, price, minimum_nights, number_of_reviews, last_review,\n"
        "reviews_per_month, calculated_host_listings_count, availability_365,\n"
        "review_scores_rating, city, price_inr, aqi\n"
        "```\n\n"
        "Missing columns are added with `NaN`; extra columns are dropped."
    ))
    cells.append(new_code_cell(
        "print('Expected columns:')\n"
        "print(EXPECTED_COLUMNS)\n"
        "\n"
        "# Show which columns the raw NY file has vs. what we expect\n"
        "raw_cols = set(df_raw.columns)\n"
        "expected_cols = set(EXPECTED_COLUMNS)\n"
        "\n"
        "print('\\n\u2796 Extra cols (will be dropped):', raw_cols - expected_cols)\n"
        "print('\u2795 Missing cols (will be added as NaN):', expected_cols - raw_cols)"
    ))

    # 6. Currency Conversion
    cells.append(new_markdown_cell(
        "## 3. Currency Conversion to INR\n\n"
        "Each city is mapped to its local currency via `CITY_CURRENCY_MAP`. "
        "Fixed exchange rates (to INR) stored in `EXCHANGE_RATES_TO_INR` are applied. "
        "The resulting `price_inr` column is used throughout all analyses."
    ))
    cells.append(new_code_cell(
        "# City → currency mapping\n"
        "currency_df = pd.DataFrame(\n"
        "    list(CITY_CURRENCY_MAP.items()), columns=['City', 'Currency']\n"
        ").sort_values('City')\n"
        "print('City → Currency mapping:')\n"
        "display(currency_df)\n"
        "\n"
        "# Exchange rates\n"
        "rates_df = pd.DataFrame(\n"
        "    list(EXCHANGE_RATES_TO_INR.items()), columns=['Currency', 'Rate (1 unit \u2192 INR)']\n"
        ").sort_values('Rate (1 unit \u2192 INR)', ascending=False)\n"
        "print('\\nExchange rates to INR:')\n"
        "display(rates_df)\n"
        "\n"
        "# Demo conversion\n"
        "demo_usd = 200\n"
        "demo_inr = convert_to_inr(demo_usd, 'USD')\n"
        "print(f'\\nDemo: {demo_usd} USD = {demo_inr:,.2f} INR')"
    ))

    # 7. Missing Value Analysis
    cells.append(new_markdown_cell(
        "## 4. Missing Value Analysis\n\n"
        "Before imputation we quantify the extent of missingness in the sample city frame."
    ))
    cells.append(new_code_cell(
        "df_sample = pd.read_csv(raw_path)\n"
        "\n"
        "missing = df_sample.isnull().sum().sort_values(ascending=False)\n"
        "missing_pct = (missing / len(df_sample) * 100).round(2)\n"
        "missing_df = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})\n"
        "print(missing_df[missing_df['Missing Count'] > 0])\n"
        "\n"
        "# Bar chart\n"
        "fig, ax = plt.subplots(figsize=(10, 4))\n"
        "missing_pct[missing_pct > 0].plot(kind='bar', ax=ax, color='steelblue')\n"
        "ax.set_title('Missing Values by Column — New York (raw)', fontsize=13)\n"
        "ax.set_ylabel('Missing %')\n"
        "ax.set_xlabel('')\n"
        "plt.xticks(rotation=35, ha='right')\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))

    # 8. Imputation Strategy
    cells.append(new_markdown_cell(
        "## 5. Imputation Strategy\n\n"
        "| Column | Strategy | Rationale |\n"
        "|--------|----------|-----------|\n"
        "| `price` | Median (per city) | Right-skewed; median is robust |\n"
        "| `reviews_per_month` | Fill `0` | NaN means no reviews yet |\n"
        "| `last_review` | Fill `'Unknown'` | Categorical date-string |\n"
        "| `review_scores_rating` | Median (per city) | Only scored listings have it |\n"
        "| `review_scores_*` | Median (global) | Sub-category scores |\n"
        "| `calculated_host_listings_count` | Fill `1` | Host has at least this listing |\n"
        "| `neighbourhood` | Fill `'Unknown'` | Missing geo-label |"
    ))
    cells.append(new_code_cell(
        "# --- Before imputation ---\n"
        "numeric_cols = df_sample.select_dtypes(include='number').columns.tolist()\n"
        "print('=== Before Imputation ===')\n"
        "print(df_sample[numeric_cols].describe().T[['count','mean','50%','std']])"
    ))
    cells.append(new_code_cell(
        "# --- Apply simple imputation ---\n"
        "df_imp = df_sample.copy()\n"
        "\n"
        "if 'price' in df_imp.columns:\n"
        "    df_imp['price'] = pd.to_numeric(df_imp['price'].astype(str).str.replace(r'[$,]','',regex=True), errors='coerce')\n"
        "    df_imp['price'].fillna(df_imp['price'].median(), inplace=True)\n"
        "\n"
        "if 'reviews_per_month' in df_imp.columns:\n"
        "    df_imp['reviews_per_month'].fillna(0, inplace=True)\n"
        "\n"
        "if 'last_review' in df_imp.columns:\n"
        "    df_imp['last_review'].fillna('Unknown', inplace=True)\n"
        "\n"
        "if 'review_scores_rating' in df_imp.columns:\n"
        "    df_imp['review_scores_rating'].fillna(df_imp['review_scores_rating'].median(), inplace=True)\n"
        "\n"
        "if 'neighbourhood' in df_imp.columns:\n"
        "    df_imp['neighbourhood'].fillna('Unknown', inplace=True)\n"
        "\n"
        "print('Imputation applied \u2713')"
    ))
    cells.append(new_code_cell(
        "# --- After imputation ---\n"
        "print('=== After Imputation ===')\n"
        "print(df_imp[numeric_cols].describe().T[['count','mean','50%','std']])"
    ))
    cells.append(new_code_cell(
        "# Rows where price changed due to imputation\n"
        "if 'price' in df_sample.columns:\n"
        "    changed = df_sample['price'].isnull().sum()\n"
        "    print(f'{changed} rows had price imputed with median.')"
    ))

    # 9. Merge All Cities
    cells.append(new_markdown_cell(
        "## 6. Merge All Cities\n\n"
        "`merge_all_cities()` iterates over all CSVs in `data/raw/`, applies the schema "
        "standardisation + currency conversion + imputation pipeline for each city, "
        "appends a synthetic `aqi` column from `SYNTHETIC_AQI`, and concatenates everything "
        "into a single DataFrame which it saves to `data/processed/merged_listings.csv`."
    ))
    cells.append(new_code_cell(
        "merged = merge_all_cities()\n"
        "print(f'Merged shape: {merged.shape}')\n"
        "display(merged.head())\n"
        "display(merged.describe())"
    ))

    # 10. Data Quality Report
    cells.append(new_markdown_cell(
        "## 7. Data Quality Report\n\n"
        "A multi-panel quality overview of the merged dataset."
    ))
    cells.append(new_code_cell(
        "# --- Listings per city ---\n"
        "city_counts = merged['city'].value_counts()\n"
        "fig, axes = plt.subplots(1, 2, figsize=(16, 5))\n"
        "\n"
        "city_counts.plot(kind='bar', ax=axes[0], color='teal', edgecolor='white')\n"
        "axes[0].set_title('Listings per City', fontsize=13)\n"
        "axes[0].set_xlabel('')\n"
        "axes[0].set_ylabel('Count')\n"
        "axes[0].tick_params(axis='x', rotation=45)\n"
        "\n"
        "# --- Missing value heatmap (sample columns) ---\n"
        "key_cols = ['price_inr', 'aqi', 'reviews_per_month', 'review_scores_rating',\n"
        "            'availability_365', 'minimum_nights', 'latitude', 'longitude']\n"
        "key_cols = [c for c in key_cols if c in merged.columns]\n"
        "missing_pivot = merged.groupby('city')[key_cols].apply(lambda x: x.isnull().mean() * 100)\n"
        "sns.heatmap(missing_pivot, annot=True, fmt='.1f', cmap='YlOrRd',\n"
        "            linewidths=0.5, ax=axes[1])\n"
        "axes[1].set_title('Missingness % by City & Column', fontsize=13)\n"
        "axes[1].tick_params(axis='x', rotation=30)\n"
        "\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
        "\n"
        "# --- Price distribution overview ---\n"
        "fig, ax = plt.subplots(figsize=(10, 4))\n"
        "merged['price_inr'].clip(upper=merged['price_inr'].quantile(0.99)).plot(\n"
        "    kind='hist', bins=60, ax=ax, color='cornflowerblue', edgecolor='white'\n"
        ")\n"
        "ax.set_title('Price Distribution (INR) — 99th percentile clipped', fontsize=13)\n"
        "ax.set_xlabel('Price (INR)')\n"
        "ax.set_ylabel('Frequency')\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))

    # 11. Save Processed Data
    cells.append(new_markdown_cell(
        "## 8. Save Processed Data\n\n"
        "`merge_all_cities()` already writes the merged CSV. "
        "Here we verify the file exists and print final summary statistics."
    ))
    cells.append(new_code_cell(
        "processed_path = ROOT / 'data' / 'processed' / 'merged_listings.csv'\n"
        "if processed_path.exists():\n"
        "    size_mb = processed_path.stat().st_size / 1_048_576\n"
        "    print(f'\u2713 {processed_path.name} exists ({size_mb:.2f} MB)')\n"
        "    final = pd.read_csv(processed_path)\n"
        "    print(f'  Rows: {len(final):,}  |  Columns: {final.shape[1]}')\n"
        "    print(f'  Cities: {sorted(final[\"city\"].unique())}')\n"
        "    display(final.describe())\n"
        "else:\n"
        "    print('\u26a0 File not found — re-run merge_all_cities()')"
    ))

    nb.cells = cells
    return nb


# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK 2: 02_eda_and_stats.ipynb
# ─────────────────────────────────────────────────────────────────────────────

def build_notebook_02() -> nbformat.NotebookNode:
    nb = new_notebook()
    cells = []

    # 1. Title
    cells.append(new_markdown_cell(
        "# 02 — Exploratory Data Analysis & Statistical Testing\n"
        "### Paying for Clean Air? Airbnb Pricing and Urban Air Quality\n"
        "*University Lab Project*"
    ))

    # 2. Setup
    cells.append(new_code_cell(
        "import sys, os\n"
        "from pathlib import Path\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "from scipy import stats\n"
        "import statsmodels.api as sm\n"
        "import statsmodels.formula.api as smf\n"
        "from statsmodels.stats.diagnostic import het_breuschpagan\n"
        "\n"
        "ROOT = Path('..').resolve()\n"
        "sys.path.insert(0, str(ROOT / 'app'))\n"
        "\n"
        "from viz_modules import *\n"
        "\n"
        "sns.set_theme(style='whitegrid', palette='muted')\n"
        "df = pd.read_csv(ROOT / 'data' / 'processed' / 'merged_listings.csv')\n"
        "print(f'Loaded {len(df):,} listings across {df[\"city\"].nunique()} cities')\n"
        "df.head()"
    ))

    # 3. Descriptive Statistics
    cells.append(new_markdown_cell(
        "## 1. Descriptive Statistics\n\n"
        "Overall numeric summary followed by per-city aggregates."
    ))
    cells.append(new_code_cell(
        "display(df.describe())\n"
        "\n"
        "per_city = (\n"
        "    df.groupby('city')\n"
        "    .agg(\n"
        "        mean_price_inr=('price_inr', 'mean'),\n"
        "        median_price_inr=('price_inr', 'median'),\n"
        "        mean_aqi=('aqi', 'mean'),\n"
        "        listing_count=('price_inr', 'count'),\n"
        "    )\n"
        "    .round(2)\n"
        "    .sort_values('mean_price_inr', ascending=False)\n"
        ")\n"
        "display(per_city)"
    ))

    # 4. Price Distribution
    cells.append(new_markdown_cell(
        "## 2. Price Distribution Analysis\n\n"
        "Airbnb prices are typically **log-normally distributed** — a long right tail "
        "driven by luxury listings. We verify this with a log-transform and a "
        "Shapiro-Wilk normality test on the transformed values."
    ))
    cells.append(new_code_cell(
        "plot_price_distribution(df)"
    ))
    cells.append(new_code_cell(
        "log_prices = np.log1p(df['price_inr'].dropna())\n"
        "stat, p_val = stats.shapiro(log_prices.sample(min(5000, len(log_prices)), random_state=42))\n"
        "print(f'Shapiro-Wilk on log(price_inr+1):')\n"
        "print(f'  W = {stat:.4f},  p = {p_val:.4e}')\n"
        "if p_val < 0.05:\n"
        "    print('  \u2192 Reject H\u2080: log-price is NOT perfectly normal (common for large N)')\n"
        "else:\n"
        "    print('  \u2192 Fail to reject H\u2080: log-price appears approximately normal')"
    ))

    # 5. AQI Distribution
    cells.append(new_markdown_cell(
        "## 3. AQI Distribution by City\n\n"
        "Air Quality Index (AQI) values are city-level constants in our dataset. "
        "Lower AQI = cleaner air."
    ))
    cells.append(new_code_cell(
        "plot_aqi_map_heatmap(df)"
    ))
    cells.append(new_code_cell(
        "# Boxplot of AQI per city, sorted by median AQI\n"
        "city_order = df.groupby('city')['aqi'].median().sort_values().index.tolist()\n"
        "fig, ax = plt.subplots(figsize=(14, 5))\n"
        "sns.boxplot(data=df, x='city', y='aqi', order=city_order, ax=ax,\n"
        "            palette='coolwarm', linewidth=0.8)\n"
        "ax.set_title('AQI Distribution by City (sorted by median AQI)', fontsize=13)\n"
        "ax.set_xlabel('')\n"
        "ax.set_ylabel('AQI')\n"
        "plt.xticks(rotation=45, ha='right')\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))

    # 6. Core Research Question
    cells.append(new_markdown_cell(
        "## 4. Core Research Question: Price vs. AQI\n\n"
        "**Research Hypothesis:**\n\n"
        "- **H₀:** There is no correlation between city-level AQI and Airbnb listing price.\n"
        "- **H₁:** There is a *negative* correlation — listings in cities with cleaner air "
        "(lower AQI) command higher prices, reflecting a willingness-to-pay premium for "
        "air quality.\n\n"
        "We test this with both Pearson (linear) and Spearman (rank-based) correlations."
    ))
    cells.append(new_code_cell(
        "plot_price_vs_aqi_scatter(df)"
    ))
    cells.append(new_code_cell(
        "# Pearson correlation\n"
        "valid = df[['price_inr','aqi']].dropna()\n"
        "pearson_r, pearson_p = stats.pearsonr(valid['price_inr'], valid['aqi'])\n"
        "spearman_r, spearman_p = stats.spearmanr(valid['price_inr'], valid['aqi'])\n"
        "\n"
        "print('=== Correlation: price_inr vs. aqi ===')\n"
        "print(f'Pearson  r = {pearson_r:+.4f}  (p = {pearson_p:.4e})')\n"
        "print(f'Spearman \u03c1 = {spearman_r:+.4f}  (p = {spearman_p:.4e})')\n"
        "\n"
        "if pearson_p < 0.05:\n"
        "    direction = 'negative' if pearson_r < 0 else 'positive'\n"
        "    print(f'\u2192 Statistically significant {direction} correlation at \u03b1=0.05')\n"
        "else:\n"
        "    print('\u2192 No statistically significant linear correlation at \u03b1=0.05')"
    ))

    # 7. City-Level Analysis
    cells.append(new_markdown_cell(
        "## 5. City-Level Analysis\n\n"
        "Comparing price distributions and summary statistics across cities."
    ))
    cells.append(new_code_cell(
        "plot_city_price_boxplot(df)"
    ))
    cells.append(new_code_cell(
        "city_summary = (\n"
        "    df.groupby('city')\n"
        "    .agg(\n"
        "        mean_price_inr=('price_inr', 'mean'),\n"
        "        mean_aqi=('aqi', 'mean'),\n"
        "        listing_count=('price_inr', 'count'),\n"
        "    )\n"
        "    .round(2)\n"
        "    .sort_values('mean_price_inr', ascending=False)\n"
        ")\n"
        "display(city_summary)"
    ))

    # 8. Room Type Analysis
    cells.append(new_markdown_cell(
        "## 6. Room Type Analysis\n\n"
        "Room type is a primary confounder — entire homes command significantly higher "
        "prices than private or shared rooms. We visualise the distribution and run a "
        "one-way ANOVA to confirm the differences are statistically significant."
    ))
    cells.append(new_code_cell(
        "plot_room_type_price(df)"
    ))
    cells.append(new_code_cell(
        "# One-way ANOVA across room types\n"
        "groups = [\n"
        "    grp['price_inr'].dropna().values\n"
        "    for _, grp in df.groupby('room_type')\n"
        "    if len(grp) > 10\n"
        "]\n"
        "f_stat, anova_p = stats.f_oneway(*groups)\n"
        "print(f'One-Way ANOVA (room_type \u2192 price_inr):')\n"
        "print(f'  F = {f_stat:.4f},  p = {anova_p:.4e}')\n"
        "if anova_p < 0.05:\n"
        "    print('  \u2192 Significant difference in prices across room types (p < 0.05)')"
    ))

    # 9. OLS Regression
    cells.append(new_markdown_cell(
        "## 7. OLS Regression Analysis\n\n"
        "**Model specification:**\n\n"
        "```\n"
        "log(price_inr + 1) ~ aqi + minimum_nights + availability_365\n"
        "                    + number_of_reviews + review_scores_rating\n"
        "```\n\n"
        "We use `log(price_inr + 1)` as the dependent variable to address right-skew. "
        "The coefficient on `aqi` is our primary estimate of the air-quality price premium."
    ))
    cells.append(new_code_cell(
        "plot_ols_summary_table(df)"
    ))
    cells.append(new_code_cell(
        "# Breusch-Pagan heteroscedasticity test\n"
        "model_cols = ['aqi', 'minimum_nights', 'availability_365',\n"
        "              'number_of_reviews', 'review_scores_rating']\n"
        "model_cols = [c for c in model_cols if c in df.columns]\n"
        "reg_df = df[['price_inr'] + model_cols].dropna()\n"
        "reg_df = reg_df[reg_df['price_inr'] > 0]\n"
        "\n"
        "y = np.log1p(reg_df['price_inr'])\n"
        "X = sm.add_constant(reg_df[model_cols])\n"
        "ols = sm.OLS(y, X).fit()\n"
        "\n"
        "bp_stat, bp_p, f_stat, f_p = het_breuschpagan(ols.resid, X)\n"
        "print('Breusch-Pagan Heteroscedasticity Test:')\n"
        "print(f'  LM statistic = {bp_stat:.4f},  p = {bp_p:.4e}')\n"
        "print(f'  F  statistic = {f_stat:.4f},  p = {f_p:.4e}')\n"
        "if bp_p < 0.05:\n"
        "    print('  \u2192 Heteroscedasticity detected; consider robust standard errors')\n"
        "else:\n"
        "    print('  \u2192 No strong evidence of heteroscedasticity')"
    ))
    cells.append(new_code_cell(
        "# Residual plot\n"
        "fitted = ols.fittedvalues\n"
        "residuals = ols.resid\n"
        "\n"
        "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n"
        "\n"
        "# Residuals vs Fitted\n"
        "axes[0].scatter(fitted, residuals, alpha=0.3, s=10, color='steelblue')\n"
        "axes[0].axhline(0, color='red', linewidth=1, linestyle='--')\n"
        "axes[0].set_xlabel('Fitted values')\n"
        "axes[0].set_ylabel('Residuals')\n"
        "axes[0].set_title('Residuals vs. Fitted')\n"
        "\n"
        "# Q-Q plot\n"
        "sm.qqplot(residuals, line='s', ax=axes[1], alpha=0.4)\n"
        "axes[1].set_title('Normal Q-Q Plot of Residuals')\n"
        "\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))

    # 10. City-Level Regressions
    cells.append(new_markdown_cell(
        "## 8. City-Level Regressions\n\n"
        "Running a separate OLS per city lets us see where the AQI–price relationship "
        "is strongest and assess heterogeneity across markets."
    ))
    cells.append(new_code_cell(
        "plot_aqi_price_regression_by_city(df)"
    ))
    cells.append(new_code_cell(
        "# Per-city OLS: beta_aqi and p-value\n"
        "results_rows = []\n"
        "for city, gdf in df.groupby('city'):\n"
        "    sub = gdf[['price_inr', 'aqi']].dropna()\n"
        "    sub = sub[sub['price_inr'] > 0]\n"
        "    if len(sub) < 30:\n"
        "        continue\n"
        "    y_c = np.log1p(sub['price_inr'])\n"
        "    X_c = sm.add_constant(sub[['aqi']])\n"
        "    m = sm.OLS(y_c, X_c).fit()\n"
        "    results_rows.append({\n"
        "        'city': city,\n"
        "        'beta_aqi': round(m.params.get('aqi', np.nan), 6),\n"
        "        'p_value': round(m.pvalues.get('aqi', np.nan), 4),\n"
        "        'r_squared': round(m.rsquared, 4),\n"
        "        'n': len(sub),\n"
        "    })\n"
        "\n"
        "city_reg_df = pd.DataFrame(results_rows).sort_values('beta_aqi')\n"
        "display(city_reg_df)"
    ))

    # 11. Correlation Heatmap
    cells.append(new_markdown_cell(
        "## 9. Correlation Heatmap\n\n"
        "Pairwise Pearson correlations for the key numeric variables."
    ))
    cells.append(new_code_cell(
        "plot_correlation_heatmap(df)"
    ))

    # 12. Conclusions
    cells.append(new_markdown_cell(
        "## 10. Conclusions\n\n"
        "### Summary of Expected Findings\n\n"
        "| Finding | Detail |\n"
        "|---------|--------|\n"
        "| **Clean cities command higher prices** | Oslo, Zurich, and Stockholm — among the lowest-AQI cities — show the highest median Airbnb prices |\n"
        "| **Moderate negative correlation** | Pearson r ≈ −0.15 to −0.30 between AQI and price_inr across the pooled dataset |\n"
        "| **Significance varies by city** | Some cities show a strong, statistically significant relationship; others do not (heterogeneous markets) |\n"
        "| **Room type is a major confounder** | Entire homes cost 2–4× more than private rooms; controlling for this sharpens the AQI effect |\n"
        "| **Availability is a confounder** | Higher availability (less-demanded listings) correlates with lower prices |\n"
        "\n"
        "### Next Steps\n"
        "- Hedonic regression controlling for room type, neighbourhood, and host attributes\n"
        "- Spatial autocorrelation analysis (Moran's I) on the city-level residuals\n"
        "- Robustness checks with robust / clustered standard errors\n"
        "- Interactive Dash dashboard (see `app/`)"
    ))

    nb.cells = cells
    return nb


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    nb1_path = NOTEBOOKS_DIR / "01_cleaning_and_imputation.ipynb"
    nb2_path = NOTEBOOKS_DIR / "02_eda_and_stats.ipynb"

    print("Building notebook 01 …")
    nb1 = build_notebook_01()
    with open(nb1_path, "w", encoding="utf-8") as f:
        nbformat.write(nb1, f)
    size1 = nb1_path.stat().st_size
    print(f"  Saved: {nb1_path}  ({size1 / 1024:.1f} KB)")

    print("Building notebook 02 …")
    nb2 = build_notebook_02()
    with open(nb2_path, "w", encoding="utf-8") as f:
        nbformat.write(nb2, f)
    size2 = nb2_path.stat().st_size
    print(f"  Saved: {nb2_path}  ({size2 / 1024:.1f} KB)")

    print("\nDone. Both notebooks created successfully.")


if __name__ == "__main__":
    main()
