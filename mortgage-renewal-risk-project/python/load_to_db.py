"""
load_to_db.py
--------------
Builds the SQLite database for the project:
  1. Runs sql/schema.sql to (re)create the tables.
  2. Loads Bank of Canada rate history into rate_history
     (uses live data/overnight_rate.csv if it exists from fetch_data.py,
      otherwise falls back to the bundled seed CSV so the project always runs).
  3. Inserts a handful of sample mortgage_scenario rows to analyze.

Run:
    python load_to_db.py
"""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SQL_DIR = ROOT / "sql"
DB_DIR = ROOT / "db"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "mortgage_risk.db"

SEED_CSV = DATA_DIR / "boc_rate_history_seed.csv"
LIVE_CSV = DATA_DIR / "overnight_rate.csv"  # produced by fetch_data.py, has date,value only


def build_schema(conn: sqlite3.Connection) -> None:
    schema_sql = (SQL_DIR / "schema.sql").read_text()
    conn.executescript(schema_sql)
    print("Schema created.")


def load_rate_history(conn: sqlite3.Connection) -> None:
    if SEED_CSV.exists():
        # Seed CSV already has decision_type / change_bps computed -> richest option
        with open(SEED_CSV, newline="") as f:
            reader = csv.DictReader(f)
            rows = [
                (r["decision_date"], float(r["overnight_rate"]), int(r["change_bps"]), r["decision_type"])
                for r in reader
            ]
        conn.executemany(
            "INSERT OR REPLACE INTO rate_history (decision_date, overnight_rate, change_bps, decision_type) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )
        print(f"Loaded {len(rows)} rows into rate_history from seed CSV.")
    elif LIVE_CSV.exists():
        # Live CSV is just date,value (daily observations) -> derive change_bps/decision_type
        with open(LIVE_CSV, newline="") as f:
            reader = csv.DictReader(f)
            observations = [(r["date"], float(r["value"])) for r in reader]
        rows = []
        prev_rate = None
        for date, rate in observations:
            change_bps = 0 if prev_rate is None else round((rate - prev_rate) * 100)
            decision_type = "hold" if change_bps == 0 else ("hike" if change_bps > 0 else "cut")
            rows.append((date, rate, change_bps, decision_type))
            prev_rate = rate
        conn.executemany(
            "INSERT OR REPLACE INTO rate_history (decision_date, overnight_rate, change_bps, decision_type) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )
        print(f"Loaded {len(rows)} rows into rate_history from live Valet API CSV.")
    else:
        raise FileNotFoundError(
            "No rate data found. Run fetch_data.py first, or make sure "
            "data/boc_rate_history_seed.csv is present."
        )


def load_sample_scenarios(conn: sqlite3.Connection) -> None:
    """
    Sample borrowers who locked in a 5-year FIXED mortgage at different points
    in the rate cycle. Edit this list freely -- these are illustrative, not real people.
    """
    scenarios = [
        (1, "First-time buyer, signed near pandemic lows", "2020-08-01", 5, 450000, 25, 1.79),
        (2, "Move-up buyer, signed as rates started climbing", "2021-11-01", 5, 620000, 25, 2.34),
        (3, "Refinance, signed right before peak hikes", "2022-02-01", 5, 500000, 25, 3.09),
        (4, "Buyer who locked in near the cycle peak", "2023-06-01", 5, 550000, 25, 5.34),
        (5, "Recent buyer, signed during the cutting cycle", "2024-11-01", 5, 480000, 25, 4.44),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO mortgage_scenario "
        "(scenario_id, borrower_label, origination_date, term_years, mortgage_amount, "
        " amortization_years, original_rate) VALUES (?, ?, ?, ?, ?, ?, ?)",
        scenarios,
    )
    print(f"Loaded {len(scenarios)} sample mortgage scenarios.")


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        build_schema(conn)
        load_rate_history(conn)
        load_sample_scenarios(conn)
        conn.commit()
        print(f"\nDatabase ready at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
