"""
06_static_charts_for_pdf.py
----------------------------
Matplotlib versions of the key charts, saved as PNGs, used to illustrate
the PDF write-up (the interactive Plotly dashboard covers on-screen /
portfolio-site use; PDFs need static images).
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = "/home/claude/airline-network-analysis"
scored = pd.read_csv(f"{BASE}/data/processed/routes_scored.csv")
clean = pd.read_csv(f"{BASE}/data/processed/routes_clean.csv")
centrality = pd.read_csv(f"{BASE}/data/processed/airport_centrality.csv")
candidates = pd.read_csv(f"{BASE}/data/processed/new_route_candidates.csv")
with open(f"{BASE}/data/processed/network_summary.json") as f:
    summary = json.load(f)

OUT = f"{BASE}/outputs/charts"
COLORS = {"EXPAND": "#1a7f37", "MAINTAIN": "#2f6fed", "MONITOR": "#e8a33d", "CUT / RESTRUCTURE": "#d1453b"}
plt.rcParams.update({"font.size": 10, "figure.facecolor": "white", "axes.facecolor": "white"})


def savefig(name):
    plt.tight_layout()
    plt.savefig(f"{OUT}/{name}", dpi=180, bbox_inches="tight")
    plt.close()


# Chart A: Top 10 profit routes
top10 = scored.nlargest(10, "operating_profit").sort_values("operating_profit")
plt.figure(figsize=(8, 5))
plt.barh(top10["route"], top10["operating_profit"] / 1e6,
         color=[COLORS[r] for r in top10["recommendation"]])
plt.xlabel("Annual Operating Profit ($M)")
plt.title("Top 10 Routes by Annual Operating Profit")
savefig("pdf_top10_profit.png")

# Chart B: Bottom 10 margin routes
bottom10 = scored.nsmallest(10, "operating_margin_pct").sort_values("operating_margin_pct")
plt.figure(figsize=(8, 5))
plt.barh(bottom10["route"], bottom10["operating_margin_pct"],
         color=[COLORS[r] for r in bottom10["recommendation"]])
plt.xlabel("Operating Margin (%)")
plt.title("10 Lowest Operating-Margin Routes")
savefig("pdf_bottom10_margin.png")

# Chart C: Seasonal demand
seasonal = clean.groupby("quarter", as_index=False)["passengers"].sum()
plt.figure(figsize=(7, 4))
plt.plot(seasonal["quarter"], seasonal["passengers"] / 1e6, marker="o", linewidth=2, color="#2f6fed")
plt.xticks([1, 2, 3, 4], ["Q1", "Q2", "Q3", "Q4"])
plt.ylabel("Network Passengers (Millions)")
plt.title("Network-Wide Seasonal Demand")
plt.grid(alpha=0.3)
savefig("pdf_seasonal_demand.png")

# Chart D: Airport centrality
top_cent = centrality.sort_values("eigenvector_centrality", ascending=True).tail(12)
plt.figure(figsize=(8, 5.5))
bar_colors = ["#0b3d91" if t == "hub" else "#8a94a6" for t in top_cent["tier"]]
plt.barh(top_cent["name"], top_cent["eigenvector_centrality"], color=bar_colors)
plt.xlabel("Eigenvector Centrality (network influence)")
plt.title("Airport Network Influence")
savefig("pdf_centrality.png")

# Chart E: Recommendation mix (pie)
mix = scored["recommendation"].value_counts()
plt.figure(figsize=(6, 6))
plt.pie(mix.values, labels=mix.index, autopct="%1.0f%%",
        colors=[COLORS[k] for k in mix.index], startangle=90,
        wedgeprops=dict(width=0.45))
plt.title("Route Portfolio: Recommendation Mix (234 routes)")
savefig("pdf_recommendation_mix.png")

# Chart F: New route candidates
cand = candidates.sort_values("estimated_annual_connecting_demand")
plt.figure(figsize=(8, 5))
plt.barh(cand["origin_city"] + " - " + cand["dest_city"],
          cand["estimated_annual_connecting_demand"], color="#2f6fed")
plt.xlabel("Estimated Annual Connecting Demand (passengers)")
plt.title("Top New Nonstop Route Candidates")
savefig("pdf_new_route_candidates.png")

# Chart G: Network resilience
resilience = summary["network_resilience_by_hub_removed_pct"]
plt.figure(figsize=(7, 4))
hubs = list(resilience.keys())
vals = list(resilience.values())
plt.bar(hubs, vals, color="#d1453b")
plt.ylabel("% of Network Still Connected")
plt.title("Network Resilience if Each Hub Is Removed")
plt.ylim(90, 100)
plt.grid(axis="y", alpha=0.3)
savefig("pdf_resilience.png")

print("Static PNG charts saved to outputs/charts/ for PDF use")
