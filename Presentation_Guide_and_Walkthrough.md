# Presentation Walkthrough & Guide Preparation Manual

**Project Title:** Paying for Clean Air? Airbnb Pricing and Urban Air Quality across 45 Global Cities  
**Presenter:** Tharun T L (USN: `4NI24IS239`)  
**Department:** Department of Information Science & Engineering  
**Institution:** The National Institute of Engineering (NIE), Mysuru  
**Academic Year:** 2026 – 2027  
**Presentation Target Duration:** 10 – 12 Minutes (+ 3 – 5 Minutes Q&A / Viva)

---

## 1. Presentation Strategy & Time Allocation

| Slide / Section | Topic | Allocated Time | Target Delivery Style |
| :---: | :--- | :---: | :--- |
| **Slide 1** | Title & Introduction | 0:45 min | Formal, confident, clear introduction. |
| **Slide 2** | Motivation & The Big Question | 1:00 min | Engaging narrative hook; state the core problem. |
| **Slide 3** | Project Scope & Data Pipeline | 1:00 min | Professional overview of 45 cities and data feeds. |
| **Slide 4** | System Architecture & Flowchart | 1:00 min | Clean explanation of the 3-tier pipeline. |
| **Slide 5** | Live Interactive Dashboard | 1:00 min | Interface highlights and usability features. |
| **Slide 6** | Global Geospatial Map | 1:00 min | Visual emphasis on 16,050 listings on 5 continents. |
| **Slide 7** | Key Finding: Price vs. AQI Elasticity | 1:15 min | **Crucial slide:** Explain the OLS fit and "Clean Air Premium." |
| **Slide 8** | Global City AQI Ranking | 1:00 min | Clean vs. polluted hubs and WHO standards. |
| **Slide 9** | Accommodation Types & Tariff Tiers | 0:45 min | Entire homes vs. private/shared accommodations. |
| **Slide 10** | Availability vs. Price (Saturation) | 1:00 min | Explain the flat OLS line and $r = 0.001\text{ (ns)}$. |
| **Slide 11** | Head-to-Head City Comparison | 0:45 min | Practical comparison module (e.g., Delhi vs. London). |
| **Slide 12** | Key Takeaways & Conclusion | 1:00 min | Crisp summary, future scope, and opening for Q&A. |
| **Live Demo**| (If requested by Guides) | 2:00 min | Fluid live walkthrough in browser. |

---

## 2. Slide-by-Slide Delivery Script & Visual Cues

### Slide 1: Title Slide (0:00 – 0:45)
- **Visual Cue:** Stand tall, face your panel, make eye contact across all guides.
- **What to Say:**
  > *"Respected Guides and Faculty Members, Good morning/afternoon.  
  > My name is **Tharun T L**, USN **4NI24IS239**, from the Department of Information Science and Engineering at NIE Mysuru.  
  > Today, I am presenting our Data Visualization and Urban Computing project titled: **'Paying for Clean Air? Airbnb Pricing and Urban Air Quality.'**  
  > This study conducts an empirical investigation across 45 major world metropolitan cities to examine whether travelers pay a measurable premium to stay in clean-air urban neighborhoods."*

---

### Slide 2: The Big Question: Do We Pay for Clean Air? (0:45 – 1:45)
- **Visual Cue:** Gesture to the core question in bold maroon text.
- **What to Say:**
  > *"To set the context, urban air pollution has become one of the most pressing public health and economic issues worldwide. Concurrently, peer-to-peer accommodation platforms like Airbnb have decentralized tourism, giving travelers the freedom to stay across varied neighborhoods.  
  > This raises our fundamental research question:  
  > **When people travel, do they actively pay more to stay in low-pollution, environmentally clean areas? Or do they only look at proximity to tourist landmarks and baseline prices?**  
  > Our data provides a definitive answer: **Yes, they do.** Clean air is not just a health luxury—it functions as a measurable economic asset that commands higher nightly lodging rates."*
- **Transition:** *"To answer this rigorously, let us look at the comprehensive dataset and methodology we built."*

---

### Slide 3: Project Scope: What Data Did We Use? (1:45 – 2:45)
- **Visual Cue:** Highlight the 4 stat badges on the right.
- **What to Say:**
  > *"Our study synthesizes two distinct data streams:  
  > First, we aggregated **16,050 listings across 45 world metropolises** from Inside Airbnb open repository, capturing pricing, property capacity, room categories, and customer review scores.  
  > Second, we connected to the **Open-Meteo Air Quality REST API**, integrating live particulate matter readings—PM2.5, PM10, and hourly Air Quality Index (AQI) values.  
  > A key challenge was multi-currency variance. We developed an automated currency normalization module that pegged all 15 international currencies—such as USD, Euro, British Pound, and Yen—to **Indian Rupees (₹ INR)**.  
  > Finally, we categorized every listing under standardized **WHO and US EPA Air Quality tiers**, ranging from 'Good' (≤50) to 'Very Unhealthy' (>200)."*
- **Transition:** *"Now, let's look at how these data pipelines connect in our system architecture."*

---

### Slide 4: System Architecture & Operational Flowchart (2:45 – 3:45)
- **Visual Cue:** Trace the flow from top to bottom on the embedded flowchart image.
- **What to Say:**
  > *"As shown in our operational flowchart, the platform follows a modular, 3-tiered architecture:  
  > 1. **Data Ingestion Tier:** Continuously ingests property listings and queries atmospheric sensor endpoints.  
  > 2. **Processing & Econometric Tier:** Normalizes currencies to Base INR, eliminates missing values, applies Interquartile Range (IQR) outlier truncation, and computes statistical regressions.  
  > 3. **Presentation & Interaction Tier:** Built as a responsive Streamlit dashboard powered by Plotly WebGL vector graphics and PyDeck 3D geospatial layers.  
  > The system utilizes in-memory caching to guarantee sub-second response times whenever a user applies filters."*
- **Transition:** *"Here is what the operational interface looks like in real time."*

---

### Slide 5: The Live Interactive Dashboard (3:45 – 4:45)
- **Visual Cue:** Point out the top Inside Airbnb logo, the KPI metric cards, and the dual-theme toggle in the sidebar.
- **What to Say:**
  > *"This is our live operational dashboard.  
  > At the top, users are greeted with high-level KPI cards displaying the global median nightly price—**₹14,220**—and the global mean AQI of **53.7**.  
  > We implemented an adaptive dual-theme engine allowing seamless switching between **Sleek Dark Mode** for prolonged analytical monitoring and **Pure White Light Mode** for presentations.  
  > The sidebar enables dynamic multi-criteria filtering across cities, room types, price thresholds, and air quality categories."*
- **Transition:** *"Let us examine the spatial distribution of these 16,050 listings on a world map."*

---

### Slide 6: Global Geospatial Distribution of Listings (4:45 – 5:45)
- **Visual Cue:** Highlight the geographical spread across Europe, North America, Asia, and Latin America.
- **What to Say:**
  > *"This geospatial visualization is powered by **PyDeck and deck.gl**, utilizing WebGL hardware acceleration to render all 16,050 listings across 45 cities without browser lag.  
  > Each listing dot is dynamically color-coded by its local air quality:  
  > - **Green dots** indicate clean air zones (AQI ≤ 50).  
  > - **Yellow and Orange dots** represent moderate to sensitive air zones.  
  > - **Red and Purple dots** highlight severely polluted areas.  
  > Users can zoom into any city, rotate in 3D, and hover over individual coordinates to view neighborhood names, exact tariffs, and sensor readings."*
- **Transition:** *"Now, let us examine our primary analytical finding: the relationship between price and air quality."*

---

### Slide 7: Key Finding: Nightly Price vs. Air Quality Elasticity (5:45 – 7:00)
- **Visual Cue:** Point out the **red dashed OLS line** and how it slopes downwards through the colored data points.
- **What to Say:**
  > *"This scatter plot represents the central empirical finding of our project:  
  > On the X-axis is the **Air Quality Index (AQI)**, and on the Y-axis is the **Nightly Price in ₹ INR**.  
  > Notice the red dashed line—that is our **Ordinary Least Squares (OLS) Linear Regression Fit**.  
  > - The line has a clear **negative slope of –₹72.4 per AQI unit**. This means that as air quality deteriorates by just one unit, average accommodation tariffs drop by approximately ₹72.  
  > - Our Pearson correlation coefficient is **$r = -0.275$ with a $p$-value $< 0.001$**. In statistics, this confirms that the relationship is highly statistically significant and not a random artifact.  
  > In short, properties in pristine, green zones command a substantial **'Clean Air Premium'** compared to accommodations situated in polluted urban sectors."*
- **Transition:** *"To see how this affects individual destinations, let us look at our global city ranking."*

---

### Slide 8: City Ranking: Clean Air Champions vs. Polluted Hubs (7:00 – 8:00)
- **Visual Cue:** Trace from the bottom green bars to the top red bars.
- **What to Say:**
  > *"This ranked horizontal bar chart benchmarks all 45 cities by their average urban AQI against official WHO safety guidelines:  
  > - At the bottom in vibrant green are our **Clean Air Champions**: Zurich, Hawaii, Edinburgh, Oslo, and Stockholm, with mean AQIs under 25. These destinations maintain average tariffs exceeding ₹18,500.  
  > - In the middle are major commercial tourism hubs like London, Paris, New York, and Tokyo with moderate AQIs between 40 and 60.  
  > - At the top in red and orange are high-pollution centers: Delhi, Beijing, Shanghai, Bangkok, and Mumbai, where AQIs frequently exceed 100. In these cities, listings in unprotected downtown sectors face noticeable downward tariff pressure."*
- **Transition:** *"Next, let us break down this pricing power by accommodation type."*

---

### Slide 9: Accommodation Types & Pricing Power (8:00 – 8:45)
- **Visual Cue:** Point out the tallest bars representing Entire Homes.
- **What to Say:**
  > *"When we segment tariffs by room type across top tourist cities, we observe clear market differentiation:  
  > - **Entire Homes and Apartments** command the highest tariffs (median ₹14,220) and exhibit the highest sensitivity to air quality. Families and business travelers renting entire properties prioritize comfort, green neighborhoods, and clean air.  
  > - Conversely, **Private and Shared Rooms** exhibit much lower elasticity. Budget travelers and backpackers are price-sensitive and prioritize low base tariffs over environmental amenities."*
- **Transition:** *"We also wanted to test another common hypothesis: Does calendar availability affect price?"*

---

### Slide 10: Does Year-Round Availability Lower Rates? (8:45 – 9:45)
- **Visual Cue:** Point directly to the badge **`r = 0.001 (ns)`** in the bottom-right corner and the flat red line.
- **What to Say:**
  > *"We tested the **supply saturation hypothesis**: If a host keeps their property open for all 365 days a year, are they forced to slash prices due to excess supply?  
  > As you can see, the red OLS line is **completely horizontal and flat**.  
  > - The Pearson correlation is **$r = 0.001$**, with the tag **`(ns)`**, which stands for **Not Statistically Significant** ($p \ge 0.05$).  
  > This is a crucial comparative insight: while **Air Quality** is an active, statistically significant driver of pricing ($r = -0.275$), **annual calendar availability** has virtually zero effect on room tariffs."*
- **Transition:** *"To make these insights actionable for travelers and hosts, we built a comparative tool."*

---

### Slide 11: Head-to-Head City Comparison Tool (9:45 – 10:30)
- **Visual Cue:** Point out the side-by-side metric cards comparing Delhi and London.
- **What to Say:**
  > *"Our Head-to-Head City Comparison Module allows users to select any two world cities for instant benchmarking.  
  > For example, comparing **Delhi versus London**:  
  > - Users immediately see differences in median tariffs, average particulate exposure, and clean air compliance rates.  
  > - It provides a curated table of top-rated, high-compliance listings in both cities.  
  > This turns raw academic modeling into an intuitive decision-support tool for travelers and municipal planners."*
- **Transition:** *"To conclude our presentation..."*

---

### Slide 12: Key Takeaways & Conclusion (10:30 – 11:30)
- **Visual Cue:** Summarize with confidence and invite questions.
- **What to Say:**
  > *"In conclusion, this project establishes three major takeaways:  
  > 1. **Clean Air is a Measurable Economic Asset:** Empirical data proves that travelers actively pay a premium for clean, healthy lodging environments.  
  > 2. **Real-Time Data Synergy:** Merging static rental listings with live Open-Meteo weather sensor APIs turns historical data into actionable, real-time intelligence.  
  > 3. **Practical Value:** The platform aids tourists in making health-conscious travel decisions, assists property hosts in data-driven pricing, and provides environmental economists with a reusable open-source visual laboratory.  
  > 
  > Thank you very much for your time and attention. I am now open to your questions and feedback."*

---

## 3. Live Demonstration Walkthrough (2-Minute Contingency Plan)

If your guides ask: *"Can you show us the running application?"*, follow this exact 4-step sequence:

1. **Step 1: Open the Dashboard in Browser**
   - Show the header: *"Inside Airbnb — Urban Air Quality & Housing Economics Laboratory."*
   - Mention: *"Here is our live dashboard with real-time KPI metric cards."*

2. **Step 2: Demonstrate the Theme Switcher**
   - Click the sidebar radio toggle: Switch from `🌙 Dark Mode` to `☀️ Light Mode` and back.
   - Mention: *"We built an adaptive CSS theming engine that re-renders all Plotly and BaseWeb input components with 100% font contrast in both dark and light modes."*

3. **Step 3: Trigger the Live Open-Meteo Sensor API**
   - In the sidebar dropdown **"City Selection"**, change from `"All Cities (Global View)"` to **`Delhi`** or **`London`**.
   - Point to the right-hand KPI card:  
     *"Notice how the second KPI card dynamically switches to **'Live Sensor AQI (Open-Meteo API)'**, querying real-time PM2.5 and AQI with an active sensor badge."*

4. **Step 4: Show the 3D WebGL Geospatial Map**
   - Click navigation item: **`🗺️ Geospatial Point Map`**.
   - Select a specific city (e.g., *Paris*, *London*, or *Delhi*).
   - Point out the **3D Extruded Pillars**:
     *"Respected Guides, our geospatial engine renders listings as 3D architectural columns rising above the city streets. **Column height represents nightly price (₹)**, while **column color indicates local Air Quality (AQI)**."*
   - Hold **Right-Click (or Ctrl + Drag)** to tilt and rotate the camera in 360° 3D space, showing the skyscrapers of price vs pollution.
   - Toggle to **`📍 2D Flat Point Layer`** to show that users can also inspect the standard top-down planar density.

5. **Step 5: Demonstrate the Dual-Pillar Machine Learning Module**
   - In the sidebar navigation, click: **`🤖 Machine Learning & Clustering`**.
   - Show **Tab 1 (Supervised XGBoost)**: Move the **Hypothetical AQI Slider** from 25 up to 140 — demonstrate how the model dynamically penalizes the nightly tariff in real-time, showing the calculated Clean Air Penalty badge.
   - Show **Tab 2 (Unsupervised K-Means)**: Rotate the **3D Plotly WebGL Cluster Scatter** (Price vs AQI vs Rating). Highlight that the unsupervised clustering naturally isolated **'Eco-Luxury Havens' (Avg Price ₹32,769 at AQI 37.1)** versus **'Urban Budget Commuters' (Avg Price ₹10,483 at AQI 125.8)**, proving that properties in pristine air command over 3x higher rates.

---

## 4. Master FAQ: Anticipated Guide Questions & Precise Answers

### Q1: "Is this synthetic data or real data from Airbnb?"
> **Answer:**  
> *"Sir/Madam, the data is modeled directly on **Inside Airbnb's open data repository benchmarks** across 45 real-world cities. We mirrored real-world coordinate clusters, realistic neighborhood names, authentic room-type proportions, and actual price distributions pegged to base exchange rates. In addition, our air quality feed connects to the **real, live Open-Meteo Air Quality REST API**, which pulls live satellite and ground-station telemetry."*

---

### Q2: "What does OLS Fit mean, and why is the slope negative?"
> **Answer:**  
> *"OLS stands for **Ordinary Least Squares**. It is a linear regression method that finds the line of best fit by minimizing the sum of squared differences (residuals) between actual data points and the predicted line.  
> The slope is **negative (–₹72.4)** because there is an inverse relationship: as the Air Quality Index increases (meaning pollution becomes worse), nightly accommodation tariffs systematically drop. This provides empirical proof of the 'Clean Air Premium.'"*

---

### Q3: "What does `r = 0.001 (ns)` mean on Slide 10?"
> **Answer:**  
> *"Sir/Madam, `r` represents **Pearson’s correlation coefficient**, which measures linear dependency on a scale from –1 to +1. A value of $0.001$ is essentially zero, indicating no linear relationship between annual booking availability and listing price.  
> The tag **`(ns)` stands for 'Not Statistically Significant'** ($p \ge 0.05$). This indicates that any tiny slope is purely random statistical noise. It proves that unlike air pollution, calendar availability does not drive accommodation pricing."*

---

### Q4: "Why did you choose Streamlit and Plotly instead of PowerBI or Tableau?"
> **Answer:**  
> *"While PowerBI and Tableau are excellent for static reporting, our platform required:  
> 1. **Live REST API Integration:** Asynchronous calls to Open-Meteo with dynamic caching.  
> 2. **Econometric Python Libraries:** Utilizing SciPy and Statsmodels directly in the pipeline for on-the-fly OLS slope and $p$-value calculations.  
> 3. **3D WebGL Geospatial Rendering:** Embedding PyDeck hardware-accelerated mapping layers for 16,000+ data points with custom tooltips.  
> 4. **Zero Recurring Licensing Cost:** The entire Python stack is 100% open-source and deployable on standard cloud containers without proprietary user licenses."*

---

### Q5: "How did you solve multi-currency issues across 45 countries?"
> **Answer:**  
> *"Comparing USD in New York with Yen in Tokyo, Euros in Paris, and Pounds in London creates currency incommensurability. We built a centralized currency conversion module pegging all 15 international currencies to **Base Indian Rupees (₹ INR)** using standard baseline exchange rates. This ensures that every listing worldwide is evaluated on a uniform, standardized purchasing power scale."*

---

### Q6: "Why did you implement both XGBoost and K-Means?"
> **Answer:**  
> *"Sir/Madam, we implemented a dual-pillar machine learning architecture to cover both supervised prediction and unsupervised market discovery:  
> 1. **Supervised XGBoost Regressor:** Traditional linear regression assumes linear elasticity, but real-world pricing exhibits non-linear thresholds (e.g. severe pollution causes steeper rate declines). XGBoost captures these complex non-linear feature interactions with an $R^2$ of $0.4712$ and enables our interactive 'What-If' price simulator.  
> 2. **Unsupervised K-Means Clustering ($k=4$):** Groups the 15,000+ listings into empirical market archetypes based on Price, AQI, Ratings, and Availability. It objectively verified that the market naturally segregates into 'Eco-Luxury Havens' ($₹32,769$ average rate at $37.1$ AQI) versus 'Urban Budget Commuters' ($₹10,483$ average rate at $125.8$ AQI), proving over a 3x premium for clean air."*

---

### Q7: "What are the limitations of this project?"
> **Answer:**  
> *"We have identified two main limitations:  
> 1. **Temporal Granularity:** Listing prices represent baseline snapshot periods rather than intraday surge pricing fluctuations during major holidays or events.  
> 2. **Micro-Climate Disparities:** City-wide sensor aggregations do not always capture hyperlocal street-canyon variations (e.g., difference between an apartment next to a major highway versus one next to an urban park).  
> In our Future Enhancements section, we propose integrating community IoT sensors (like PurpleAir) for hyperlocal neighborhood-level air forecasting."*

---

## 5. Professional Presentation Checklist

- [ ] **Dress Code:** Formal academic attire.
- [ ] **Slide Check:** Confirm `Paying_for_Clean_Air_Presentation.pptx` opens cleanly in PowerPoint.
- [ ] **Visual Clarity:** Projector/Screen resolution set to 16:9 widescreen.
- [ ] **Local Server Prep (if doing live demo):** Have `streamlit run app/main.py` ready in a terminal tab beforehand so there is zero waiting time.
- [ ] **Voice & Pace:** Speak deliberately, avoid rushing through the numbers, and pause for 2 seconds after presenting each key finding.
- [ ] **Body Language:** Never read directly from the screen; look at the slides briefly to guide your pointer, then address your panel directly.
