import { useEffect, useState } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import { Moon, Sun } from "lucide-react";

interface Listing {
  listing_id: number;
  city: string;
  neighbourhood: string;
  room_type: string;
  price_inr: number;
  aqi: number;
  aqi_category: string;
  latitude: number;
  longitude: number;
  review_scores_rating: number;
  number_of_reviews: number;
}

interface Stats {
  total_listings: number;
  entire_home_pct: number;
  median_price: number;
  mean_aqi: number;
  clean_air_pct: number;
}

interface ComparisonData {
  city_a: { name: string; summary: Stats; top_stays: Listing[] };
  city_b: { name: string; summary: Stats; top_stays: Listing[] };
}

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<"map" | "premium" | "compare" | "data">("map");

  // Filter options
  const [cities, setCities] = useState<string[]>([]);
  const [roomTypes, setRoomTypes] = useState<string[]>([]);
  const [selectedCity, setSelectedCity] = useState("All Cities (Global View)");
  const [selectedRooms, setSelectedRooms] = useState<string[]>([]);
  const [minAqi, setMinAqi] = useState<number>(0);
  const [maxAqi, setMaxAqi] = useState<number>(250);
  const [minPrice, setMinPrice] = useState<number>(0);
  const [maxPrice, setMaxPrice] = useState<number>(55000);

  // Data states
  const [stats, setStats] = useState<Stats | null>(null);
  const [listings, setListings] = useState<Listing[]>([]);
  const [aqiRanking, setAqiRanking] = useState<any[]>([]);
  const [scatterData, setScatterData] = useState<{ points: any[]; regression: any } | null>(null);

  // Comparison State
  const [compCityA, setCompCityA] = useState("Amsterdam");
  const [compCityB, setCompCityB] = useState("Zurich");
  const [compData, setCompData] = useState<ComparisonData | null>(null);

  // Load initial metadata
  useEffect(() => {
    fetch(`${API_BASE}/meta`)
      .then((res) => res.json())
      .then((data) => {
        setCities(data.cities || []);
        setRoomTypes(data.room_types || []);
        setSelectedRooms(data.room_types || []);
        if (data.price_range?.max) setMaxPrice(data.price_range.max);
      })
      .catch((err) => console.error("Error loading meta:", err));
  }, []);

  // Fetch KPI Stats & Listings whenever filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (selectedCity && selectedCity !== "All Cities (Global View)") params.append("city", selectedCity);
    selectedRooms.forEach((r) => params.append("room_type", r));
    params.append("min_aqi", minAqi.toString());
    params.append("max_aqi", maxAqi.toString());
    params.append("min_price", minPrice.toString());
    params.append("max_price", maxPrice.toString());

    fetch(`${API_BASE}/stats?${params.toString()}`)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Error fetching stats:", err));

    fetch(`${API_BASE}/listings?${params.toString()}&limit=600`)
      .then((res) => res.json())
      .then((data) => setListings(data))
      .catch((err) => console.error("Error fetching listings:", err));
  }, [selectedCity, selectedRooms, minAqi, maxAqi, minPrice, maxPrice]);

  // Fetch Charts Data
  useEffect(() => {
    fetch(`${API_BASE}/charts/aqi-ranking`)
      .then((res) => res.json())
      .then((data) => setAqiRanking(data))
      .catch((err) => console.error("Error fetching ranking:", err));

    const cityParam = selectedCity !== "All Cities (Global View)" ? `?city=${encodeURIComponent(selectedCity)}` : "";
    fetch(`${API_BASE}/charts/scatter${cityParam}`)
      .then((res) => res.json())
      .then((data) => setScatterData(data))
      .catch((err) => console.error("Error fetching scatter:", err));
  }, [selectedCity]);

  // Fetch City Comparison
  useEffect(() => {
    if (activeTab === "compare" && compCityA && compCityB) {
      fetch(`${API_BASE}/compare?city_a=${encodeURIComponent(compCityA)}&city_b=${encodeURIComponent(compCityB)}`)
        .then((res) => res.json())
        .then((data) => setCompData(data))
        .catch((err) => console.error("Error fetching comparison:", err));
    }
  }, [activeTab, compCityA, compCityB]);

  const toggleRoom = (room: string) => {
    setSelectedRooms((prev) => (prev.includes(room) ? prev.filter((r) => r !== room) : [...prev, room]));
  };

  const getAqiColor = (aqi: number) => {
    if (aqi <= 50) return "#2ecc71";
    if (aqi <= 100) return "#f1c40f";
    if (aqi <= 150) return "#e67e22";
    return "#e74c3c";
  };

  return (
    <div className={darkMode ? "dark" : ""} style={{ minHeight: "100vh", backgroundColor: "var(--bg)" }}>
      {/* Top Inside Airbnb Header */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "16px 32px",
          borderBottom: "1px solid var(--card-border)",
          backgroundColor: "var(--bg)",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: "1.45rem", fontWeight: 800, color: "#ff385c", letterSpacing: "-0.5px" }}>
            Inside Airbnb
          </span>
          <span
            style={{
              fontSize: "1.05rem",
              fontWeight: 500,
              color: "var(--text-main)",
              borderLeft: "1px solid var(--card-border)",
              paddingLeft: 12,
            }}
          >
            Paying for Clean Air?
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span
            style={{
              fontSize: "0.82rem",
              fontWeight: 600,
              backgroundColor: "var(--card-bg)",
              border: "1px solid var(--card-border)",
              padding: "6px 14px",
              borderRadius: 20,
              color: "var(--text-sub)",
            }}
          >
            30 Global Cities Research
          </span>
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              background: "none",
              border: "1px solid var(--card-border)",
              padding: "6px 12px",
              borderRadius: 8,
              color: "var(--text-main)",
            }}
          >
            {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            <span style={{ fontSize: "0.85rem" }}>{darkMode ? "Light" : "Dark"}</span>
          </button>
        </div>
      </header>

      {/* Main Content Container */}
      <main style={{ maxWidth: 1400, margin: "0 auto", padding: "24px 32px" }}>
        {/* Filter Controls Row */}
        <section
          style={{
            backgroundColor: "var(--card-bg)",
            border: "1px solid var(--card-border)",
            borderRadius: 12,
            padding: "20px 24px",
            marginBottom: 24,
            display: "grid",
            gridTemplateColumns: "1.4fr 1.6fr 1.2fr 1.2fr",
            gap: 20,
            alignItems: "center",
          }}
        >
          {/* City Selector */}
          <div>
            <label style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
              📍 Select City
            </label>
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: 8,
                marginTop: 6,
                border: "1px solid var(--card-border)",
                backgroundColor: "var(--bg)",
                color: "var(--text-main)",
                fontSize: "0.95rem",
              }}
            >
              {cities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Room Type Pills */}
          <div>
            <label style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
              🏠 Room Type
            </label>
            <div style={{ display: "flex", gap: 6, marginTop: 6, flexWrap: "wrap" }}>
              {roomTypes.map((rt) => {
                const active = selectedRooms.includes(rt);
                return (
                  <button
                    key={rt}
                    onClick={() => toggleRoom(rt)}
                    style={{
                      fontSize: "0.8rem",
                      fontWeight: 600,
                      padding: "6px 10px",
                      borderRadius: 16,
                      border: active ? "1px solid #ff385c" : "1px solid var(--card-border)",
                      backgroundColor: active ? "#ff385c" : "var(--bg)",
                      color: active ? "#fff" : "var(--text-sub)",
                      transition: "0.15s ease",
                    }}
                  >
                    {rt}
                  </button>
                );
              })}
            </div>
          </div>

          {/* AQI Range Inputs */}
          <div>
            <label style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
              🌫️ AQI Range (Manual Input)
            </label>
            <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
              <input
                type="number"
                value={minAqi}
                onChange={(e) => setMinAqi(Number(e.target.value))}
                placeholder="Min"
                style={{
                  width: "50%",
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--card-border)",
                  backgroundColor: "var(--bg)",
                  color: "var(--text-main)",
                }}
              />
              <input
                type="number"
                value={maxAqi}
                onChange={(e) => setMaxAqi(Number(e.target.value))}
                placeholder="Max"
                style={{
                  width: "50%",
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--card-border)",
                  backgroundColor: "var(--bg)",
                  color: "var(--text-main)",
                }}
              />
            </div>
          </div>

          {/* Price Range Inputs */}
          <div>
            <label style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
              💵 Price Range (₹ INR)
            </label>
            <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
              <input
                type="number"
                value={minPrice}
                onChange={(e) => setMinPrice(Number(e.target.value))}
                placeholder="Min"
                style={{
                  width: "50%",
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--card-border)",
                  backgroundColor: "var(--bg)",
                  color: "var(--text-main)",
                }}
              />
              <input
                type="number"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
                placeholder="Max"
                style={{
                  width: "50%",
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--card-border)",
                  backgroundColor: "var(--bg)",
                  color: "var(--text-main)",
                }}
              />
            </div>
          </div>
        </section>

        {/* Hero Editorial Statement */}
        <section
          style={{
            backgroundColor: "var(--card-bg)",
            border: "1px solid var(--card-border)",
            borderRadius: 12,
            padding: "24px 28px",
            marginBottom: 24,
          }}
        >
          <h1 style={{ margin: "0 0 8px 0", fontSize: "1.85rem", fontWeight: 800 }}>
            {selectedCity === "All Cities (Global View)" ? "30 Global Metropolitan Areas" : selectedCity}
          </h1>
          <p style={{ margin: 0, fontSize: "0.95rem", color: "var(--text-sub)", lineHeight: 1.6, maxWidth: 900 }}>
            Investigating how urban air quality (AQI) intersects with short-term rental nightly prices. Do hosts in
            clean-air zones command a price premium? Explore spatial distributions, room type segmentation, and
            comparative analytics.
          </p>
        </section>

        {/* Big Number Stat Cards */}
        {stats && (
          <section
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, 1fr)",
              gap: 16,
              marginBottom: 28,
            }}
          >
            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 10,
                padding: "16px 20px",
              }}
            >
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
                Total Listings
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#ff385c", marginTop: 4 }}>
                {stats.total_listings.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-sub)", marginTop: 2 }}>in current filter</div>
            </div>

            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 10,
                padding: "16px 20px",
              }}
            >
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
                Entire Homes
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, marginTop: 4 }}>{stats.entire_home_pct}%</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-sub)", marginTop: 2 }}>residential pressure</div>
            </div>

            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 10,
                padding: "16px 20px",
              }}
            >
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
                Median Price
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#008489", marginTop: 4 }}>
                ₹{stats.median_price.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-sub)", marginTop: 2 }}>per night (INR)</div>
            </div>

            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 10,
                padding: "16px 20px",
              }}
            >
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
                Mean AQI
              </div>
              <div
                style={{
                  fontSize: "1.8rem",
                  fontWeight: 800,
                  color: stats.mean_aqi <= 50 ? "#2ecc71" : stats.mean_aqi <= 100 ? "#f1c40f" : "#e74c3c",
                  marginTop: 4,
                }}
              >
                {stats.mean_aqi}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-sub)", marginTop: 2 }}>
                {stats.mean_aqi <= 50 ? "Good" : stats.mean_aqi <= 100 ? "Moderate" : "Unhealthy"}
              </div>
            </div>

            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 10,
                padding: "16px 20px",
              }}
            >
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-sub)", textTransform: "uppercase" }}>
                Clean Air Ratio
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, marginTop: 4 }}>{stats.clean_air_pct}%</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-sub)", marginTop: 2 }}>listings in AQI ≤ 50</div>
            </div>
          </section>
        )}

        {/* Tab Navigation Navigation */}
        <div style={{ display: "flex", gap: 24, borderBottom: "1px solid var(--card-border)", marginBottom: 24 }}>
          {[
            { id: "map", label: "🗺️ Interactive Map" },
            { id: "premium", label: "🌿 Clean Air Premium (Interactive Charts)" },
            { id: "compare", label: "⚖️ City-to-City Comparison" },
            { id: "data", label: "📋 Raw Data Explorer" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              style={{
                background: "none",
                border: "none",
                padding: "10px 4px",
                fontSize: "0.95rem",
                fontWeight: 600,
                color: activeTab === t.id ? "#ff385c" : "var(--text-sub)",
                borderBottom: activeTab === t.id ? "3px solid #ff385c" : "3px solid transparent",
                cursor: "pointer",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab 1: Interactive Map View */}
        {activeTab === "map" && (
          <section>
            <div style={{ marginBottom: 14 }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 700, margin: "0 0 4px 0" }}>
                Spatial Distribution & Density
              </h2>
              <p style={{ margin: 0, fontSize: "0.88rem", color: "var(--text-sub)" }}>
                Displaying {listings.length} geo-referenced listings. Points colored by Air Quality Index (AQI).
              </p>
            </div>

            {/* Custom SVG Point Canvas Map View */}
            <div
              style={{
                width: "100%",
                height: 520,
                backgroundColor: darkMode ? "#181f2a" : "#e8edf2",
                borderRadius: 12,
                border: "1px solid var(--card-border)",
                position: "relative",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {listings.length === 0 ? (
                <span style={{ color: "var(--text-sub)" }}>No listings found for this filter.</span>
              ) : (
                <svg width="100%" height="100%" style={{ position: "absolute", top: 0, left: 0 }}>
                  {(() => {
                    const lats = listings.map((l) => l.latitude);
                    const lons = listings.map((l) => l.longitude);
                    const minLat = Math.min(...lats);
                    const maxLat = Math.max(...lats);
                    const minLon = Math.min(...lons);
                    const maxLon = Math.max(...lons);

                    return listings.map((l) => {
                      const xPercent = ((l.longitude - minLon) / (maxLon - minLon || 1)) * 90 + 5;
                      const yPercent = (1 - (l.latitude - minLat) / (maxLat - minLat || 1)) * 85 + 7;
                      return (
                        <circle
                          key={l.listing_id}
                          cx={`${xPercent}%`}
                          cy={`${yPercent}%`}
                          r="4"
                          fill={getAqiColor(l.aqi)}
                          stroke="#ffffff"
                          strokeWidth="0.8"
                          opacity="0.8"
                        >
                          <title>
                            {`${l.city} - ${l.neighbourhood}\nRoom: ${l.room_type}\nPrice: ₹${l.price_inr.toLocaleString()}\nAQI: ${l.aqi} (${l.aqi_category})`}
                          </title>
                        </circle>
                      );
                    });
                  })()}
                </svg>
              )}
            </div>

            {/* Map Legend */}
            <div style={{ display: "flex", gap: 20, marginTop: 12, fontSize: "0.85rem" }}>
              <span>🟢 Good (AQI ≤ 50)</span>
              <span>🟡 Moderate (51–100)</span>
              <span>🟠 Unhealthy for SG (101–150)</span>
              <span>🔴 Unhealthy / Hazardous (151+)</span>
            </div>
          </section>
        )}

        {/* Tab 2: Clean Air Premium Interactive Charts */}
        {activeTab === "premium" && (
          <section style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 24 }}>
            {/* Scatter Plot: Price vs AQI */}
            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 12,
                padding: "20px 24px",
              }}
            >
              <h3 style={{ margin: "0 0 6px 0", fontSize: "1.15rem", fontWeight: 700 }}>
                Nightly Price vs. Air Quality Index
              </h3>
              <p style={{ margin: "0 0 16px 0", fontSize: "0.85rem", color: "var(--text-sub)" }}>
                Testing price elasticity against AQI with interactive tooltips and zoom.
              </p>

              {scatterData && (
                <div style={{ width: "100%", height: 380 }}>
                  <ResponsiveContainer>
                    <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis type="number" dataKey="aqi" name="AQI" label={{ value: "AQI", position: "bottom", offset: 0 }} />
                      <YAxis
                        type="number"
                        dataKey="price_inr"
                        name="Price"
                        tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                        label={{ value: "Price (₹)", angle: -90, position: "left" }}
                      />
                      <Tooltip
                        cursor={{ strokeDasharray: "3 3" }}
                        formatter={(val: any, name: any) =>
                          name === "Price" ? [`₹${Number(val).toLocaleString()}`, "Price"] : [val, "AQI"]
                        }
                      />
                      <Scatter data={scatterData.points} fill="#ff385c" opacity={0.6} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Bar Chart: City Mean AQI Ranking */}
            <div
              style={{
                backgroundColor: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                borderRadius: 12,
                padding: "20px 24px",
              }}
            >
              <h3 style={{ margin: "0 0 6px 0", fontSize: "1.15rem", fontWeight: 700 }}>
                Mean AQI by City (Interactive Bar Chart)
              </h3>
              <p style={{ margin: "0 0 16px 0", fontSize: "0.85rem", color: "var(--text-sub)" }}>
                Green bars reflect WHO clean air compliance (&lt;= 50).
              </p>

              <div style={{ width: "100%", height: 380 }}>
                <ResponsiveContainer>
                  <BarChart data={aqiRanking.slice(0, 15)} margin={{ top: 10, right: 20, bottom: 50, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="city" angle={-45} textAnchor="end" interval={0} height={60} />
                    <YAxis label={{ value: "Mean AQI", angle: -90, position: "insideLeft" }} />
                    <Tooltip formatter={(val: any) => [val, "Mean AQI"]} />
                    <Bar dataKey="mean_aqi">
                      {aqiRanking.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getAqiColor(entry.mean_aqi)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>
        )}

        {/* Tab 3: City Comparison */}
        {activeTab === "compare" && (
          <section>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
              <div>
                <label style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-sub)" }}>Select City A</label>
                <select
                  value={compCityA}
                  onChange={(e) => setCompCityA(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: 8,
                    marginTop: 6,
                    border: "1px solid var(--card-border)",
                    backgroundColor: "var(--card-bg)",
                    color: "var(--text-main)",
                  }}
                >
                  {cities
                    .filter((c) => c !== "All Cities (Global View)")
                    .map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-sub)" }}>Select City B</label>
                <select
                  value={compCityB}
                  onChange={(e) => setCompCityB(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: 8,
                    marginTop: 6,
                    border: "1px solid var(--card-border)",
                    backgroundColor: "var(--card-bg)",
                    color: "var(--text-main)",
                  }}
                >
                  {cities
                    .filter((c) => c !== "All Cities (Global View)")
                    .map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                </select>
              </div>
            </div>

            {/* Comparison Cards & Tables */}
            {compData && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                {/* City A Card */}
                <div
                  style={{
                    backgroundColor: "var(--card-bg)",
                    border: "1px solid var(--card-border)",
                    borderRadius: 12,
                    padding: "20px 24px",
                  }}
                >
                  <h3 style={{ margin: "0 0 16px 0", fontSize: "1.3rem", fontWeight: 800 }}>{compData.city_a.name}</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}>Mean AQI</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{compData.city_a.summary?.mean_aqi}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}>Median Price</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#008489" }}>
                        ₹{compData.city_a.summary?.median_price?.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}>Clean Air %</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{compData.city_a.summary?.clean_air_pct}%</div>
                    </div>
                  </div>

                  <h4 style={{ fontSize: "0.95rem", margin: "0 0 8px 0" }}>Top Rated Stays in Clean Air Zone (AQI ≤ 50)</h4>
                  <table style={{ width: "100%", fontSize: "0.82rem", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--card-border)", textAlign: "left" }}>
                        <th style={{ padding: "6px 4px" }}>Neighbourhood</th>
                        <th style={{ padding: "6px 4px" }}>Price</th>
                        <th style={{ padding: "6px 4px" }}>Rating</th>
                        <th style={{ padding: "6px 4px" }}>AQI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {compData.city_a.top_stays.map((s, idx) => (
                        <tr key={idx} style={{ borderBottom: "1px solid var(--card-border)" }}>
                          <td style={{ padding: "6px 4px" }}>{s.neighbourhood}</td>
                          <td style={{ padding: "6px 4px", fontWeight: 600 }}>₹{s.price_inr.toLocaleString()}</td>
                          <td style={{ padding: "6px 4px" }}>{s.review_scores_rating} ⭐</td>
                          <td style={{ padding: "6px 4px", color: getAqiColor(s.aqi), fontWeight: 700 }}>{s.aqi}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* City B Card */}
                <div
                  style={{
                    backgroundColor: "var(--card-bg)",
                    border: "1px solid var(--card-border)",
                    borderRadius: 12,
                    padding: "20px 24px",
                  }}
                >
                  <h3 style={{ margin: "0 0 16px 0", fontSize: "1.3rem", fontWeight: 800 }}>{compData.city_b.name}</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}>Mean AQI</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{compData.city_b.summary?.mean_aqi}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}>Median Price</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#008489" }}>
                        ₹{compData.city_b.summary?.median_price?.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}>Clean Air %</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{compData.city_b.summary?.clean_air_pct}%</div>
                    </div>
                  </div>

                  <h4 style={{ fontSize: "0.95rem", margin: "0 0 8px 0" }}>Top Rated Stays in Clean Air Zone (AQI ≤ 50)</h4>
                  <table style={{ width: "100%", fontSize: "0.82rem", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--card-border)", textAlign: "left" }}>
                        <th style={{ padding: "6px 4px" }}>Neighbourhood</th>
                        <th style={{ padding: "6px 4px" }}>Price</th>
                        <th style={{ padding: "6px 4px" }}>Rating</th>
                        <th style={{ padding: "6px 4px" }}>AQI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {compData.city_b.top_stays.map((s, idx) => (
                        <tr key={idx} style={{ borderBottom: "1px solid var(--card-border)" }}>
                          <td style={{ padding: "6px 4px" }}>{s.neighbourhood}</td>
                          <td style={{ padding: "6px 4px", fontWeight: 600 }}>₹{s.price_inr.toLocaleString()}</td>
                          <td style={{ padding: "6px 4px" }}>{s.review_scores_rating} ⭐</td>
                          <td style={{ padding: "6px 4px", color: getAqiColor(s.aqi), fontWeight: 700 }}>{s.aqi}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Tab 4: Raw Data Explorer */}
        {activeTab === "data" && (
          <section
            style={{
              backgroundColor: "var(--card-bg)",
              border: "1px solid var(--card-border)",
              borderRadius: 12,
              padding: "20px 24px",
            }}
          >
            <h3 style={{ margin: "0 0 12px 0", fontSize: "1.2rem", fontWeight: 800 }}>Filtered Listings Explorer</h3>
            <div style={{ maxHeight: 500, overflowY: "auto" }}>
              <table style={{ width: "100%", fontSize: "0.85rem", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid var(--card-border)", textAlign: "left" }}>
                    <th style={{ padding: "8px" }}>ID</th>
                    <th style={{ padding: "8px" }}>City</th>
                    <th style={{ padding: "8px" }}>Neighbourhood</th>
                    <th style={{ padding: "8px" }}>Room</th>
                    <th style={{ padding: "8px" }}>Price (₹)</th>
                    <th style={{ padding: "8px" }}>AQI</th>
                    <th style={{ padding: "8px" }}>Category</th>
                    <th style={{ padding: "8px" }}>Rating</th>
                  </tr>
                </thead>
                <tbody>
                  {listings.slice(0, 100).map((l) => (
                    <tr key={l.listing_id} style={{ borderBottom: "1px solid var(--card-border)" }}>
                      <td style={{ padding: "8px" }}>{l.listing_id}</td>
                      <td style={{ padding: "8px" }}>{l.city}</td>
                      <td style={{ padding: "8px" }}>{l.neighbourhood}</td>
                      <td style={{ padding: "8px" }}>{l.room_type}</td>
                      <td style={{ padding: "8px", fontWeight: 600 }}>₹{l.price_inr.toLocaleString()}</td>
                      <td style={{ padding: "8px", color: getAqiColor(l.aqi), fontWeight: 700 }}>{l.aqi}</td>
                      <td style={{ padding: "8px" }}>{l.aqi_category}</td>
                      <td style={{ padding: "8px" }}>{l.review_scores_rating} ⭐</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      {/* Inside Airbnb Footer */}
      <footer
        style={{
          marginTop: 60,
          padding: "30px 20px",
          borderTop: "1px solid var(--card-border)",
          backgroundColor: "var(--card-bg)",
          textAlign: "center",
          color: "var(--text-sub)",
          fontSize: "0.85rem",
        }}
      >
        <b>Inside Airbnb: Paying for Clean Air?</b> — Built with React, TypeScript & FastAPI.
      </footer>
    </div>
  );
}
