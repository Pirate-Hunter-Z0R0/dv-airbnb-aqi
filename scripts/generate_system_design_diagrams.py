"""
generate_system_design_diagrams.py
==================================
Generates high-resolution academic diagrams for Chapter 5 / Chapter 4: System Design:
1. Design Flowchart (design_flowchart.png)
2. Design Methodology Diagram (design_methodology.png)

Rendered with Matplotlib at 300 DPI for inclusion in the academic seminar report.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

OUT_DIR = Path(r"e:\Project\dv-project\clean-air-airbnb\data\images")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. DESIGN FLOWCHART
# -----------------------------------------------------------------------------
def generate_design_flowchart():
    fig, ax = plt.subplots(figsize=(11, 13), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(
        50, 97, "System Operational Design Flowchart",
        ha="center", va="center", fontsize=16, fontweight="bold",
        fontfamily="serif", color="#111827"
    )
    ax.text(
        50, 94.5, "End-to-End Analytical & Visual Pipeline for 'Paying for Clean Air?'",
        ha="center", va="center", fontsize=11, fontstyle="italic",
        fontfamily="serif", color="#4B5563"
    )

    def draw_box(x, y, w, h, title, lines, bg_color="#F3F4F6", border_color="#1F2937", rx=0.04):
        # Background box with rounded corners
        box = FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle=f"round,pad=0.5,rounding_size={rx}",
            ec=border_color, fc=bg_color, lw=1.5, zorder=2
        )
        ax.add_patch(box)
        # Header text
        ax.text(
            x, y + h * 0.26, title,
            ha="center", va="center", fontsize=11, fontweight="bold",
            fontfamily="sans-serif", color="#111827", zorder=3
        )
        # Body text
        body = "\n".join(lines)
        ax.text(
            x, y - h * 0.16, body,
            ha="center", va="center", fontsize=8.5,
            fontfamily="sans-serif", color="#374151", zorder=3, linespacing=1.35
        )

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>", color="#1F2937", lw=1.8,
                mutation_scale=14, shrinkA=3, shrinkB=3
            ),
            zorder=4
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(
                mx + 1.5, my, label,
                ha="left", va="center", fontsize=8, fontweight="bold",
                fontfamily="sans-serif", color="#1F2937", zorder=5
            )

    # Layer 1: Data Sources (Two parallel boxes)
    draw_box(
        28, 86, 38, 7.5,
        "Inside Airbnb Listing Feeds",
        ["• 16,050 listings across 45 global metropolises", "• Coordinates, nightly prices, room types, reviews"],
        bg_color="#EFF6FF", border_color="#2563EB"
    )
    draw_box(
        72, 86, 38, 7.5,
        "Open-Meteo Air Quality API",
        ["• Real-time satellite & sensor telemetry", "• PM2.5, PM10, and hourly AQI metrics"],
        bg_color="#ECFDF5", border_color="#059669"
    )

    # Layer 2: ETL & Data Normalization
    draw_box(
        50, 72, 60, 9,
        "Data Ingestion & Currency Normalization Pipeline",
        [
            "• Pegs 15 sovereign currencies to Indian Rupees (Base INR Jan 2024)",
            "• Interquartile Range (IQR) outlier truncation & null imputation",
            "• Spatial coordinate alignment and city metadata merging"
        ],
        bg_color="#FEF3C7", border_color="#D97706"
    )

    draw_arrow(28, 81.8, 42, 77, "Geocoded Raw Data")
    draw_arrow(72, 81.8, 58, 77, "Atmospheric Feeds")

    # Layer 3: Feature Engineering & Classification
    draw_box(
        50, 58, 60, 8.5,
        "Environmental Categorization & Transformation",
        [
            "• Maps AQI into EPA/WHO standard tiers (Good ≤50 to Very Unhealthy >200)",
            "• Computes logarithmic price transformations & elasticities",
            "• Structures in-memory cached DataFrames (@st.cache_data)"
        ],
        bg_color="#F3E8FF", border_color="#7C3AED"
    )
    draw_arrow(50, 67, 50, 62.8, "Clean Processed Dataset")

    # Layer 4: Analytics & Econometric Engine
    draw_box(
        50, 44, 60, 9,
        "Statistical & Econometric Analysis Engine",
        [
            "• Multivariate Ordinary Least Squares (OLS) regression modeling",
            "• Pearson correlation matrices (Price vs AQI: r = -0.275, p < 0.001)",
            "• Cross-city comparative aggregation and room-type tariff benchmarking"
        ],
        bg_color="#FCE7F3", border_color="#DB2777"
    )
    draw_arrow(50, 53.2, 50, 49, "Engineered Features")

    # Layer 5: User Interaction & Dynamic Filtering (Decision block / controller)
    draw_box(
        50, 30.5, 62, 8.5,
        "Dynamic UI Filtering & Theming Controller",
        [
            "• Multi-criteria sidebar filters: City, Room Type, Price & AQI thresholds",
            "• 1-Click adaptive theming: Pure White (Light Mode) & Sleek Dark (Dark Mode)",
            "• Reactive state dispatch with sub-second query latency"
        ],
        bg_color="#E0E7FF", border_color="#4F46E5"
    )
    draw_arrow(50, 39, 50, 35.3, "Model Parameters & Data Feeds")

    # Layer 6: Visual Presentation & Decision Support (3 branches)
    draw_box(
        22, 17, 30, 8.5,
        "Geospatial Visualization",
        ["• PyDeck 3D Carto Point Map", "• Color-coded AQI bubbles", "• Hover tooltips & coordinates"],
        bg_color="#F1F5F9", border_color="#475569"
    )
    draw_box(
        50, 17, 24, 8.5,
        "Econometric Charts",
        ["• Hedonic elasticity scatter", "• Marginal notched boxplots", "• Pearson correlation heatmap"],
        bg_color="#F1F5F9", border_color="#475569"
    )
    draw_box(
        78, 17, 30, 8.5,
        "Comparative Dashboards",
        ["• Head-to-Head City Compare", "• Real-time KPI summary cards", "• Room-type grouped tariffs"],
        bg_color="#F1F5F9", border_color="#475569"
    )

    draw_arrow(36, 25.8, 26, 21.8)
    draw_arrow(50, 25.8, 50, 21.8)
    draw_arrow(64, 25.8, 74, 21.8)

    # Layer 7: Final End User Decision Artifact
    draw_box(
        50, 5, 54, 5.5,
        "End User Decision-Support & Policy Insights",
        ["Informs urban environmental economists, travelers, hosts, and municipal planners"],
        bg_color="#ECFDF5", border_color="#059669"
    )
    draw_arrow(22, 12.2, 40, 8.2)
    draw_arrow(50, 12.2, 50, 8.2)
    draw_arrow(78, 12.2, 60, 8.2)

    plt.tight_layout()
    out_path = OUT_DIR / "design_flowchart.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Design Flowchart successfully generated at: {out_path}")


# -----------------------------------------------------------------------------
# 2. DESIGN METHODOLOGY DIAGRAM
# -----------------------------------------------------------------------------
def generate_design_methodology():
    fig, ax = plt.subplots(figsize=(11, 12), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(
        50, 96.5, "System Design Methodology Architecture",
        ha="center", va="center", fontsize=16, fontweight="bold",
        fontfamily="serif", color="#111827"
    )
    ax.text(
        50, 93.8, "Five-Phase Sequential Research & Visual Engineering Methodology",
        ha="center", va="center", fontsize=11, fontstyle="italic",
        fontfamily="serif", color="#4B5563"
    )

    phases = [
        {
            "phase": "PHASE 1",
            "title": "Problem Formulation & Theoretical Framework",
            "y": 82,
            "badge_color": "#1D4ED8",
            "bg_color": "#EFF6FF",
            "border_color": "#3B82F6",
            "items": [
                "• Conceptualize the 'Clean Air Premium' hypothesis grounded in Rosen's (1974) Hedonic Pricing Model.",
                "• Formulate empirical research questions: Does atmospheric quality dictate short-term lodging tariffs?",
                "• Establish cross-metropolitan study boundary across 45 diverse global cities spanning 5 continents."
            ]
        },
        {
            "phase": "PHASE 2",
            "title": "Data Acquisition, Ingestion & Currency Harmonization",
            "y": 66,
            "badge_color": "#047857",
            "bg_color": "#ECFDF5",
            "border_color": "#10B981",
            "items": [
                "• Ingest 16,050 listings from Inside Airbnb repositories (geolocations, tariffs, room types, reviews).",
                "• Establish fixed conversion baseline matrices pegging 15 currencies to Base Indian Rupees (INR).",
                "• Cleanse missing coordinates, eliminate null values, and apply IQR outlier bounds on nightly rates."
            ]
        },
        {
            "phase": "PHASE 3",
            "title": "Live Sensor Fusion & Environmental Telemetry",
            "y": 50,
            "badge_color": "#B45309",
            "bg_color": "#FEF3C7",
            "border_color": "#F59E0B",
            "items": [
                "• Integrate Open-Meteo Air Quality REST API with asynchronous querying and local TTL caching.",
                "• Query hourly atmospheric telemetry: PM2.5, PM10, European AQI, and US EPA Air Quality Index.",
                "• Classify listings into EPA tiers (Good ≤50, Moderate 51-100, Sensitive 101-150, Unhealthy >150)."
            ]
        },
        {
            "phase": "PHASE 4",
            "title": "Econometric Modeling & Statistical Verification",
            "y": 34,
            "badge_color": "#6D28D9",
            "bg_color": "#F5F3FF",
            "border_color": "#8B5CF6",
            "items": [
                "• Bivariate Linear Regression estimating air quality price elasticity (slope = -72.4 INR/AQI, r = -0.275).",
                "• Multivariate Ordinary Least Squares (OLS) model controlling for capacity, room type, and reviews (R² = 0.312).",
                "• Two-sample hypothesis testing and ANOVA assessing tariff differences across air quality categories."
            ]
        },
        {
            "phase": "PHASE 5",
            "title": "Interactive Visual Analytics & Dual-Theme UX Engineering",
            "y": 18,
            "badge_color": "#BE185D",
            "bg_color": "#FDF2F8",
            "border_color": "#EC4899",
            "items": [
                "• Apply Edward Tufte's data-ink principles and Shneiderman's mantra: Overview, Zoom/Filter, Details.",
                "• Engineer responsive dual-theming (Pure White Light Mode & Sleek Dark Mode) via explicit Plotly canvas CSS.",
                "• Deploy interactive PyDeck 3D maps, marginal notched boxplots, grouped room-type bars, and KPI cards."
            ]
        }
    ]

    for p in phases:
        y = p["y"]
        # Outer Card
        card = FancyBboxPatch(
            (6, y - 6), 88, 12,
            boxstyle="round,pad=0.5,rounding_size=0.03",
            ec=p["border_color"], fc=p["bg_color"], lw=1.6, zorder=2
        )
        ax.add_patch(card)

        # Phase Badge
        badge = FancyBboxPatch(
            (8, y + 2.5), 14, 2.7,
            boxstyle="round,pad=0.2,rounding_size=0.04",
            ec=p["badge_color"], fc=p["badge_color"], lw=1.0, zorder=3
        )
        ax.add_patch(badge)
        ax.text(
            15, y + 3.85, p["phase"],
            ha="center", va="center", fontsize=9, fontweight="bold",
            fontfamily="sans-serif", color="#FFFFFF", zorder=4
        )

        # Title
        ax.text(
            24, y + 3.85, p["title"],
            ha="left", va="center", fontsize=11, fontweight="bold",
            fontfamily="sans-serif", color="#111827", zorder=3
        )

        # Bullet Items
        text_y = y + 0.5
        for item in p["items"]:
            ax.text(
                10, text_y, item,
                ha="left", va="center", fontsize=8.6,
                fontfamily="sans-serif", color="#374151", zorder=3
            )
            text_y -= 2.1

    # Connect Phase Cards with Flow Arrows
    for i in range(len(phases) - 1):
        y_top = phases[i]["y"] - 6.5
        y_bot = phases[i + 1]["y"] + 6.5
        ax.annotate(
            "", xy=(50, y_bot), xytext=(50, y_top),
            arrowprops=dict(
                arrowstyle="-|>", color="#374151", lw=2.2,
                mutation_scale=16, shrinkA=2, shrinkB=2
            ),
            zorder=5
        )

    # Bottom summary tag
    ax.text(
        50, 4,
        "Iterative, Data-Driven Lifecycle: Continuous Feedback Loop from User Exploration to Econometric Validation",
        ha="center", va="center", fontsize=9.5, fontstyle="italic",
        fontfamily="serif", color="#4B5563"
    )

    plt.tight_layout()
    out_path = OUT_DIR / "design_methodology.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Design Methodology Diagram successfully generated at: {out_path}")


if __name__ == "__main__":
    generate_design_flowchart()
    generate_design_methodology()
