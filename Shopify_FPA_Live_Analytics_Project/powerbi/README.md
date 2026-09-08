# Power BI build guide

## Data
Load:
- `data/processed/kpi_trend.csv`
- `data/processed/q3_2026_scenarios.csv`
- `data/raw/shopify_market_seed.csv` (or the live market file after refresh)

## Suggested pages

### 1. Executive FP&A
Cards:
- Revenue
- Gross Profit
- Gross Margin
- Operating Expenses
- Operating Margin
- YoY Revenue Growth

Visuals:
- Revenue vs Gross Profit trend
- Margin trend
- Latest quarter KPI table

### 2. Forecast & Scenario
Show Conservative / Base / Upside:
- Revenue
- Gross Profit
- Operating Expenses
- Operating Income
- Operating Margin

### 3. Market Context
Use daily SHOP price only as context, not as a substitute for operating performance.

## DAX measures

Revenue = SUM(kpi_trend[revenue_m])

Gross Profit = SUM(kpi_trend[gross_profit_m])

Operating Expenses = SUM(kpi_trend[opex_m])

Operating Income = SUM(kpi_trend[operating_income_m])

Gross Margin % = DIVIDE([Gross Profit],[Revenue])

OpEx % Revenue = DIVIDE([Operating Expenses],[Revenue])

Operating Margin % = DIVIDE([Operating Income],[Revenue])

Revenue YoY % =
VAR CurrentRevenue = [Revenue]
VAR PriorRevenue =
    CALCULATE([Revenue], DATEADD(kpi_trend[date], -1, YEAR))
RETURN DIVIDE(CurrentRevenue-PriorRevenue, PriorRevenue)
