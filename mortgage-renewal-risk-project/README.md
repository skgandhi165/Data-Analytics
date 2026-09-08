# Canadian Mortgage Renewal Risk Project

A small end-to-end data project (Python + SQL + Python) that models how
Bank of Canada rate cycles affect Canadian mortgage holders at renewal —
built as a portfolio piece for entry-level analyst roles at Canadian banks.

## What it does

1. **Extracts** Bank of Canada policy rate data (live, via the free Valet API).
2. **Loads** it into a SQLite database with a proper schema (fact table +
   reference table + derived output table).
3. **Analyzes** it with SQL (window functions, rolling averages, rate-cycle
   detection) and Python (mortgage payment math).
4. **Models** "renewal shock" — the monthly payment increase/decrease a
   borrower faces when their 5-year fixed mortgage comes up for renewal,
   depending on when they originally signed.
5. **Visualizes** the results as charts.

## Folder structure

```
mortgage-renewal-risk-project/
├── README.md                      <- you are here
├── data/
│   ├── boc_rate_history_seed.csv  <- real BoC rate decisions, 2020-2026 (pre-loaded)
│   ├── overnight_rate.csv         <- created when you run fetch_data.py (live data)
│   └── bond_yield_5yr.csv         <- created when you run fetch_data.py (live data)
├── sql/
│   ├── schema.sql                 <- database schema (3 tables)
│   └── queries.sql                <- 8 analyst-style SQL queries
├── python/
│   ├── fetch_data.py              <- pulls LIVE data from the BoC Valet API
│   ├── load_to_db.py              <- builds the SQLite database
│   └── analysis.py                <- computes renewal shock + makes charts
├── db/
│   └── mortgage_risk.db           <- SQLite database (created when you run load_to_db.py)
├── charts/
│   ├── rate_history.png
│   └── renewal_shock.png
└── reports/
    ├── Project_Overview.pdf       <- the "why" -- goal, discovery, findings
    └── Step_by_Step_Guide.pdf     <- the "how" -- walk yourself through it
```

## How to run it yourself

```bash
cd mortgage-renewal-risk-project

# 1. (Optional) refresh with live data from the Bank of Canada
python python/fetch_data.py

# 2. Build the database
python python/load_to_db.py

# 3. Run the analysis and generate charts
python python/analysis.py

# 4. Explore the SQL yourself
sqlite3 db/mortgage_risk.db
sqlite3 db/mortgage_risk.db < sql/queries.sql
```

Requires: `python3`, `pandas`-free standard library for fetch/load, and
`matplotlib` for the charts (`pip install matplotlib`).

The project works **out of the box** even with no internet connection,
because `data/boc_rate_history_seed.csv` already contains real,
verified Bank of Canada rate decisions from 2020–2026. Running
`fetch_data.py` simply refreshes that data live.

## Key finding (see Project_Overview.pdf for the full story)

Whether a mortgage renewal is painful or a relief right now depends almost
entirely on *when* the borrower originally signed — not on some universal
"rates are high" narrative. Borrowers who locked in during 2020–2021 (when
rates bottomed at 0.25%) face the sharpest payment increases today, while
borrowers who locked in near the 2023 peak (5.00%) are actually renewing
into relief as rates have since fallen to 2.25%.

## Editing the assumptions

- `python/analysis.py` → `ASSUMED_TODAY_FIXED_RATE` — update this to
  whatever the current 5-year fixed mortgage rate is when you re-run it.
- `python/load_to_db.py` → `load_sample_scenarios()` — swap in your own
  borrower scenarios (amounts, dates, rates).
