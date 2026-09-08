-- Shopify FP&A Analytics
-- Load data/processed/kpi_trend.csv into a table named shopify_financials.

-- 1. Core KPIs
SELECT
    period,
    date,
    revenue_m,
    gross_profit_m,
    opex_m,
    operating_income_m,
    ROUND(gross_profit_m / NULLIF(revenue_m,0) * 100, 2) AS gross_margin_pct,
    ROUND(opex_m / NULLIF(revenue_m,0) * 100, 2) AS opex_pct_revenue,
    ROUND(operating_income_m / NULLIF(revenue_m,0) * 100, 2) AS operating_margin_pct
FROM shopify_financials
ORDER BY date;

-- 2. Year-over-year comparison for Q2
SELECT
    a.period AS current_period,
    b.period AS prior_period,
    ROUND((a.revenue_m/b.revenue_m-1)*100,2) AS revenue_growth_pct,
    ROUND((a.gross_profit_m/b.gross_profit_m-1)*100,2) AS gross_profit_growth_pct,
    ROUND((a.opex_m/b.opex_m-1)*100,2) AS opex_growth_pct,
    ROUND((a.operating_income_m/b.operating_income_m-1)*100,2) AS operating_income_growth_pct
FROM shopify_financials a
JOIN shopify_financials b
  ON a.frequency='Q2'
 AND b.frequency='Q2'
 AND CAST(substr(a.date,1,4) AS INTEGER)=CAST(substr(b.date,1,4) AS INTEGER)+1;

-- 3. Margin bridge
SELECT
    period,
    ROUND(gross_margin*100,2) AS gross_margin_pct,
    ROUND(opex_pct_revenue*100,2) AS opex_pct_revenue,
    ROUND(operating_margin*100,2) AS operating_margin_pct
FROM shopify_financials
WHERE frequency='Q2'
ORDER BY date;
