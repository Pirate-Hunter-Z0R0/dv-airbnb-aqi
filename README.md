# 🌿 Paying for Clean Air? Airbnb Pricing and Urban Air Quality

> **University Lab Project** investigating the econometric relationship between urban air quality (AQI) and Airbnb nightly prices across **45 global metropolitan areas**. Styled with an editorial **Inside Airbnb** aesthetic.

---

## 🚀 Quick Start Guide (For Collaborators & Friends)

Follow these simple steps in order to run the project on your computer.

### Step 1: Prerequisites
Make sure you have installed on your machine:
- **Python 3.10+** (Python 3.10, 3.11, 3.12, 3.13, or 3.14)
- **Git** (optional, if cloning via GitHub)
- **VS Code** (recommended editor)

---

### Step 2: Open the Project in Terminal
Open your terminal (PowerShell, Command Prompt, or Terminal on macOS/Linux) and navigate to the project directory:

```bash
cd clean-air-airbnb
```

---

### Step 3: (Recommended) Create & Activate Virtual Environment
Creating a virtual environment ensures dependencies don't conflict with other Python projects on your machine.

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 4: Install Dependencies
Install all required libraries using `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### Step 5: (Optional) Re-run Data Pipeline
The processed dataset (`data/processed/merged_listings.csv` with 16,050 listings across 45 cities) is already included. If you want to re-generate everything from scratch:

```bash
python scripts/generate_synthetic_data.py
python scripts/data_merger.py
```

---

### Step 6: Launch the Dashboard!
Run the Streamlit application:

```bash
streamlit run app/main.py
```
*(Alternative if `streamlit` is not directly on your PATH: `python -m streamlit run app/main.py`)*

Your browser will automatically open to:
👉 **`http://localhost:8501`**

---

## 📁 Project Structure

```
clean-air-airbnb/
├── app/
│   ├── main.py              # Streamlit dashboard (Inside Airbnb design)
│   ├── interactive_viz.py   # Interactive Plotly charts (zoom, pan, hover)
│   └── viz_modules.py       # Seaborn & Matplotlib figure generators
├── data/
│   ├── raw/                 # 45 individual city CSV files
│   └── processed/
│       └── merged_listings.csv  # 16,050 listings, INR-converted, imputed
├── notebooks/
│   ├── 01_cleaning_and_imputation.ipynb
│   └── 02_eda_and_stats.ipynb
├── scripts/
│   ├── currency_converter.py      # Multi-currency to INR conversion map
│   ├── data_merger.py             # Schema standardization & ETL merge
│   └── generate_synthetic_data.py # Synthetic raw dataset generator
├── requirements.txt         # Project Python dependencies
└── README.md                # Project documentation
```

---

## 🌟 Key Features of the Dashboard
1. **Interactive Geospatial Map**: Geo-referenced listing coordinates with AQI color tags.
2. **Clean Air Premium Analysis**: Interactive scatter plot with dynamic OLS regression fit testing $H_1$.
3. **Head-to-Head City Comparison**: Compare any 2 of the 45 cities and view the top-rated stays in clean-air zones.
4. **Manual Filters**: Precise numeric inputs for AQI and Price (INR) along with Room Type selectors.
5. **Theme-Aware Styling**: Seamless readability in both Light and Dark modes.
