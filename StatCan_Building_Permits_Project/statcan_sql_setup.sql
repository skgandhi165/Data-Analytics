-- =====================================================================
-- StatCan Building Permits Live Tracker — SQL Setup & Example Queries
-- =====================================================================
-- Assumes you've run the notebook, which exports statcan_building_permits.db
-- with three tables: building_permits, national_trend, forecast.
--
-- Works as-is in SQLite. See "Portability notes" at the bottom for
-- SQL Server / PostgreSQL / MySQL equivalents.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. TABLE SCHEMAS (for reference / if loading the CSV elsewhere)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS building_permits (
    REF_DATE            DATE,     -- first day of the reporting month
    GEO                  TEXT,     -- region: Canada, Alberta, Ontario, British Columbia, Quebec
    "Type of structure"   TEXT,     -- Residential / Non-residential
    VALUE                 REAL      -- permit value, $ thousands (StatCan units)
);

CREATE TABLE IF NOT EXISTS national_trend (
    REF_DATE            DATE,
    VALUE                 REAL,     -- national total permit value that month
    yoy_change_pct         REAL,     -- % change vs. same month, prior year
    rolling_3mo_avg         REAL      -- 3-month rolling average
);

CREATE TABLE IF NOT EXISTS forecast (
    REF_DATE            DATE,     -- future month
    forecast_value         REAL      -- scikit-learn linear trend projection
);


-- ---------------------------------------------------------------------
-- 2. BASIC SANITY CHECKS
-- ---------------------------------------------------------------------

SELECT COUNT(*) AS total_rows, MIN(REF_DATE) AS earliest, MAX(REF_DATE) AS latest
FROM building_permits;

SELECT DISTINCT GEO FROM building_permits;


-- ---------------------------------------------------------------------
-- 3. NATIONAL TREND WITH YEAR-OVER-YEAR CONTEXT
-- ---------------------------------------------------------------------

SELECT
    REF_DATE,
    ROUND(VALUE, 0)             AS total_permit_value,
    ROUND(yoy_change_pct, 1)    AS yoy_change_pct,
    ROUND(rolling_3mo_avg, 0)   AS rolling_3mo_avg
FROM national_trend
ORDER BY REF_DATE DESC
LIMIT 12;


-- ---------------------------------------------------------------------
-- 4. REGIONAL RANKING — WHO'S GROWING, WHO'S SLOWING
-- ---------------------------------------------------------------------
-- Compares each region's most recent 3 months vs. the prior 3 months.

WITH monthly AS (
    SELECT GEO, REF_DATE, SUM(VALUE) AS total_value
    FROM building_permits
    WHERE GEO != 'Canada'
    GROUP BY GEO, REF_DATE
),
ranked AS (
    SELECT GEO, REF_DATE, total_value,
           ROW_NUMBER() OVER (PARTITION BY GEO ORDER BY REF_DATE DESC) AS rn
    FROM monthly
)
SELECT
    GEO,
    ROUND(AVG(CASE WHEN rn <= 3 THEN total_value END), 0)  AS avg_last_3mo,
    ROUND(AVG(CASE WHEN rn BETWEEN 4 AND 6 THEN total_value END), 0) AS avg_prior_3mo,
    ROUND(
        (AVG(CASE WHEN rn <= 3 THEN total_value END)
         - AVG(CASE WHEN rn BETWEEN 4 AND 6 THEN total_value END))
        / AVG(CASE WHEN rn BETWEEN 4 AND 6 THEN total_value END) * 100
    , 1) AS pct_change
FROM ranked
GROUP BY GEO
ORDER BY pct_change DESC;


-- ---------------------------------------------------------------------
-- 5. RESIDENTIAL VS. NON-RESIDENTIAL SPLIT, NATIONAL
-- ---------------------------------------------------------------------

SELECT
    REF_DATE,
    SUM(CASE WHEN "Type of structure" = 'Residential' THEN VALUE ELSE 0 END)     AS residential_value,
    SUM(CASE WHEN "Type of structure" = 'Non-residential' THEN VALUE ELSE 0 END) AS non_residential_value
FROM building_permits
WHERE GEO = 'Canada'
GROUP BY REF_DATE
ORDER BY REF_DATE;


-- ---------------------------------------------------------------------
-- 6. FORECAST VS. ACTUAL (once new live months come in)
-- ---------------------------------------------------------------------
-- Once you've re-run the notebook after the forecast window has passed,
-- this compares what was projected against what actually happened.

SELECT
    f.REF_DATE,
    f.forecast_value,
    n.VALUE AS actual_value,
    ROUND(n.VALUE - f.forecast_value, 0) AS forecast_error
FROM forecast f
LEFT JOIN national_trend n ON f.REF_DATE = n.REF_DATE
ORDER BY f.REF_DATE;


-- ---------------------------------------------------------------------
-- 7. SEASONAL PATTERN CHECK — AVERAGE BY CALENDAR MONTH
-- ---------------------------------------------------------------------

SELECT
    CAST(STRFTIME('%m', REF_DATE) AS INTEGER) AS calendar_month,
    ROUND(AVG(VALUE), 0) AS avg_permit_value
FROM national_trend
GROUP BY calendar_month
ORDER BY calendar_month;


-- =====================================================================
-- PORTABILITY NOTES
-- =====================================================================
-- PostgreSQL:
--   - STRFTIME('%m', x)  -> replace with EXTRACT(MONTH FROM x)
--   - Window functions (ROW_NUMBER) work identically
-- SQL Server:
--   - STRFTIME('%m', x)  -> replace with MONTH(x)
--   - LIMIT 12            -> replace with TOP 12 in the SELECT clause
-- MySQL:
--   - STRFTIME('%m', x)  -> replace with MONTH(x)
-- =====================================================================
