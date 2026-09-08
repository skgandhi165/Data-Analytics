"""
04_profitability_model.py
--------------------------
Combines route economics (margin, load factor, yield) with network
position (centrality) into a single "Route Health Score" and produces
a ranked action list: EXPAND / MAINTAIN / MONITOR / CUT.

This mirrors how a real network-planning team screens their portfolio
each quarter - it's not just "which routes make the most money," it's
"which routes make money AND are efficient AND are getting worse or
better," which is what determines the actual add/cut decision.
"""

import pandas as pd

ANNUAL_PATH = "/home/claude/airline-network-analysis/data/processed/routes_annual.csv"
CLEAN_PATH = "/home/claude/airline-network-analysis/data/processed/routes_clean.csv"
CENTRALITY_PATH = "/home/claude/airline-network-analysis/data/processed/airport_centrality.csv"
OUT_SCORED = "/home/claude/airline-network-analysis/data/processed/routes_scored.csv"
OUT_ACTIONS = "/home/claude/airline-network-analysis/outputs/exports/route_action_list.csv"


def minmax(s: pd.Series) -> pd.Series:
    return (s - s.min()) / (s.max() - s.min())


def compute_trend(clean: pd.DataFrame) -> pd.DataFrame:
    """Q1 -> Q4 passenger growth rate per route, as a simple trend signal."""
    q1 = clean[clean["quarter"] == 1].set_index(["origin", "dest"])["passengers"]
    q4 = clean[clean["quarter"] == 4].set_index(["origin", "dest"])["passengers"]
    trend = ((q4 - q1) / q1 * 100).rename("q1_to_q4_growth_pct").reset_index()
    return trend


def score_routes(annual: pd.DataFrame, trend: pd.DataFrame, centrality: pd.DataFrame) -> pd.DataFrame:
    df = annual.merge(trend, on=["origin", "dest"], how="left")

    # bring in destination-side centrality as a proxy for strategic network value
    cent_map = centrality.set_index("code")["eigenvector_centrality"].to_dict()
    df["network_value"] = df["dest"].map(cent_map).fillna(0) + df["origin"].map(cent_map).fillna(0)

    df["score_margin"] = minmax(df["operating_margin_pct"])
    df["score_load_factor"] = minmax(df["load_factor"])
    df["score_growth"] = minmax(df["q1_to_q4_growth_pct"].fillna(0))
    df["score_network_value"] = minmax(df["network_value"])

    # weighted composite: profitability matters most, then efficiency, then growth/strategic fit
    df["route_health_score"] = (
        df["score_margin"] * 0.40
        + df["score_load_factor"] * 0.25
        + df["score_growth"] * 0.20
        + df["score_network_value"] * 0.15
    ) * 100

    # Classify by quantile within the portfolio rather than a fixed cutoff -
    # this is how network planning teams actually screen a route portfolio each
    # quarter: relative to the rest of the network, not against an arbitrary bar.
    q80, q50, q20 = df["route_health_score"].quantile([0.80, 0.50, 0.20])

    def classify(score):
        if score >= q80:
            return "EXPAND"
        elif score >= q50:
            return "MAINTAIN"
        elif score >= q20:
            return "MONITOR"
        else:
            return "CUT / RESTRUCTURE"

    df["recommendation"] = df["route_health_score"].apply(classify)
    return df.sort_values("route_health_score", ascending=False)


def main():
    annual = pd.read_csv(ANNUAL_PATH)
    clean = pd.read_csv(CLEAN_PATH)
    centrality = pd.read_csv(CENTRALITY_PATH)

    trend = compute_trend(clean)
    scored = score_routes(annual, trend, centrality)
    scored.to_csv(OUT_SCORED, index=False)

    action_cols = ["route", "origin_city", "dest_city", "operating_profit",
                   "operating_margin_pct", "load_factor", "q1_to_q4_growth_pct",
                   "route_health_score", "recommendation"]
    scored[action_cols].to_csv(OUT_ACTIONS, index=False)

    print("Route Health Score distribution:")
    print(scored["recommendation"].value_counts())

    print("\nTop 5 EXPAND candidates:")
    print(scored[scored["recommendation"] == "EXPAND"][action_cols].head().to_string(index=False))

    print("\nTop 5 CUT / RESTRUCTURE candidates:")
    print(scored[scored["recommendation"] == "CUT / RESTRUCTURE"][action_cols].head().to_string(index=False))

    print(f"\nSaved full scored table -> {OUT_SCORED}")
    print(f"Saved action list -> {OUT_ACTIONS}")


if __name__ == "__main__":
    main()
