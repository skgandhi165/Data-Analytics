"""
02_data_pipeline.py
--------------------
Cleans the raw route data and engineers the analyst-facing metrics:
- yield (revenue per passenger-mile)
- RASM (revenue per available seat mile) — the standard airline
  profitability metric
- CASM (cost per available seat mile) — already simulated upstream
- operating margin per route
- annualized (sum of 4 quarters) route-level rollup
"""

import pandas as pd

RAW_PATH = "/home/claude/airline-network-analysis/data/raw/t100_style_route_data.csv"
OUT_PATH = "/home/claude/airline-network-analysis/data/processed/routes_clean.csv"
OUT_ANNUAL = "/home/claude/airline-network-analysis/data/processed/routes_annual.csv"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.dropna()
    df = df[(df["passengers"] > 0) & (df["seats"] > 0) & (df["distance_miles"] > 0)]
    df = df[df["load_factor"] <= 1.0]
    after = len(df)
    print(f"Cleaning: dropped {before - after} invalid rows ({before} -> {after})")
    return df


def engineer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["asm"] = df["seats"] * df["distance_miles"]              # available seat miles
    df["rpm"] = df["passengers"] * df["distance_miles"]          # revenue passenger miles
    df["rasm_cents"] = (df["revenue"] / df["asm"]) * 100          # revenue per ASM, cents
    df["yield_cents_per_mile"] = (df["revenue"] / df["rpm"]) * 100
    df["operating_profit"] = df["revenue"] - df["op_cost"]
    df["operating_margin_pct"] = (df["operating_profit"] / df["revenue"]) * 100
    df["route"] = df["origin"] + "-" + df["dest"]
    return df


def build_annual_rollup(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby(["origin", "dest", "route", "origin_city", "dest_city",
                       "origin_tier", "dest_tier", "distance_miles"], as_index=False).agg(
        departures=("departures", "sum"),
        seats=("seats", "sum"),
        passengers=("passengers", "sum"),
        revenue=("revenue", "sum"),
        op_cost=("op_cost", "sum"),
        asm=("asm", "sum"),
        rpm=("rpm", "sum"),
    )
    agg["load_factor"] = agg["passengers"] / agg["seats"]
    agg["rasm_cents"] = (agg["revenue"] / agg["asm"]) * 100
    agg["yield_cents_per_mile"] = (agg["revenue"] / agg["rpm"]) * 100
    agg["operating_profit"] = agg["revenue"] - agg["op_cost"]
    agg["operating_margin_pct"] = (agg["operating_profit"] / agg["revenue"]) * 100
    # seasonality spread: how much passenger volume swings quarter to quarter
    seasonality = df.groupby(["origin", "dest"])["passengers"].agg(
        lambda x: (x.max() - x.min()) / x.mean()
    ).reset_index(name="seasonality_index")
    agg = agg.merge(seasonality, on=["origin", "dest"])
    return agg


def main():
    df = pd.read_csv(RAW_PATH)
    df = clean(df)
    df = engineer_metrics(df)
    df.to_csv(OUT_PATH, index=False)

    annual = build_annual_rollup(df)
    annual = annual.sort_values("operating_profit", ascending=False)
    annual.to_csv(OUT_ANNUAL, index=False)

    print(f"\nProcessed {len(df)} route-quarter records -> {OUT_PATH}")
    print(f"Rolled up into {len(annual)} annual routes -> {OUT_ANNUAL}")
    print("\nTop 5 most profitable routes (annual):")
    print(annual[["route", "operating_profit", "operating_margin_pct", "load_factor"]].head())
    print("\nBottom 5 least profitable routes (annual):")
    print(annual[["route", "operating_profit", "operating_margin_pct", "load_factor"]].tail())


if __name__ == "__main__":
    main()
