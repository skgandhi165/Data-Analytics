# Airline Route Network Profitability & Optimization Analysis

An end-to-end analytics project that models a domestic airline's route
network as a graph, scores every route on profitability and network
value, and produces an EXPAND / MAINTAIN / MONITOR / CUT recommendation
per route — the kind of quarterly network-planning deliverable a real
airline analytics team produces.

## Why this project

Built as a portfolio piece for entry-level data/business analyst roles,
targeting the airline industry specifically. It's designed to demonstrate:
- **Python data pipelines** (cleaning, feature engineering)
- **SQL-equivalent aggregation logic** (route rollups, groupby)
- **Graph theory / network analysis** (`networkx` — most portfolio
  projects don't touch this, which is the differentiator)
- **Business framing** — every chart ties back to a decision
  ("which 5 routes should we add or cut next quarter")
- **Dashboarding** (interactive Plotly dashboard, Power BI-ready exports)

## Data

This project uses **synthetic data generated to match the schema and
economics of the real US DOT/BTS T-100 Domestic Segment dataset**
(the standard free public dataset for this kind of analysis). Live
internet access wasn't available in the environment this was built in,
so `scripts/01_generate_data.py` builds a realistic stand-in: a
25-airport, 5-hub network with hub-and-spoke structure, seasonal demand,
distance-based pricing, and the stage-length cost effect real airlines
see.

**To swap in real data:** download "T-100 Domestic Segment (All
Carriers)" from https://www.transtats.bts.gov/DL_SelectFields.asp?gnoyr_VQ=FMF
for your date range of choice, and point `scripts/02_data_pipeline.py`
at it (column names are documented in the docstring of script 01).

## Project structure

```
airline-network-analysis/
├── data/
│   ├── raw/                     # generated T-100-style route data
│   └── processed/               # cleaned, engineered, scored datasets
├── scripts/
│   ├── 01_generate_data.py      # synthetic BTS-style data generator
│   ├── 02_data_pipeline.py      # cleaning + metric engineering (yield, RASM, CASM, margin)
│   ├── 03_network_analysis.py   # networkx graph: centrality, resilience, new-route candidates
│   ├── 04_profitability_model.py# Route Health Score + EXPAND/MAINTAIN/MONITOR/CUT classification
│   ├── 05_visualizations.py     # interactive Plotly dashboard + charts
│   └── 06_static_charts_for_pdf.py # matplotlib PNGs for the write-up
├── outputs/
│   ├── charts/                  # PNG + interactive HTML charts
│   ├── dashboard/dashboard.html # single-page interactive dashboard (open in any browser)
│   └── exports/                 # Power BI-ready CSV exports
├── Project_Overview.pdf         # goal, background, key findings
├── Technical_Walkthrough.pdf    # step-by-step process explanation
└── README.md
```

## How to run it

```bash
pip install pandas numpy networkx plotly matplotlib
python scripts/01_generate_data.py
python scripts/02_data_pipeline.py
python scripts/03_network_analysis.py
python scripts/04_profitability_model.py
python scripts/05_visualizations.py
python scripts/06_static_charts_for_pdf.py
```

Then open `outputs/dashboard/dashboard.html` in any browser.

## Key outputs

- `data/processed/routes_scored.csv` — every route with its Route
  Health Score and recommendation
- `outputs/exports/route_action_list.csv` — the analyst-facing action
  list, ready to import into Power BI or Excel
- `data/processed/network_summary.json` — network-level stats
  (most influential airport, most fragile hub, top new-route candidate)
- `outputs/dashboard/dashboard.html` — interactive dashboard

## Putting this on your portfolio site

- Link `outputs/dashboard/dashboard.html` directly (works as a static
  file on GitHub Pages)
- Use the PNGs in `outputs/charts/` as the project card preview image
- Push `data/`, `scripts/`, and `outputs/` to
  `github.com/skgandhi165/Data-Analytics`
