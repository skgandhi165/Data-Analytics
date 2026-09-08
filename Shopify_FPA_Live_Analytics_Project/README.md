# Shopify FP&A & Financial Performance Analytics

## Purpose
A portfolio-ready FP&A project designed to demonstrate:
- financial statement analysis
- KPI and margin analysis
- variance thinking
- forecasting and scenario planning
- Python + SQL + Power BI
- live/refreshable data ingestion

## Company
Shopify Inc. (SHOP). The initial seed dataset is based on Shopify's published financial results and SEC filings. The live refresh layer is designed to pull new SEC facts and daily market data when you run it.

## What the project answers
1. Is revenue growth translating into profit growth?
2. Are operating expenses scaling faster or slower than revenue?
3. What is happening to gross margin and operating margin?
4. Which assumptions matter most for the next quarter?
5. What would management need to watch if growth slows or costs rise?

## Current snapshot
Q2 2026 revenue was US$3.583B, gross profit US$1.708B, operating expenses US$1.220B and operating income US$488M. Shopify reported 34% revenue growth and 18% free-cash-flow margin for Q2 2026.

## Refresh
1. Install dependencies:
   `pip install -r requirements.txt`
2. Run:
   `python src/fetch_data.py`
3. Transform:
   `python src/transform.py`
4. Run analysis:
   `python src/analyze.py`
5. Load the resulting CSVs into Power BI.

Financial statements update when new filings/results are published; daily market data can refresh each run.

## Important modelling note
Public-company filings are quarterly/annual. Do not fabricate monthly actuals from quarterly totals. If monthly FP&A data is needed, use a clearly labelled synthetic budget/actual layer or a company dataset that genuinely reports monthly observations.

## Files
- `src/` — live ingestion + transformation + analysis
- `sql/` — SQL analysis
- `powerbi/` — dashboard structure and DAX
- `data/` — seed/live/processed datasets
- `notebooks/` — reproducible Python analysis
- `reports/` — two learning PDFs
- `charts/` — analysis visuals

## Resume angle
**Built an FP&A analytics model using Python, SQL and Power BI to analyze revenue growth, gross-margin trends, operating leverage and scenario-based forecasts using live/refreshable public-company financial data.**
