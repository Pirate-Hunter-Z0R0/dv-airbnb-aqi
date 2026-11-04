import numpy as np
import pandas as pd
import random
import os
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = Path(r"e:\Project\dv-project\clean-air-airbnb\data\raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# City configurations
CITY_CONFIGS = [
    {"name": "Amsterdam",    "currency": "EUR", "price_range": (60, 280),       "aqi_mean": 35,  "aqi_std": 10, "n_listings": 350,
     "lat": 52.3676, "lon": 4.9041, "neighbourhoods": ["Centrum","Jordaan","De Pijp","Oud-West","Noord","Oost","Westerpark","Buitenveldert"]},
    {"name": "Bangkok",      "currency": "THB", "price_range": (800, 6000),     "aqi_mean": 105, "aqi_std": 30, "n_listings": 400,
     "lat": 13.7563, "lon": 100.5018, "neighbourhoods": ["Sukhumvit","Silom","Chatuchak","Bang Rak","Lat Phrao","Sathon","Khlong Toei","Wang Thonglang"]},
    {"name": "Barcelona",    "currency": "EUR", "price_range": (55, 320),       "aqi_mean": 42,  "aqi_std": 12, "n_listings": 420,
     "lat": 41.3851, "lon": 2.1734, "neighbourhoods": ["Eixample","Gracia","Born","Barceloneta","Sarrià","Poblenou","Horta","Sants"]},
    {"name": "Berlin",       "currency": "EUR", "price_range": (45, 250),       "aqi_mean": 38,  "aqi_std": 11, "n_listings": 380,
     "lat": 52.5200, "lon": 13.4050, "neighbourhoods": ["Mitte","Prenzlauer Berg","Kreuzberg","Neukölln","Friedrichshain","Charlottenburg","Schöneberg","Pankow"]},
    {"name": "Bogota",       "currency": "COP", "price_range": (80000, 350000), "aqi_mean": 55,  "aqi_std": 18, "n_listings": 280,
     "lat": 4.7110,  "lon": -74.0721, "neighbourhoods": ["Chapinero","Usaquén","Candelaria","Suba","Teusaquillo","Fontibón","Kennedy","Bosa"]},
    {"name": "Brisbane",     "currency": "AUD", "price_range": (70, 300),       "aqi_mean": 28,  "aqi_std": 8,  "n_listings": 250,
     "lat": -27.4698, "lon": 153.0251, "neighbourhoods": ["CBD","South Brisbane","New Farm","Fortitude Valley","West End","Paddington","Teneriffe","Newstead"]},
    {"name": "Brussels",     "currency": "EUR", "price_range": (55, 230),       "aqi_mean": 40,  "aqi_std": 12, "n_listings": 260,
     "lat": 50.8503, "lon": 4.3517, "neighbourhoods": ["Ixelles","Saint-Gilles","Laeken","Etterbeek","Schaerbeek","Molenbeek","Uccle","Auderghem"]},
    {"name": "Buenos Aires", "currency": "ARS", "price_range": (8000, 45000),   "aqi_mean": 65,  "aqi_std": 20, "n_listings": 320,
     "lat": -34.6037, "lon": -58.3816, "neighbourhoods": ["Palermo","Recoleta","San Telmo","Belgrano","Almagro","Villa Crespo","Caballito","Flores"]},
    {"name": "Cape Town",    "currency": "ZAR", "price_range": (700, 4500),     "aqi_mean": 32,  "aqi_std": 10, "n_listings": 300,
     "lat": -33.9249, "lon": 18.4241, "neighbourhoods": ["City Bowl","Sea Point","Green Point","Observatory","Woodstock","Gardens","De Waterkant","Camps Bay"]},
    {"name": "Dublin",       "currency": "EUR", "price_range": (70, 350),       "aqi_mean": 25,  "aqi_std": 8,  "n_listings": 290,
     "lat": 53.3498, "lon": -6.2603, "neighbourhoods": ["Temple Bar","Rathmines","Ranelagh","Ballsbridge","Portobello","Docklands","Phibsborough","Clontarf"]},
    {"name": "Goa",          "currency": "INR", "price_range": (1500, 12000),   "aqi_mean": 48,  "aqi_std": 15, "n_listings": 280,
     "lat": 15.2993, "lon": 74.1240, "neighbourhoods": ["Calangute","Baga","Anjuna","Panjim","Candolim","Vagator","Colva","Margao"]},
    {"name": "Hong Kong",    "currency": "HKD", "price_range": (400, 3500),     "aqi_mean": 82,  "aqi_std": 22, "n_listings": 310,
     "lat": 22.3193, "lon": 114.1694, "neighbourhoods": ["Central","Wan Chai","Mong Kok","Tsim Sha Tsui","Causeway Bay","Sham Shui Po","Kwun Tong","Yau Ma Tei"]},
    {"name": "Istanbul",     "currency": "TRY", "price_range": (800, 6000),     "aqi_mean": 75,  "aqi_std": 22, "n_listings": 370,
     "lat": 41.0082, "lon": 28.9784, "neighbourhoods": ["Beyoğlu","Kadıköy","Beşiktaş","Sultanahmet","Fatih","Üsküdar","Bakırköy","Şişli"]},
    {"name": "Lisbon",       "currency": "EUR", "price_range": (65, 310),       "aqi_mean": 38,  "aqi_std": 11, "n_listings": 340,
     "lat": 38.7169, "lon": -9.1399, "neighbourhoods": ["Alfama","Bairro Alto","Chiado","Príncipe Real","Mouraria","Intendente","Belém","Santos"]},
    {"name": "Madrid",       "currency": "EUR", "price_range": (55, 270),       "aqi_mean": 45,  "aqi_std": 14, "n_listings": 360,
     "lat": 40.4168, "lon": -3.7038, "neighbourhoods": ["Malasaña","Chueca","Lavapiés","Retiro","Salamanca","Chamberí","Moncloa","Carabanchel"]},
    {"name": "Milan",        "currency": "EUR", "price_range": (60, 290),       "aqi_mean": 58,  "aqi_std": 16, "n_listings": 330,
     "lat": 45.4654, "lon": 9.1859, "neighbourhoods": ["Duomo","Brera","Navigli","Isola","Porta Venezia","Ticinese","Nolo","Loreto"]},
    {"name": "New York",     "currency": "USD", "price_range": (80, 450),       "aqi_mean": 52,  "aqi_std": 16, "n_listings": 500,
     "lat": 40.7128, "lon": -74.0060, "neighbourhoods": ["Manhattan","Brooklyn","Queens","Harlem","Williamsburg","Astoria","Bushwick","Bronx"]},
    {"name": "Oslo",         "currency": "NOK", "price_range": (700, 3500),     "aqi_mean": 22,  "aqi_std": 7,  "n_listings": 240,
     "lat": 59.9139, "lon": 10.7522, "neighbourhoods": ["Grünerløkka","Frogner","Majorstuen","St. Hanshaugen","Sagene","Gamle Oslo","Nordstrand","Aker Brygge"]},
    {"name": "Paris",        "currency": "EUR", "price_range": (70, 380),       "aqi_mean": 48,  "aqi_std": 14, "n_listings": 450,
     "lat": 48.8566, "lon": 2.3522, "neighbourhoods": ["Marais","Montmartre","Saint-Germain","Bastille","Oberkampf","Belleville","République","Nation"]},
    {"name": "Sao Paulo",    "currency": "BRL", "price_range": (120, 800),      "aqi_mean": 88,  "aqi_std": 25, "n_listings": 390,
     "lat": -23.5505, "lon": -46.6333, "neighbourhoods": ["Vila Madalena","Pinheiros","Jardins","Liberdade","Consolação","Bela Vista","Moema","Itaim Bibi"]},
    {"name": "Santiago",     "currency": "CLP", "price_range": (25000, 180000), "aqi_mean": 72,  "aqi_std": 20, "n_listings": 290,
     "lat": -33.4489, "lon": -70.6693, "neighbourhoods": ["Providencia","Las Condes","Miraflores","Bellavista","Barrio Italia","Vitacura","Ñuñoa","Santiago Centro"]},
    {"name": "Singapore",    "currency": "SGD", "price_range": (90, 450),       "aqi_mean": 60,  "aqi_std": 18, "n_listings": 350,
     "lat": 1.3521,  "lon": 103.8198, "neighbourhoods": ["Orchard","Marina Bay","Chinatown","Little India","Bugis","Sentosa","Tanjong Pagar","Queenstown"]},
    {"name": "Stockholm",    "currency": "SEK", "price_range": (600, 3200),     "aqi_mean": 20,  "aqi_std": 6,  "n_listings": 270,
     "lat": 59.3293, "lon": 18.0686, "neighbourhoods": ["Södermalm","Östermalm","Vasastan","Kungsholmen","Gamla Stan","Norrmalm","Lidingö","Hammarby Sjöstad"]},
    {"name": "Sydney",       "currency": "AUD", "price_range": (75, 380),       "aqi_mean": 30,  "aqi_std": 9,  "n_listings": 400,
     "lat": -33.8688, "lon": 151.2093, "neighbourhoods": ["CBD","Newtown","Surry Hills","Glebe","Manly","Bondi","Pyrmont","Redfern"]},
    {"name": "Taipei",       "currency": "TWD", "price_range": (1200, 8000),    "aqi_mean": 78,  "aqi_std": 22, "n_listings": 310,
     "lat": 25.0330,  "lon": 121.5654, "neighbourhoods": ["Xinyi","Da'an","Zhongzheng","Wanhua","Zhongshan","Songshan","Shilin","Neihu"]},
    {"name": "Tokyo",        "currency": "JPY", "price_range": (5000, 35000),   "aqi_mean": 45,  "aqi_std": 13, "n_listings": 420,
     "lat": 35.6762, "lon": 139.6503, "neighbourhoods": ["Shinjuku","Shibuya","Asakusa","Roppongi","Akihabara","Harajuku","Ueno","Ginza"]},
    {"name": "Valencia",     "currency": "EUR", "price_range": (50, 240),       "aqi_mean": 40,  "aqi_std": 12, "n_listings": 280,
     "lat": 39.4699, "lon": -0.3763, "neighbourhoods": ["El Carmen","Ruzafa","Benimaclet","Cabanyal","Patraix","Extramurs","Campanar","Malilla"]},
    {"name": "Venice",       "currency": "EUR", "price_range": (80, 450),       "aqi_mean": 35,  "aqi_std": 10, "n_listings": 240,
     "lat": 45.4408, "lon": 12.3155, "neighbourhoods": ["San Marco","Dorsoduro","Cannaregio","Castello","Santa Croce","San Polo","Giudecca","Lido"]},
    {"name": "Zurich",       "currency": "CHF", "price_range": (100, 550),      "aqi_mean": 18,  "aqi_std": 6,  "n_listings": 220,
     "lat": 47.3769, "lon": 8.5417, "neighbourhoods": ["Altstadt","Zürich West","Seefeld","Wipkingen","Enge","Oerlikon","Albisrieden","Leimbach"]},
    # Extra Requested Cities:
    {"name": "Toronto",      "currency": "CAD", "price_range": (90, 420),       "aqi_mean": 34,  "aqi_std": 10, "n_listings": 420,
     "lat": 43.6532, "lon": -79.3832, "neighbourhoods": ["Downtown","Kensington Market","Yorkville","The Annex","Distillery District","Queen West","High Park","Leslieville"]},
    {"name": "Montreal",     "currency": "CAD", "price_range": (75, 340),       "aqi_mean": 28,  "aqi_std": 9,  "n_listings": 380,
     "lat": 45.5017, "lon": -73.5673, "neighbourhoods": ["Plateau-Mont-Royal","Old Montreal","Mile End","Downtown","Griffintown","Rosemont","Verdun","Villeray"]},
    {"name": "Ottawa",       "currency": "CAD", "price_range": (70, 300),       "aqi_mean": 26,  "aqi_std": 8,  "n_listings": 260,
     "lat": 45.4215, "lon": -75.6972, "neighbourhoods": ["ByWard Market","Centretown","The Glebe","Sandy Hill","Hintonburg","Westboro","Kanata","Orléans"]},
    {"name": "Chicago",      "currency": "USD", "price_range": (85, 450),       "aqi_mean": 46,  "aqi_std": 13, "n_listings": 450,
     "lat": 41.8781, "lon": -87.6298, "neighbourhoods": ["Loop","River North","Lincoln Park","Wicker Park","Logan Square","West Loop","Lakeview","Hyde Park"]},
    {"name": "Dallas",       "currency": "USD", "price_range": (80, 420),       "aqi_mean": 52,  "aqi_std": 14, "n_listings": 340,
     "lat": 32.7767, "lon": -96.7970, "neighbourhoods": ["Downtown","Uptown","Deep Ellum","Bishop Arts","Lower Greenville","Oak Lawn","Knox-Henderson","Preston Hollow"]},
    {"name": "Hawaii",       "currency": "USD", "price_range": (140, 680),      "aqi_mean": 16,  "aqi_std": 5,  "n_listings": 480,
     "lat": 21.3069, "lon": -157.8583, "neighbourhoods": ["Waikiki","Kailua","Lahaina","North Shore","Kihei","Princeville","Kona","Hilo"]},
    {"name": "Munich",       "currency": "EUR", "price_range": (65, 330),       "aqi_mean": 32,  "aqi_std": 10, "n_listings": 360,
     "lat": 48.1351, "lon": 11.5820, "neighbourhoods": ["Altstadt","Schwabing","Maxvorstadt","Glockenbachviertel","Haidhausen","Au","Neuhausen","Sendling"]},
    {"name": "Budapest",     "currency": "HUF", "price_range": (15000, 75000), "aqi_mean": 50,  "aqi_std": 15, "n_listings": 350,
     "lat": 47.4979, "lon": 19.0402, "neighbourhoods": ["District V (Belváros)","District VII (Jewish Quarter)","District VI (Terézváros)","District I (Castle District)","District VIII","District IX","District II","Óbuda"]},
    {"name": "Rome",         "currency": "EUR", "price_range": (70, 390),       "aqi_mean": 54,  "aqi_std": 15, "n_listings": 460,
     "lat": 41.9028, "lon": 12.4964, "neighbourhoods": ["Trastevere","Centro Storico","Monti","Testaccio","Prati","San Lorenzo","Campo de' Fiori","Aventino"]},
    {"name": "Beijing",      "currency": "CNY", "price_range": (280, 1800),     "aqi_mean": 115, "aqi_std": 35, "n_listings": 440,
     "lat": 39.9042, "lon": 116.4074, "neighbourhoods": ["Dongcheng","Chaoyang","Xicheng","Haidian","Sanlitun","Wangfujing","Gulou","Wudaokou"]},
    {"name": "Shanghai",     "currency": "CNY", "price_range": (300, 2000),     "aqi_mean": 108, "aqi_std": 32, "n_listings": 460,
     "lat": 31.2304, "lon": 121.4737, "neighbourhoods": ["Jing'an","French Concession","Huangpu","Pudong","Xuhui","Bund","Hongkou","Changning"]},
    {"name": "London",       "currency": "GBP", "price_range": (70, 420),       "aqi_mean": 42,  "aqi_std": 12, "n_listings": 500,
     "lat": 51.5074, "lon": -0.1278, "neighbourhoods": ["Westminster","Camden","Kensington","Shoreditch","Greenwich","Soho","Islington","Chelsea"]},
    {"name": "Edinburgh",    "currency": "GBP", "price_range": (65, 360),       "aqi_mean": 22,  "aqi_std": 7,  "n_listings": 320,
     "lat": 55.9533, "lon": -3.1883, "neighbourhoods": ["Old Town","New Town","Leith","Stockbridge","Morningside","Haymarket","Bruntsfield","Dean Village"]},
    {"name": "Copenhagen",   "currency": "DKK", "price_range": (500, 2800),     "aqi_mean": 24,  "aqi_std": 7,  "n_listings": 340,
     "lat": 55.6761, "lon": 12.5683, "neighbourhoods": ["Indre By","Vesterbro","Nørrebro","Østerbro","Christianshavn","Frederiksberg","Amagerbro","Valby"]},
    # Additional Indian Metros to complete 45 global cities:
    {"name": "Delhi",        "currency": "INR", "price_range": (1800, 14000),   "aqi_mean": 165, "aqi_std": 45, "n_listings": 450,
     "lat": 28.6139, "lon": 77.2090, "neighbourhoods": ["Connaught Place","Hauz Khas","South Extension","Vasant Kunj","Saket","Greater Kailash","Karol Bagh","Dwarka"]},
    {"name": "Mumbai",       "currency": "INR", "price_range": (2500, 18000),   "aqi_mean": 92,  "aqi_std": 26, "n_listings": 440,
     "lat": 19.0760, "lon": 72.8777, "neighbourhoods": ["Bandra West","Colaba","Juhu","Andheri West","Powai","Lower Parel","Dadar","Worli"]},
]


def aqi_category(aqi_val):
    if aqi_val <= 50:
        return "Good"
    elif aqi_val <= 100:
        return "Moderate"
    elif aqi_val <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi_val <= 200:
        return "Unhealthy"
    elif aqi_val <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def generate_city_data(cfg):
    n = cfg["n_listings"]
    p_min, p_max = cfg["price_range"]

    # --- listing_id ---
    listing_ids = np.random.choice(range(100000, 999999), size=n, replace=False)

    # --- neighbourhood ---
    neighbourhoods = np.random.choice(cfg["neighbourhoods"], size=n)

    # --- room_type ---
    room_types = np.random.choice(
        ["Entire home/apt", "Private room", "Shared room", "Hotel room"],
        size=n, p=[0.55, 0.30, 0.08, 0.07]
    )

    # --- price (lognormal, clipped) ---
    log_mean = np.log((p_min + p_max) / 2)
    log_sigma = 0.5
    prices = np.random.lognormal(mean=log_mean, sigma=log_sigma, size=n)
    prices = np.clip(prices, p_min, p_max).round(2)

    # --- minimum_nights ---
    nights_choices = list(range(1, 31))
    weights_raw = np.array([5, 4, 3] + [1] * 27, dtype=float)
    weights_raw /= weights_raw.sum()
    minimum_nights = np.random.choice(nights_choices, size=n, p=weights_raw)

    # --- availability_365 ---
    availability = np.random.randint(0, 366, size=n)

    # --- number_of_reviews (right-skewed via exponential) ---
    reviews_raw = np.random.exponential(scale=40, size=n)
    number_of_reviews = np.clip(reviews_raw, 0, 500).astype(int)

    # --- review_scores_rating ---
    ratings = np.random.normal(loc=4.3, scale=0.5, size=n)
    ratings = np.clip(ratings, 1.0, 5.0).round(2)

    # --- aqi ---
    aqi_vals = np.random.normal(loc=cfg["aqi_mean"], scale=cfg["aqi_std"], size=n)
    aqi_vals = np.clip(aqi_vals, 1, 500).astype(int)

    # --- aqi_category ---
    aqi_cats = [aqi_category(v) for v in aqi_vals]

    # --- lat/lon ---
    lat_noise = np.random.uniform(-0.07, 0.07, size=n)
    lon_noise = np.random.uniform(-0.07, 0.07, size=n)
    latitudes  = (cfg["lat"] + lat_noise).round(6)
    longitudes = (cfg["lon"] + lon_noise).round(6)

    df = pd.DataFrame({
        "city":                 cfg["name"],
        "listing_id":           listing_ids,
        "neighbourhood":        neighbourhoods,
        "room_type":            room_types,
        "price":                prices,
        "minimum_nights":       minimum_nights,
        "availability_365":     availability,
        "number_of_reviews":    number_of_reviews,
        "review_scores_rating": ratings,
        "aqi":                  aqi_vals,
        "aqi_category":         aqi_cats,
        "latitude":             latitudes,
        "longitude":            longitudes,
    })

    # --- Introduce ~5-8% NaN in price, review_scores_rating, aqi ---
    for col in ["price", "review_scores_rating", "aqi"]:
        frac = np.random.uniform(0.05, 0.08)
        nan_idx = np.random.choice(df.index, size=int(n * frac), replace=False)
        df.loc[nan_idx, col] = np.nan

    # Recompute aqi_category where aqi is NaN
    df["aqi_category"] = df["aqi"].apply(
        lambda v: aqi_category(int(v)) if pd.notna(v) else np.nan
    )

    return df


total_listings = 0

for cfg in CITY_CONFIGS:
    df = generate_city_data(cfg)
    city_slug = cfg["name"].lower().replace(" ", "_")
    out_path = OUTPUT_DIR / f"{city_slug}_listings.csv"
    df.to_csv(out_path, index=False)
    n = len(df)
    total_listings += n
    print(f"Generated {n} listings for {cfg['name']}")

print(f"\nTotal listings generated: {total_listings}")
