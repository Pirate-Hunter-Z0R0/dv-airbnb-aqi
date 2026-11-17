"""
Machine Learning Pipeline for Paying for Clean Air Project
Implements:
1. Supervised Learning: XGBoost Regressor for Listing Nightly Price Prediction & AQI Elasticity
2. Unsupervised Learning: K-Means Clustering for Market Segmentation & Listing Archetypes
"""

import os
import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.cluster import KMeans
import xgboost as xgb
import joblib

# Paths setup
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "merged_listings.csv"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

CATEGORICAL_FEATURES = ["city", "room_type"]
NUMERICAL_FEATURES = [
    "aqi",
    "minimum_nights",
    "availability_365",
    "number_of_reviews",
    "review_scores_rating",
]
TARGET = "price_inr"

CLUSTER_FEATURES = ["price_inr", "aqi", "availability_365", "review_scores_rating"]


def load_and_preprocess_data():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Ensure numeric columns
    for col in NUMERICAL_FEATURES + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Drop rows missing crucial target or features
    df_clean = df.dropna(subset=CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET]).copy()
    print(f"Dataset clean record count: {len(df_clean):,} rows (from {len(df):,})")
    return df_clean


def train_xgboost_regressor(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("TRAINING SUPERVISED MODEL: XGBoost Regressor")
    print("=" * 60)
    
    X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = df[TARGET]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Train size: {len(X_train):,}, Test size: {len(X_test):,}")
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("num", StandardScaler(), NUMERICAL_FEATURES),
        ]
    )
    
    xgb_reg = xgb.XGBRegressor(
        n_estimators=250,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1,
    )
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", xgb_reg)
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mae_test = mean_absolute_error(y_test, y_pred_test)
    
    print(f"Train R²: {r2_train:.4f}")
    print(f"Test R²:  {r2_test:.4f}")
    print(f"Test RMSE: ₹{rmse_test:,.2f}")
    print(f"Test MAE:  ₹{mae_test:,.2f}")
    
    # Feature Importances Extraction
    cat_feature_names = (
        pipeline.named_steps["preprocessor"]
        .named_transformers_["cat"]
        .get_feature_names_out(CATEGORICAL_FEATURES)
        .tolist()
    )
    all_feature_names = cat_feature_names + NUMERICAL_FEATURES
    raw_importances = pipeline.named_steps["regressor"].feature_importances_
    
    # Aggregate importance by source feature
    importance_summary = {}
    for name, imp in zip(all_feature_names, raw_importances):
        for orig_col in CATEGORICAL_FEATURES + NUMERICAL_FEATURES:
            if name == orig_col or name.startswith(orig_col + "_"):
                importance_summary[orig_col] = importance_summary.get(orig_col, 0.0) + float(imp)
                break
                
    # Normalize to 100%
    tot = sum(importance_summary.values()) or 1.0
    importance_pct = {k: round((v / tot) * 100, 2) for k, v in sorted(importance_summary.items(), key=lambda x: x[1], reverse=True)}
    
    print("\nFeature Importance Breakdown (%):")
    for feat, pct in importance_pct.items():
        print(f"  - {feat:22s}: {pct:5.2f}%")
        
    # Save Model Pipeline and Metadata
    model_path = MODELS_DIR / "xgboost_price_pipeline.joblib"
    joblib.dump(pipeline, model_path)
    print(f"\nSaved XGBoost pipeline to: {model_path}")
    
    metrics = {
        "r2_test": round(r2_test, 4),
        "r2_train": round(r2_train, 4),
        "rmse_test": round(rmse_test, 2),
        "mae_test": round(mae_test, 2),
        "feature_importances": importance_pct,
    }
    with open(MODELS_DIR / "xgboost_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    return pipeline, metrics


def train_kmeans_clustering(df: pd.DataFrame, n_clusters: int = 4):
    print("\n" + "=" * 60)
    print(f"TRAINING UNSUPERVISED MODEL: K-Means Clustering (k={n_clusters})")
    print("=" * 60)
    
    X_clust = df[CLUSTER_FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clust)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=15)
    clusters = kmeans.fit_predict(X_scaled)
    df["cluster"] = clusters
    
    # Characterize and Name Archetypes based on Centroids
    profile = df.groupby("cluster")[CLUSTER_FEATURES].mean().reset_index()
    counts = df["cluster"].value_counts().to_dict()
    profile["count"] = profile["cluster"].map(counts)
    
    # Heuristic archetype labeler based on relative Price and AQI
    archetype_names = {}
    for idx, row in profile.iterrows():
        c_id = int(row["cluster"])
        p = row["price_inr"]
        a = row["aqi"]
        r = row["review_scores_rating"]
        
        # Relative scoring against dataset averages
        mean_p = df["price_inr"].mean()
        mean_a = df["aqi"].mean()
        
        if p >= mean_p and a <= mean_a:
            archetype_names[c_id] = "Eco-Luxury Havens (Clean Air & High Rate)"
        elif p < mean_p and a > mean_a:
            archetype_names[c_id] = "Urban Budget Commuters (High AQI / Budget)"
        elif r >= 4.4 and a <= mean_a + 10:
            archetype_names[c_id] = "Prime Tourist Stays (Top Rated & Moderate AQI)"
        else:
            archetype_names[c_id] = "Standard High-Availability Rentals"
            
    # Ensure distinct labels if any collisions
    used = set()
    for c_id in sorted(archetype_names.keys()):
        label = archetype_names[c_id]
        if label in used:
            archetype_names[c_id] = f"Cluster {c_id} (Balanced Urban Segment)"
        used.add(archetype_names[c_id])
        
    profile["archetype"] = profile["cluster"].map(archetype_names)
    df["archetype"] = df["cluster"].map(archetype_names)
    
    print("\nCluster Profiles:")
    for _, r in profile.iterrows():
        print(f"  Cluster {int(r['cluster'])}: {r['archetype']}")
        print(f"    - Avg Price: ₹{r['price_inr']:,.0f} | Avg AQI: {r['aqi']:.1f} | Avg Rating: {r['review_scores_rating']:.2f} | Count: {int(r['count']):,}")
        
    # Save clustering pipeline and profiled dataframe with cluster labels
    kmeans_pack = {
        "scaler": scaler,
        "kmeans": kmeans,
        "cluster_features": CLUSTER_FEATURES,
        "archetype_names": archetype_names,
        "profile": profile.to_dict(orient="records"),
    }
    joblib.dump(kmeans_pack, MODELS_DIR / "kmeans_pipeline.joblib")
    
    # Save labeled dataset with cluster column so Streamlit displays instantly
    labeled_csv_path = ROOT / "data" / "processed" / "clustered_listings.csv"
    df.to_csv(labeled_csv_path, index=False)
    print(f"\nSaved clustered dataset to: {labeled_csv_path}")
    print(f"Saved KMeans bundle to: {MODELS_DIR / 'kmeans_pipeline.joblib'}")
    
    return kmeans_pack, df


def main():
    df_clean = load_and_preprocess_data()
    train_xgboost_regressor(df_clean)
    train_kmeans_clustering(df_clean, n_clusters=4)
    print("\nMachine Learning Pipeline Execution Complete Successfully.")


if __name__ == "__main__":
    main()
