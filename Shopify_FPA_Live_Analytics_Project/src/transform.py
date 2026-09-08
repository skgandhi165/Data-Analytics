"""
Transform SEC facts into an FP&A-friendly table.
This script is intentionally conservative: it preserves source facts and
does not invent monthly data from quarterly statements.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/"data/raw"
OUT = ROOT/"data/processed"
OUT.mkdir(exist_ok=True)

def latest_fact(df, metric, fp):
    x = df[(df.metric==metric) & (df.fp==fp)].copy()
    if x.empty:
        return None
    x["end"] = pd.to_datetime(x["end"])
    # Prefer the latest filed fact for each period end.
    x = x.sort_values(["end","filed"]).drop_duplicates(["end"], keep="last")
    return x.iloc[-1]

def build():
    p = RAW/"shopify_financials_live.csv"
    if not p.exists():
        raise FileNotFoundError("Run src/fetch_data.py first.")
    df = pd.read_csv(p)
    df["value_m"] = df["value"]/1e6
    # For duration facts, SEC may report year-to-date values for Q2/Q3.
    # A production analyst should derive discrete quarters from YTD filings
    # using the prior quarter's cumulative value.
    df.to_csv(OUT/"shopify_financials_long.csv", index=False)
    print("Wrote long-format financial facts.")

if __name__ == "__main__":
    build()
