"""
Live FP&A data refresh for Shopify (SHOP).

Sources:
1) SEC Company Facts API: quarterly/annual GAAP facts. No API key required.
2) Yahoo Finance chart endpoint: daily market data.

Run:
    python src/fetch_data.py

The script writes:
    data/raw/shopify_financials_live.csv
    data/raw/shopify_market_live.csv

Financial statement data updates when Shopify files new results; market data can update daily.
"""
import json, requests, pandas as pd
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Srushti Gandhi FP&A portfolio project contact email@example.com"}

def sec_get():
    url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0001594805.json"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def facts_frame(data):
    facts = data["facts"]["us-gaap"]
    candidates = {
        "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "gross_profit": ["GrossProfit"],
        "operating_income": ["OperatingIncomeLoss"],
        "opex": ["OperatingExpenses"],
        "fcf": [], "gmv": [], "mrr": []
    }
    out = []
    for metric, tags in candidates.items():
        for tag in tags:
            if tag in facts:
                units = facts[tag]["units"]
                unit = "USD"
                if unit not in units:
                    unit = next(iter(units))
                for x in units[unit]:
                    if x.get("form") in ("10-Q","10-K") and x.get("fp") in ("Q1","Q2","Q3","FY"):
                        out.append({
                            "metric": metric,
                            "tag": tag,
                            "value": x.get("val"),
                            "start": x.get("start"),
                            "end": x.get("end"),
                            "form": x.get("form"),
                            "fp": x.get("fp"),
                            "filed": x.get("filed"),
                            "frame": x.get("frame"),
                            "unit": unit
                        })
                break
    return pd.DataFrame(out)

def fetch_market():
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/SHOP"
           "?period1=1735689600&period2=now&interval=1d&events=history")
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    j = r.json()["chart"]["result"][0]
    ts = pd.to_datetime(j["timestamp"], unit="s", utc=True).date
    q = j["indicators"]["quote"][0]
    return pd.DataFrame({
        "date": ts,
        "open": q["open"],
        "high": q["high"],
        "low": q["low"],
        "close": q["close"],
        "volume": q["volume"]
    }).dropna(subset=["close"])

if __name__ == "__main__":
    sec = sec_get()
    ff = facts_frame(sec)
    ff.to_csv(RAW/"shopify_financials_live.csv", index=False)
    mk = fetch_market()
    mk.to_csv(RAW/"shopify_market_live.csv", index=False)
    print("Refresh complete:", datetime.now(timezone.utc).isoformat())
