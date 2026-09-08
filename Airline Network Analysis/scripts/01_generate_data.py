"""
01_generate_data.py
--------------------
Generates a synthetic, BTS-style domestic airline route dataset.

WHY SYNTHETIC DATA:
Real BTS (Bureau of Transportation Statistics) datasets — T-100 Segment
data and DB1B ticket pricing data — are the gold-standard free sources
for this kind of project (transtats.bts.gov). This environment doesn't
have live internet access to pull them directly, so this script builds
a synthetic dataset that mirrors the real T-100 schema and realistic
route economics (hub-and-spoke structure, seasonal demand, distance-based
pricing, load factors).

TO SWAP IN REAL DATA LATER:
Go to https://www.transtats.bts.gov/DL_SelectFields.asp?gnoyr_VQ=FMF
and download "T-100 Domestic Segment (All Carriers)" for your date range.
The column names below (origin, dest, carrier, passengers, seats,
distance, quarter) match the real T-100 field names closely enough that
scripts 02-04 will work with only minor column-renaming changes.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

# ---- Airport network: a realistic hub-and-spoke structure -----------------
# 5 major hubs + 20 spoke cities, modeled loosely on a major US/Canada carrier
HUBS = {
    "ORD": {"name": "Chicago O'Hare", "lat": 41.98, "lon": -87.90, "tier": "hub"},
    "DFW": {"name": "Dallas/Fort Worth", "lat": 32.90, "lon": -97.04, "tier": "hub"},
    "DEN": {"name": "Denver", "lat": 39.86, "lon": -104.67, "tier": "hub"},
    "ATL": {"name": "Atlanta", "lat": 33.64, "lon": -84.43, "tier": "hub"},
    "SEA": {"name": "Seattle-Tacoma", "lat": 47.45, "lon": -122.31, "tier": "hub"},
}

SPOKES = {
    "LAX": {"name": "Los Angeles", "lat": 33.94, "lon": -118.41, "tier": "spoke"},
    "JFK": {"name": "New York JFK", "lat": 40.64, "lon": -73.78, "tier": "spoke"},
    "MIA": {"name": "Miami", "lat": 25.79, "lon": -80.29, "tier": "spoke"},
    "PHX": {"name": "Phoenix", "lat": 33.43, "lon": -112.01, "tier": "spoke"},
    "IAH": {"name": "Houston", "lat": 29.98, "lon": -95.34, "tier": "spoke"},
    "BOS": {"name": "Boston", "lat": 42.36, "lon": -71.01, "tier": "spoke"},
    "SFO": {"name": "San Francisco", "lat": 37.62, "lon": -122.38, "tier": "spoke"},
    "LAS": {"name": "Las Vegas", "lat": 36.08, "lon": -115.15, "tier": "spoke"},
    "MSP": {"name": "Minneapolis", "lat": 44.88, "lon": -93.22, "tier": "spoke"},
    "DTW": {"name": "Detroit", "lat": 42.21, "lon": -83.35, "tier": "spoke"},
    "PDX": {"name": "Portland", "lat": 45.59, "lon": -122.60, "tier": "spoke"},
    "SLC": {"name": "Salt Lake City", "lat": 40.79, "lon": -111.98, "tier": "spoke"},
    "STL": {"name": "St. Louis", "lat": 38.75, "lon": -90.37, "tier": "spoke"},
    "MCI": {"name": "Kansas City", "lat": 39.30, "lon": -94.71, "tier": "spoke"},
    "OMA": {"name": "Omaha", "lat": 41.30, "lon": -95.89, "tier": "spoke"},
    "BOI": {"name": "Boise", "lat": 43.56, "lon": -116.22, "tier": "spoke"},
    "TUL": {"name": "Tulsa", "lat": 36.20, "lon": -95.89, "tier": "spoke"},
    "GEG": {"name": "Spokane", "lat": 47.62, "lon": -117.53, "tier": "spoke"},
    "FAR": {"name": "Fargo", "lat": 46.92, "lon": -96.82, "tier": "spoke"},
    "BIL": {"name": "Billings", "lat": 45.81, "lon": -108.54, "tier": "spoke"},
}

AIRPORTS = {**HUBS, **SPOKES}


def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def build_route_list():
    """Every hub connects to every spoke (hub-and-spoke). Hubs also
    connect to each other (trunk routes). A handful of spoke-spoke
    'point-to-point' routes exist on the highest-demand pairs."""
    routes = []
    for h in HUBS:
        for s in SPOKES:
            routes.append((h, s))
    hub_list = list(HUBS)
    for i in range(len(hub_list)):
        for j in range(i + 1, len(hub_list)):
            routes.append((hub_list[i], hub_list[j]))
    # A few high-demand spoke-to-spoke leisure/business routes
    point_to_point = [
        ("LAX", "JFK"), ("SFO", "JFK"), ("LAX", "LAS"), ("MIA", "JFK"),
        ("BOS", "JFK"), ("PHX", "LAS"), ("SLC", "BOI"),
    ]
    routes.extend(point_to_point)
    return routes


def simulate_route(origin, dest, quarter, base_demand_index):
    o, d = AIRPORTS[origin], AIRPORTS[dest]
    distance = haversine_miles(o["lat"], o["lon"], d["lat"], d["lon"])

    # base demand driven by whether endpoints are hubs, plus some randomness
    hub_bonus = (2.2 if o["tier"] == "hub" else 1.0) * (2.2 if d["tier"] == "hub" else 1.0)
    base_pax_per_dep = np.random.normal(115, 20) * min(hub_bonus, 3.0) ** 0.5

    # seasonality: Q3 (summer) up, Q1 (winter, ex. holiday) down, leisure routes (LAS, MIA) spike opposite
    seasonal = {1: 0.90, 2: 1.00, 3: 1.15, 4: 0.98}[quarter]
    if dest in ("LAS", "MIA", "PHX") or origin in ("LAS", "MIA", "PHX"):
        seasonal = {1: 1.10, 2: 0.95, 3: 1.05, 4: 0.95}[quarter]

    departures = int(np.clip(np.random.poisson(60) * (1.4 if o["tier"] == "hub" or d["tier"] == "hub" else 1.0), 20, 400))
    seats_per_dep = np.random.choice([76, 150, 160, 189], p=[0.15, 0.35, 0.30, 0.20])
    seats = departures * seats_per_dep

    load_factor = np.clip(np.random.normal(0.80, 0.08) * seasonal, 0.45, 0.97)
    passengers = int(seats * load_factor)

    # fare/yield: shorter and thinner (monopoly-ish) routes carry higher yield (cents/mile);
    # longer routes have lower per-mile yield but a higher fare floor (standard airline pricing curve)
    competition_factor = 1.05 if (o["tier"] == "spoke" and d["tier"] == "spoke") else 0.90
    base_yield_cents = np.random.normal(15.5, 2.0) * competition_factor * (1000 / distance) ** 0.22
    base_yield_cents = np.clip(base_yield_cents, 7.5, 32.0)
    avg_fare = round(base_yield_cents / 100 * distance + np.random.normal(0, 6), 2)
    avg_fare = max(avg_fare, 59.0 + distance * 0.015)

    revenue = round(avg_fare * passengers, 2)

    # cost proxy: fuel/crew/ownership cost per available seat mile (CASM). CASM falls with stage
    # length (fixed costs like boarding/taxi/climb amortize over more miles) - the standard
    # "stage-length effect" in airline economics - and is lower for larger, more efficient gauges.
    gauge_efficiency = 0.90 if seats_per_dep >= 150 else 1.15
    stage_length_factor = np.clip((650 / distance) ** 0.28, 0.55, 1.6)
    casm_cents = np.random.normal(9.0, 0.8) * gauge_efficiency * stage_length_factor
    asm = seats * distance
    op_cost = round(casm_cents / 100 * asm, 2)

    return {
        "origin": origin, "dest": dest, "quarter": quarter,
        "origin_city": o["name"], "dest_city": d["name"],
        "origin_tier": o["tier"], "dest_tier": d["tier"],
        "distance_miles": round(distance, 1),
        "departures": departures, "seats": seats, "passengers": passengers,
        "load_factor": round(load_factor, 3),
        "avg_fare": avg_fare, "revenue": revenue,
        "op_cost": op_cost, "casm_cents": round(casm_cents, 2),
    }


def main():
    routes = build_route_list()
    rows = []
    for (o, d) in routes:
        for q in [1, 2, 3, 4]:
            rows.append(simulate_route(o, d, q, None))
            # reverse direction (airlines report both directions of a segment)
            rows.append(simulate_route(d, o, q, None))

    df = pd.DataFrame(rows)
    df.to_csv("/home/claude/airline-network-analysis/data/raw/t100_style_route_data.csv", index=False)

    airports_df = pd.DataFrame([
        {"code": k, "name": v["name"], "lat": v["lat"], "lon": v["lon"], "tier": v["tier"]}
        for k, v in AIRPORTS.items()
    ])
    airports_df.to_csv("/home/claude/airline-network-analysis/data/raw/airports.csv", index=False)

    print(f"Generated {len(df)} route-quarter records across {len(AIRPORTS)} airports.")
    print(df.head())


if __name__ == "__main__":
    main()
