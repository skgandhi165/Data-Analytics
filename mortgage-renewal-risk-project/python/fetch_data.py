"""
fetch_data.py
--------------
Pulls LIVE data from the Bank of Canada Valet API (no key required) and
saves it as clean CSVs in the /data folder.

Run this yourself, locally, whenever you want fresh data:
    python fetch_data.py

Series used:
  V39079              -> Target for the overnight rate (the BoC policy rate)
  BD.CDN.5YR.DQ.YLD    -> Government of Canada 5-year benchmark bond yield
                          (this is what 5-year FIXED mortgage rates are priced off)

Docs: https://www.bankofcanada.ca/valet/docs
"""

import csv
import json
import urllib.request
import urllib.error
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.bankofcanada.ca/valet/observations/{series}/json?start_date={start}"

SERIES = {
    "V39079": "overnight_rate.csv",              # policy rate
    "BD.CDN.5YR.DQ.YLD": "bond_yield_5yr.csv",    # 5yr GoC bond yield
}

START_DATE = "2015-01-01"


def fetch_series(series_code: str, start_date: str = START_DATE) -> list[dict]:
    """Fetch one series from the Valet API and return a list of {date, value} dicts."""
    url = BASE_URL.format(series=series_code, start=start_date)
    print(f"Fetching {series_code} from {url} ...")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"  !! Could not reach Bank of Canada Valet API: {e}")
        print("  !! Check your internet connection / firewall and try again.")
        return []

    observations = payload.get("observations", [])
    rows = []
    for obs in observations:
        date = obs.get("d")
        value_block = obs.get(series_code, {})
        value = value_block.get("v")
        if date and value is not None:
            rows.append({"date": date, "value": float(value)})
    print(f"  -> got {len(rows)} observations")
    return rows


def save_csv(rows: list[dict], filename: str) -> None:
    out_path = DATA_DIR / filename
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "value"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> saved to {out_path}")


def main():
    for series_code, filename in SERIES.items():
        rows = fetch_series(series_code)
        if rows:
            save_csv(rows, filename)
        else:
            print(f"  Skipping save for {series_code} (no data returned).")

    print("\nDone. If the fetch failed (e.g. no internet access in this environment),")
    print("the project still works using the pre-loaded seed data in data/boc_rate_history_seed.csv")


if __name__ == "__main__":
    main()
