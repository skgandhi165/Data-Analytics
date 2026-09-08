"""
FP&A analysis layer.

Uses the cleaned financial table plus management guidance assumptions.
Outputs KPI trends, scenario forecasts, and a concise management view.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data/processed"
DATA.mkdir(exist_ok=True)

def run(seed=True):
    src = ROOT/"data/raw/shopify_financials_seed.csv" if seed else DATA/"shopify_quarterly_model.csv"
    df = pd.read_csv(src)
    df["gross_margin"] = df.gross_profit_m/df.revenue_m
    df["opex_pct_revenue"] = df.opex_m/df.revenue_m
    df["operating_margin"] = df.operating_income_m/df.revenue_m
    df.to_csv(DATA/"kpi_trend.csv", index=False)
    print(df.sort_values("date").tail(8).to_string(index=False))

if __name__ == "__main__":
    run()
