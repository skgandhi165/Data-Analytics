"""
03_network_analysis.py
-----------------------
Models the airline's route map as a directed, weighted graph and applies
graph theory to answer network-design questions a real network planning
analyst asks:

- Which airports function as true hubs (highest centrality)?
- How resilient is the network if a hub is disrupted (weather, ATC)?
- Which city-pairs are structurally "bridge" routes (few alternate paths)?
- Which underserved spoke-spoke pairs might justify a new direct route?
"""

import json

import networkx as nx
import pandas as pd

ANNUAL_PATH = "/home/claude/airline-network-analysis/data/processed/routes_annual.csv"
AIRPORTS_PATH = "/home/claude/airline-network-analysis/data/raw/airports.csv"
OUT_CENTRALITY = "/home/claude/airline-network-analysis/data/processed/airport_centrality.csv"
OUT_SUMMARY = "/home/claude/airline-network-analysis/data/processed/network_summary.json"
OUT_NEW_ROUTE_CANDIDATES = "/home/claude/airline-network-analysis/data/processed/new_route_candidates.csv"


def build_graph(routes: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()
    for _, r in routes.iterrows():
        G.add_edge(
            r["origin"], r["dest"],
            weight=r["passengers"],
            revenue=r["revenue"],
            distance=r["distance_miles"],
        )
    return G


def centrality_analysis(G: nx.DiGraph, airports: pd.DataFrame) -> pd.DataFrame:
    degree = dict(G.degree(weight="weight"))
    betweenness = nx.betweenness_centrality(G, weight="distance", normalized=True)
    # eigenvector centrality on the undirected, passenger-weighted version = "influence" in the network
    Gu = G.to_undirected()
    eigen = nx.eigenvector_centrality_numpy(Gu, weight="weight")

    rows = []
    for code in G.nodes():
        meta = airports[airports["code"] == code].iloc[0]
        rows.append({
            "code": code, "name": meta["name"], "tier": meta["tier"],
            "weighted_degree": degree.get(code, 0),
            "betweenness_centrality": round(betweenness.get(code, 0), 4),
            "eigenvector_centrality": round(eigen.get(code, 0), 4),
            "num_routes": G.degree(code),
        })
    df = pd.DataFrame(rows).sort_values("eigenvector_centrality", ascending=False)
    return df


def network_resilience(G: nx.DiGraph, hub_codes: list) -> dict:
    """Simulates removing each hub and measures the % of spoke-pairs that
    lose direct or 1-stop connectivity - a proxy for network fragility."""
    Gu = G.to_undirected()
    base_pairs = sum(1 for _ in nx.all_pairs_shortest_path_length(Gu))
    results = {}
    for hub in hub_codes:
        H = Gu.copy()
        H.remove_node(hub)
        if H.number_of_nodes() == 0:
            continue
        largest_cc = max(nx.connected_components(H), key=len)
        pct_still_connected = len(largest_cc) / Gu.number_of_nodes() * 100
        results[hub] = round(pct_still_connected, 1)
    return results


def find_new_route_candidates(routes: pd.DataFrame, G: nx.DiGraph, airports: pd.DataFrame, top_n=10) -> pd.DataFrame:
    """Finds spoke-spoke city pairs with NO direct route today, estimates
    combined connecting-passenger demand through shared hubs, and flags
    the pairs with the strongest case for a new nonstop route."""
    spokes = airports[airports["tier"] == "spoke"]["code"].tolist()
    existing_routes = set(zip(routes["origin"], routes["dest"]))

    candidates = []
    for i, a in enumerate(spokes):
        for b in spokes[i + 1:]:
            if (a, b) in existing_routes or (b, a) in existing_routes:
                continue
            # estimate implied connecting demand: passengers flowing a->hub->b via shared hubs
            implied = 0
            for hub in G.nodes():
                if G.has_edge(a, hub) and G.has_edge(hub, b):
                    implied += min(G[a][hub]["weight"], G[hub][b]["weight"]) * 0.35  # connect rate assumption
            if implied > 0:
                a_meta = airports[airports["code"] == a].iloc[0]
                b_meta = airports[airports["code"] == b].iloc[0]
                candidates.append({
                    "origin": a, "dest": b,
                    "origin_city": a_meta["name"], "dest_city": b_meta["name"],
                    "estimated_annual_connecting_demand": round(implied),
                })
    df = pd.DataFrame(candidates).sort_values("estimated_annual_connecting_demand", ascending=False)
    return df.head(top_n)


def main():
    routes = pd.read_csv(ANNUAL_PATH)
    airports = pd.read_csv(AIRPORTS_PATH)
    hub_codes = airports[airports["tier"] == "hub"]["code"].tolist()

    G = build_graph(routes)
    print(f"Graph built: {G.number_of_nodes()} airports, {G.number_of_edges()} directed route segments")

    cent = centrality_analysis(G, airports)
    cent.to_csv(OUT_CENTRALITY, index=False)
    print("\nTop 5 airports by network influence (eigenvector centrality):")
    print(cent[["code", "name", "tier", "eigenvector_centrality", "num_routes"]].head())

    resilience = network_resilience(G, hub_codes)
    print("\nNetwork resilience - % of network still connected if each hub is removed:")
    for hub, pct in sorted(resilience.items(), key=lambda x: x[1]):
        print(f"  Remove {hub}: {pct}% of airports remain connected")

    candidates = find_new_route_candidates(routes, G, airports, top_n=10)
    candidates.to_csv(OUT_NEW_ROUTE_CANDIDATES, index=False)
    print("\nTop new nonstop route candidates (no direct route today, high implied connecting demand):")
    print(candidates.to_string(index=False))

    summary = {
        "num_airports": G.number_of_nodes(),
        "num_route_segments": G.number_of_edges(),
        "hub_codes": hub_codes,
        "most_central_airport": cent.iloc[0]["code"],
        "network_resilience_by_hub_removed_pct": resilience,
        "most_fragile_hub": min(resilience, key=resilience.get),
        "top_new_route_candidate": f"{candidates.iloc[0]['origin']}-{candidates.iloc[0]['dest']}",
    }
    with open(OUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved network summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
