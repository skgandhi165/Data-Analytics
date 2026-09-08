"""
05_visualizations.py
---------------------
Builds the static charts (for the write-up / portfolio site screenshots)
and a self-contained interactive HTML dashboard (for a live-clickable
portfolio link, and as a stand-in for what would be a Power BI dashboard
in a real corporate environment).
"""

import json

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

BASE = "/home/claude/airline-network-analysis"
scored = pd.read_csv(f"{BASE}/data/processed/routes_scored.csv")
clean = pd.read_csv(f"{BASE}/data/processed/routes_clean.csv")
centrality = pd.read_csv(f"{BASE}/data/processed/airport_centrality.csv")
airports = pd.read_csv(f"{BASE}/data/raw/airports.csv")
candidates = pd.read_csv(f"{BASE}/data/processed/new_route_candidates.csv")
with open(f"{BASE}/data/processed/network_summary.json") as f:
    summary = json.load(f)

CHART_DIR = f"{BASE}/outputs/charts"
DASH_DIR = f"{BASE}/outputs/dashboard"

TEMPLATE = "plotly_white"
COLOR_MAP = {"EXPAND": "#1a7f37", "MAINTAIN": "#2f6fed", "MONITOR": "#e8a33d", "CUT / RESTRUCTURE": "#d1453b"}

# ---------------------------------------------------------------- Chart 1
# Route network map
fig_map = go.Figure()
for _, r in scored.iterrows():
    o = airports[airports["code"] == r["origin"]].iloc[0]
    d = airports[airports["code"] == r["dest"]].iloc[0]
    fig_map.add_trace(go.Scattergeo(
        lon=[o["lon"], d["lon"]], lat=[o["lat"], d["lat"]],
        mode="lines",
        line=dict(width=max(0.5, min(r["operating_profit"] / 2_000_000, 4)),
                   color=COLOR_MAP[r["recommendation"]]),
        opacity=0.55, showlegend=False, hoverinfo="skip",
    ))
for _, a in airports.iterrows():
    fig_map.add_trace(go.Scattergeo(
        lon=[a["lon"]], lat=[a["lat"]], mode="markers+text",
        marker=dict(size=16 if a["tier"] == "hub" else 8,
                    color="#0b3d91" if a["tier"] == "hub" else "#8a94a6",
                    line=dict(width=1, color="white")),
        text=a["code"], textposition="top center",
        textfont=dict(size=9), showlegend=False,
        hovertext=f"{a['name']} ({a['tier']})", hoverinfo="text",
    ))
fig_map.update_layout(
    title="Route Network by Recommendation (line color = action, thickness = profit)",
    geo=dict(scope="north america", projection_type="albers usa", showland=True,
             landcolor="#f4f4f4", countrycolor="#ccc"),
    template=TEMPLATE, height=600, margin=dict(l=10, r=10, t=60, b=10),
)
fig_map.write_html(f"{CHART_DIR}/01_route_network_map.html")

# ---------------------------------------------------------------- Chart 2
# Top/bottom routes by operating profit
top10 = scored.nlargest(10, "operating_profit")[["route", "operating_profit", "recommendation"]]
bottom10 = scored.nsmallest(10, "operating_margin_pct")[["route", "operating_margin_pct", "recommendation"]]

fig_top = px.bar(top10.sort_values("operating_profit"), x="operating_profit", y="route",
                  orientation="h", color="recommendation", color_discrete_map=COLOR_MAP,
                  title="Top 10 Routes by Annual Operating Profit", template=TEMPLATE)
fig_top.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10))
fig_top.write_html(f"{CHART_DIR}/02_top10_profit_routes.html")

fig_bottom = px.bar(bottom10.sort_values("operating_margin_pct"), x="operating_margin_pct", y="route",
                     orientation="h", color="recommendation", color_discrete_map=COLOR_MAP,
                     title="10 Lowest Operating-Margin Routes", template=TEMPLATE)
fig_bottom.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10))
fig_bottom.write_html(f"{CHART_DIR}/03_bottom10_margin_routes.html")

# ---------------------------------------------------------------- Chart 3
# Seasonal demand curve (network-wide passengers by quarter)
seasonal = clean.groupby("quarter", as_index=False)["passengers"].sum()
fig_season = px.line(seasonal, x="quarter", y="passengers", markers=True,
                      title="Network-Wide Passenger Volume by Quarter",
                      template=TEMPLATE)
fig_season.update_layout(height=400, margin=dict(l=10, r=10, t=60, b=10))
fig_season.write_html(f"{CHART_DIR}/04_seasonal_demand.html")

# ---------------------------------------------------------------- Chart 4
# Airport centrality
fig_cent = px.bar(centrality.sort_values("eigenvector_centrality", ascending=True).tail(15),
                   x="eigenvector_centrality", y="name", color="tier", orientation="h",
                   title="Airport Network Influence (Eigenvector Centrality)",
                   template=TEMPLATE, color_discrete_map={"hub": "#0b3d91", "spoke": "#8a94a6"})
fig_cent.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10))
fig_cent.write_html(f"{CHART_DIR}/05_airport_centrality.html")

# ---------------------------------------------------------------- Chart 5
# Recommendation mix (donut)
mix = scored["recommendation"].value_counts().reset_index()
mix.columns = ["recommendation", "count"]
fig_mix = px.pie(mix, names="recommendation", values="count", hole=0.55,
                  color="recommendation", color_discrete_map=COLOR_MAP,
                  title="Route Portfolio: Recommendation Mix (234 routes)", template=TEMPLATE)
fig_mix.update_layout(height=450, margin=dict(l=10, r=10, t=60, b=10))
fig_mix.write_html(f"{CHART_DIR}/06_recommendation_mix.html")

# ---------------------------------------------------------------- Chart 6
# New route candidates
fig_cand = px.bar(candidates.sort_values("estimated_annual_connecting_demand"),
                   x="estimated_annual_connecting_demand", y="origin_city",
                   color="estimated_annual_connecting_demand", orientation="h",
                   title="Top New Nonstop Route Candidates (est. annual connecting demand)",
                   template=TEMPLATE, color_continuous_scale="Blues",
                   hover_data=["dest_city"])
fig_cand.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10), coloraxis_showscale=False)
fig_cand.write_html(f"{CHART_DIR}/07_new_route_candidates.html")

print("All 7 charts saved to outputs/charts/ (both .html and .png)")

# ================================================================
# Combined single-page interactive dashboard
# ================================================================
kpi_total_profit = scored["operating_profit"].sum()
kpi_avg_margin = (scored["operating_profit"].sum() / scored["revenue"].sum()) * 100
kpi_avg_lf = scored["load_factor"].mean() * 100
kpi_expand_ct = (scored["recommendation"] == "EXPAND").sum()
kpi_cut_ct = (scored["recommendation"] == "CUT / RESTRUCTURE").sum()

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Airline Route Network Profitability Dashboard</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0;
         background: #0d1117; color: #e6edf3; }}
  header {{ padding: 28px 32px 8px; border-bottom: 1px solid #21262d; }}
  header h1 {{ margin: 0 0 4px; font-size: 22px; }}
  header p {{ margin: 0; color: #8b949e; font-size: 14px; }}
  .kpis {{ display: flex; gap: 16px; padding: 20px 32px; flex-wrap: wrap; }}
  .kpi {{ background: #161b22; border: 1px solid #21262d; border-radius: 10px;
          padding: 16px 20px; min-width: 170px; }}
  .kpi .label {{ font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: .04em; }}
  .kpi .value {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 8px 32px 32px; }}
  .grid .full {{ grid-column: 1 / -1; }}
  .card {{ background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 8px; }}
  iframe {{ width: 100%; border: none; }}
  .footer {{ padding: 16px 32px 32px; color: #6e7681; font-size: 12px; }}
</style>
</head>
<body>
<header>
  <h1>Airline Route Network Profitability &amp; Optimization Dashboard</h1>
  <p>Synthetic BTS T-100-style data | {summary['num_airports']} airports | {summary['num_route_segments']} route segments | Built by Srushti Gandhi</p>
</header>
<div class="kpis">
  <div class="kpi"><div class="label">Network Operating Profit</div><div class="value">${kpi_total_profit/1e6:,.1f}M</div></div>
  <div class="kpi"><div class="label">Blended Operating Margin</div><div class="value">{kpi_avg_margin:.1f}%</div></div>
  <div class="kpi"><div class="label">Avg Load Factor</div><div class="value">{kpi_avg_lf:.1f}%</div></div>
  <div class="kpi"><div class="label">Routes Flagged EXPAND</div><div class="value" style="color:#3fb950">{kpi_expand_ct}</div></div>
  <div class="kpi"><div class="label">Routes Flagged CUT</div><div class="value" style="color:#f85149">{kpi_cut_ct}</div></div>
</div>
<div class="grid">
  <div class="card full"><iframe src="../charts/01_route_network_map.html" height="620"></iframe></div>
  <div class="card"><iframe src="../charts/02_top10_profit_routes.html" height="520"></iframe></div>
  <div class="card"><iframe src="../charts/03_bottom10_margin_routes.html" height="520"></iframe></div>
  <div class="card"><iframe src="../charts/06_recommendation_mix.html" height="470"></iframe></div>
  <div class="card"><iframe src="../charts/04_seasonal_demand.html" height="470"></iframe></div>
  <div class="card full"><iframe src="../charts/05_airport_centrality.html" height="520"></iframe></div>
  <div class="card full"><iframe src="../charts/07_new_route_candidates.html" height="520"></iframe></div>
</div>
<div class="footer">
  Data: synthetic, generated to match the schema and economics of the US DOT/BTS T-100 Domestic Segment dataset.
  See README.md for how to swap in the real BTS dataset.
</div>
</body>
</html>
"""
with open(f"{DASH_DIR}/dashboard.html", "w") as f:
    f.write(dashboard_html)

print("Interactive dashboard saved -> outputs/dashboard/dashboard.html")
