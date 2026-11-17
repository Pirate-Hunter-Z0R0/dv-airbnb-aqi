"""
generate_project_presentation.py
================================
Generates a 12-slide executive/seminar PowerPoint presentation for:
'Paying for Clean Air? Airbnb Pricing and Urban Air Quality'

Styling based on reference presentation:
- Background: #FAF0DC (Warm Linen / Off-White)
- Font Color: #4A1515 (Deep Maroon / Burgundy)
- Title Font: Georgia (Bold, Serif)
- Body Font: Cambria (Serif, Clean)
- Tone: Simple, direct, free of complex technical jargon
- Images embedded from: clean-air-airbnb/data/images/
- Slide budget: Exactly 12 slides
"""

from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BG_COLOR = RGBColor(0xFA, 0xF0, 0xDC)    # #FAF0DC
TEXT_COLOR = RGBColor(0x4A, 0x15, 0x15)  # #4A1515
MUTED_TEXT = RGBColor(0x7A, 0x35, 0x35)  # Soft Burgundy Accent
CARD_BG = RGBColor(0xF5, 0xE5, 0xCB)     # Subtle card tint

FONT_TITLE = "Georgia"
FONT_BODY = "Cambria"

IMG_DIR = Path(r"e:\Project\dv-project\clean-air-airbnb\data\images")
P_FLOWCHART = IMG_DIR / "design_flowchart.png"
P_DASHBOARD = IMG_DIR / "Screenshot 2026-11-04 224302.png"
P_MAP = IMG_DIR / "Screenshot 2026-11-04 224325.png"
P_SCATTER = IMG_DIR / "plot-image-scatter.png"
P_RANKING = IMG_DIR / "plot-image (1).png"
P_ROOMTYPE = IMG_DIR / "plot-image.png"
P_AVAIL = IMG_DIR / "plot-image (6).png"
P_COMPARE = IMG_DIR / "Screenshot 2026-11-04 224521.png"


def add_run(p, text, font_name=FONT_BODY, font_size=16, color=TEXT_COLOR, bold=False, italic=False):
    r = p.add_run()
    r.text = text
    r.font.name = font_name
    r.font.size = Pt(font_size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic
    return r


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_styled_slide(title_text=""):
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

        if title_text:
            tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.733), Inches(0.85))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            add_run(p, title_text, font_name=FONT_TITLE, font_size=32, color=TEXT_COLOR, bold=True)

            # Accent underline
            line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.32), Inches(1.8), Inches(0.04)
            )
            line.fill.solid()
            line.fill.fore_color.rgb = TEXT_COLOR
            line.line.color.rgb = TEXT_COLOR

        return slide

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    s1.background.fill.solid()
    s1.background.fill.fore_color.rgb = BG_COLOR

    # Main Title Box
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.9), Inches(11.333), Inches(2.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.space_after = Pt(4)
    add_run(p1, "Paying for Clean Air?", font_name=FONT_TITLE, font_size=46, color=TEXT_COLOR, bold=True)

    p1_sub = tf1.add_paragraph()
    p1_sub.space_after = Pt(12)
    add_run(p1_sub, "Airbnb Pricing and Urban Air Quality in 45 World Cities", font_name=FONT_TITLE, font_size=24, color=TEXT_COLOR)

    p1_desc = tf1.add_paragraph()
    add_run(p1_desc, "A Visual Analytics & Environmental Economics Project", font_name=FONT_BODY, font_size=18, color=MUTED_TEXT, italic=True)

    # Metadata Card
    meta_card = s1.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.0), Inches(11.333), Inches(2.6)
    )
    meta_card.fill.solid()
    meta_card.fill.fore_color.rgb = CARD_BG
    meta_card.line.color.rgb = TEXT_COLOR
    meta_card.line.width = Pt(1.5)

    meta_tb = s1.shapes.add_textbox(Inches(1.4), Inches(4.2), Inches(10.5), Inches(2.2))
    mtf = meta_tb.text_frame
    mtf.word_wrap = True

    entries = [
        ("Presenter Name", "Tharun T L"),
        ("USN", "4NI24IS239"),
        ("Branch / Department", "Information Science & Engineering"),
        ("Institution", "The National Institute of Engineering, Mysuru"),
        ("Data Sources", "Inside Airbnb Open Data & Open-Meteo Air Quality API"),
    ]
    for i, (label, val) in enumerate(entries):
        p = mtf.paragraphs[0] if i == 0 else mtf.add_paragraph()
        p.space_after = Pt(4)
        add_run(p, f"{label} : ", font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        add_run(p, val, font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 2: THE CORE QUESTION & MOTIVATION
    # =========================================================================
    s2 = add_styled_slide("The Big Question: Do We Pay for Clean Air?")

    # Left Narrative Box
    tb2_left = s2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.5), Inches(5.2))
    tf2_l = tb2_left.text_frame
    tf2_l.word_wrap = True

    points2 = [
        ("Urban Air Pollution: ", "Air quality is now a foremost health concern in major world metropolises, influencing where people live, work, and travel."),
        ("Booming Short-Term Rentals: ", "Airbnb listings have transformed how travelers book accommodations, offering flexible choices across diverse neighborhoods."),
        ("The Core Question: ", "Do tourists and travelers pay more to stay in areas with clean, unpolluted air? Or do they only care about price and proximity to city centers?"),
        ("Our Core Finding: ", "YES! Clean air commands a clear, measurable price premium. Listings in cleaner cities and greener zones consistently charge significantly higher nightly rates."),
    ]
    for i, (prefix, text) in enumerate(points2):
        p = tf2_l.paragraphs[0] if i == 0 else tf2_l.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, prefix, font_name=FONT_TITLE, font_size=17, color=TEXT_COLOR, bold=True)
        add_run(p, text, font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    # Right Stat Cards
    stat_boxes = [
        ("45 Global Cities", "Encompassing North America, Europe, Asia-Pacific, Latin America, and India"),
        ("16,050 Listings", "Representative sample with verified rates, room types, and coordinates"),
        ("Live Air Sensors", "Hourly PM2.5, PM10, and AQI feeds via Open-Meteo satellite & ground stations"),
        ("Pegged to ₹ INR", "All 15 international currencies normalized to Indian Rupees for fair benchmarking"),
    ]
    for idx, (title, desc) in enumerate(stat_boxes):
        y_pos = 1.6 + idx * 1.3
        card = s2.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.7), Inches(y_pos), Inches(4.8), Inches(1.15)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = TEXT_COLOR
        card.line.width = Pt(1.2)

        ctb = s2.shapes.add_textbox(Inches(7.9), Inches(y_pos + 0.1), Inches(4.4), Inches(0.95))
        ctf = ctb.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        add_run(cp1, title, font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        cp2 = ctf.add_paragraph()
        add_run(cp2, desc, font_name=FONT_BODY, font_size=13, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 3: DATASET & METHODOLOGY (SIMPLE)
    # =========================================================================
    s3 = add_styled_slide("Project Scope: What Data Did We Use?")

    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    steps = [
        ("1. Airbnb Listings Data", "Inside Airbnb Open Data repository covering 16,050 listings across 45 world metropolises. Includes property location, room category, nightly prices, availability, and guest reviews."),
        ("2. Real-Time Air Quality API", "Integrated Open-Meteo Air Quality REST API to query live hourly PM2.5, PM10, and Air Quality Index (AQI) values for every city based on GPS coordinates."),
        ("3. Currency Normalization", "Converted 15 sovereign currencies (USD, EUR, GBP, JPY, CAD, AUD, etc.) into Indian Rupees (₹ INR) using standard baseline exchange rates to allow fair cross-city comparisons."),
        ("4. WHO / EPA Clean Air Standards", "Classified properties into 5 clear environmental quality tiers: Good (≤50), Moderate (51–100), Sensitive (101–150), Unhealthy (151–200), and Very Unhealthy (>200)."),
    ]
    for i, (title, desc) in enumerate(steps):
        p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
        p.space_after = Pt(16)
        add_run(p, f"•  {title}: ", font_name=FONT_TITLE, font_size=18, color=TEXT_COLOR, bold=True)
        add_run(p, desc, font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE & FLOWCHART
    # =========================================================================
    s4 = add_styled_slide("System Architecture & Operational Flowchart")

    # Left narrative
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    flow_pts = [
        ("Layered Architecture: ", "The platform is built in three clear, modular tiers: Data Ingestion, Statistical Engine, and Interactive Web Dashboard."),
        ("Automated Processing: ", "Raw listing files and live weather APIs are cleaned, harmonized to Base INR, and cached in memory for instant interaction."),
        ("User Interaction: ", "Users filter listings by city, room type, price bounds, and air quality tiers with immediate visual recalculation."),
        ("Accessible Theming: ", "Built-in support for both Pure White Light Mode and Sleek Dark Mode for easy presentation."),
    ]
    for i, (pfx, txt) in enumerate(flow_pts):
        p = tf4.paragraphs[0] if i == 0 else tf4.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, pfx, font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        add_run(p, txt, font_name=FONT_BODY, font_size=15, color=TEXT_COLOR)

    # Right: Embedded Flowchart Image
    if P_FLOWCHART.exists():
        s4.shapes.add_picture(str(P_FLOWCHART), Inches(7.0), Inches(1.5), width=Inches(5.5))

    # =========================================================================
    # SLIDE 5: LIVE DASHBOARD OVERVIEW
    # =========================================================================
    s5 = add_styled_slide("The Live Interactive Dashboard")

    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.7))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    p5 = tf5.paragraphs[0]
    add_run(p5, "A modern web dashboard built with Streamlit & Plotly featuring live KPI cards, interactive filters, and real-time sensor updates.", font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    if P_DASHBOARD.exists():
        s5.shapes.add_picture(str(P_DASHBOARD), Inches(1.2), Inches(2.1), width=Inches(10.933))

    # =========================================================================
    # SLIDE 6: GEOSPATIAL MAP OF 16,050 LISTINGS
    # =========================================================================
    s6 = add_styled_slide("Global Geospatial Distribution of Listings")

    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.7))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    p6 = tf6.paragraphs[0]
    add_run(p6, "High-performance PyDeck 3D map plotting 16,050 listings across 45 world metropolises, color-coded by local air quality safety tiers.", font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    if P_MAP.exists():
        s6.shapes.add_picture(str(P_MAP), Inches(1.2), Inches(2.1), width=Inches(10.933))

    # =========================================================================
    # SLIDE 7: KEY FINDING - PRICE VS AQI ELASTICITY
    # =========================================================================
    s7 = add_styled_slide("Key Finding: Nightly Price vs. Air Quality")

    # Left: Scatter image
    if P_SCATTER.exists():
        s7.shapes.add_picture(str(P_SCATTER), Inches(0.8), Inches(1.6), width=Inches(5.8))

    # Right: Narrative
    tb7 = s7.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.5), Inches(5.2))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    pts7 = [
        ("The Downward Sloping Line: ", "As Air Quality Index (AQI) increases (meaning air becomes dirtier and more polluted), nightly accommodation tariffs steadily drop."),
        ("Quantifying the Clean Air Premium: ", "The regression slope indicates an average drop of ~₹72.4 per AQI unit increase. Guests pay substantially more to stay in clean, green environments."),
        ("Statistical Significance: ", "A Pearson correlation of r = -0.275 (p < 0.001) confirms this is not random chance—clean air is a genuine economic amenity."),
        ("High-End Resilience: ", "Luxury entire homes command high rates even in moderate air, but discount heavily in severe pollution zones."),
    ]
    for i, (pfx, txt) in enumerate(pts7):
        p = tf7.paragraphs[0] if i == 0 else tf7.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, pfx, font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        add_run(p, txt, font_name=FONT_BODY, font_size=15, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 8: CITY RANKING - CLEANEST VS POLLUTED
    # =========================================================================
    s8 = add_styled_slide("City Ranking: Clean Air Champions vs. Polluted Hubs")

    if P_RANKING.exists():
        s8.shapes.add_picture(str(P_RANKING), Inches(0.8), Inches(1.5), width=Inches(3.3))

    tb8 = s8.shapes.add_textbox(Inches(4.5), Inches(1.6), Inches(8.0), Inches(5.2))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    pts8 = [
        ("Clean Air Champions (Mean AQI < 25): ", "Zurich, Hawaii, Edinburgh, Oslo, Stockholm, Copenhagen, Dublin, and Munich. These destinations feature pristine air and average nightly rates exceeding ₹18,500."),
        ("Moderate Air Metropolises (AQI 40 – 60): ", "London, Paris, New York, Tokyo, Madrid, and Chicago. Moderate air quality, with high pricing power driven by heavy tourism and business demand."),
        ("Severely Polluted Hubs (AQI > 100): ", "Delhi, Beijing, Shanghai, Bangkok, and Mumbai. Experience seasonal and chronic smog, leading to significant accommodation discounting in unprotected city centers."),
        ("WHO Guidelines Marked: ", "Dashed benchmark lines show compliance with WHO Clean Air (≤50) and Moderate (≤100) thresholds."),
    ]
    for i, (pfx, txt) in enumerate(pts8):
        p = tf8.paragraphs[0] if i == 0 else tf8.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, pfx, font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        add_run(p, txt, font_name=FONT_BODY, font_size=15, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 9: ROOM TYPE BREAKDOWN
    # =========================================================================
    s9 = add_styled_slide("Accommodation Types & Pricing Power")

    if P_ROOMTYPE.exists():
        s9.shapes.add_picture(str(P_ROOMTYPE), Inches(0.8), Inches(1.6), width=Inches(6.2))

    tb9 = s9.shapes.add_textbox(Inches(7.4), Inches(1.6), Inches(5.1), Inches(5.2))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    pts9 = [
        ("Entire Homes Lead the Market: ", "Entire homes/apartments command the highest rates (median: ₹14,220) across all 45 global destinations."),
        ("Highest Sensitivity to Air Quality: ", "Families and luxury travelers renting entire apartments demonstrate the highest willingness to pay for cleaner air and green neighborhoods."),
        ("Private & Shared Rooms: ", "Exhibit much lower price elasticity. Budget-conscious backpackers and solo travelers prioritize price over environmental factors."),
        ("Hotel Rooms on Airbnb: ", "Maintain steady commercial pricing with professional hospitality standards."),
    ]
    for i, (pfx, txt) in enumerate(pts9):
        p = tf9.paragraphs[0] if i == 0 else tf9.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, pfx, font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        add_run(p, txt, font_name=FONT_BODY, font_size=15, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 10: AVAILABILITY VS PRICING (SUPPLY SATURATION)
    # =========================================================================
    s10 = add_styled_slide("Does Year-Round Availability Lower Rates?")

    if P_AVAIL.exists():
        s10.shapes.add_picture(str(P_AVAIL), Inches(0.8), Inches(1.6), width=Inches(5.8))

    tb10 = s10.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.5), Inches(5.2))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    pts10 = [
        ("Testing Supply Saturation: ", "We tested whether properties that remain open 365 days a year are forced to discount their nightly rates to attract guests."),
        ("Flat Trendline (r = 0.001): ", "The red OLS regression line is completely flat across 0 to 365 days of annual availability."),
        ("Not Statistically Significant (ns): ", "Pearson r = 0.001 (ns) proves that annual calendar availability has zero measurable effect on listing prices."),
        ("Key Conclusion: ", "Unlike Air Quality (which is a strong active driver of price), calendar availability is completely neutral in dictating accommodation value."),
    ]
    for i, (pfx, txt) in enumerate(pts10):
        p = tf10.paragraphs[0] if i == 0 else tf10.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, pfx, font_name=FONT_TITLE, font_size=16, color=TEXT_COLOR, bold=True)
        add_run(p, txt, font_name=FONT_BODY, font_size=15, color=TEXT_COLOR)

    # =========================================================================
    # SLIDE 11: HEAD-TO-HEAD CITY COMPARISON
    # =========================================================================
    s11 = add_styled_slide("Head-to-Head City Comparison Module")

    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.7))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    p11 = tf11.paragraphs[0]
    add_run(p11, "Direct side-by-side benchmarking of any two cities (e.g., Delhi vs. London) evaluating mean AQI, median prices, and clean air compliance.", font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    if P_COMPARE.exists():
        s11.shapes.add_picture(str(P_COMPARE), Inches(1.2), Inches(2.1), width=Inches(10.933))

    # =========================================================================
    # SLIDE 12: CONCLUSION & KEY TAKEAWAYS
    # =========================================================================
    s12 = add_styled_slide("Key Takeaways & Conclusion")

    tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(3.6))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    concl_pts = [
        ("1. Clean Air is a Measurable Economic Asset: ", "Empirical evidence across 16,050 listings confirms that travelers actively pay a premium to avoid urban air pollution."),
        ("2. Real-Time Data Synergy: ", "Merging static platform datasets with live atmospheric APIs (Open-Meteo) turns ordinary listings data into actionable intelligence."),
        ("3. Actionable Insights: ", "Helps travelers make health-conscious booking choices, assists hosts in setting data-backed seasonal rates, and guides municipal tourism planners."),
    ]
    for i, (pfx, txt) in enumerate(concl_pts):
        p = tf12.paragraphs[0] if i == 0 else tf12.add_paragraph()
        p.space_after = Pt(14)
        add_run(p, pfx, font_name=FONT_TITLE, font_size=17, color=TEXT_COLOR, bold=True)
        add_run(p, txt, font_name=FONT_BODY, font_size=16, color=TEXT_COLOR)

    # Thank you box at the bottom
    ty_card = s12.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.5), Inches(5.4), Inches(8.333), Inches(1.4)
    )
    ty_card.fill.solid()
    ty_card.fill.fore_color.rgb = CARD_BG
    ty_card.line.color.rgb = TEXT_COLOR
    ty_card.line.width = Pt(1.5)

    ty_tb = s12.shapes.add_textbox(Inches(2.7), Inches(5.5), Inches(7.933), Inches(1.2))
    ty_tf = ty_tb.text_frame
    ty_tf.word_wrap = True
    tp1 = ty_tf.paragraphs[0]
    tp1.alignment = PP_ALIGN.CENTER
    add_run(tp1, "Thank You!", font_name=FONT_TITLE, font_size=28, color=TEXT_COLOR, bold=True)

    tp2 = ty_tf.add_paragraph()
    tp2.alignment = PP_ALIGN.CENTER
    add_run(tp2, "Questions & Discussion Welcome", font_name=FONT_BODY, font_size=16, color=MUTED_TEXT)

    # Save to disk
    out_dir = Path(r"e:\Project\dv-project\clean-air-airbnb")
    out_path = out_dir / "Paying_for_Clean_Air_Presentation.pptx"
    prs.save(str(out_path))
    print(f"Presentation successfully generated at: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    create_presentation()
