-- =====================================================================
-- AESO Alberta Electricity Live Dashboard — SQL Setup & Example Queries
-- =====================================================================
-- This file assumes you've already run the notebook and exported
-- aeso_electricity_data.csv (or aeso_electricity_data.db).
--
-- Works as-is in SQLite. For SQL Server / PostgreSQL / MySQL, see the
-- "Portability notes" at the bottom — only a few syntax tweaks needed.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. TABLE SCHEMA
-- ---------------------------------------------------------------------
-- If you're loading the CSV into a database yourself (rather than using
-- the notebook's built-in SQLite export), create the table first:

CREATE TABLE IF NOT EXISTS electricity_prices (
    time_local        DATETIME,      -- Alberta local time (Mountain)
    time_utc          DATETIME,      -- UTC time
    pool_price         REAL,          -- $/MWh, actual pool price
    forecast_pool_price REAL,         -- $/MWh, AESO's short-term forecast
    rolling_30day_avg  REAL,          -- 30-day rolling average price
    data_source         TEXT,          -- 'LIVE' or 'SIMULATED'
    demand_mw           REAL,          -- Alberta Internal Load, in MW
    forecast_demand_mw  REAL,          -- forecast load, in MW
    rolling_mean_7d      REAL,          -- 7-day rolling mean price (from notebook)
    rolling_std_7d        REAL,          -- 7-day rolling std dev of price
    price_zscore          REAL,          -- how many std devs above the 7-day mean
    is_price_spike         INTEGER,       -- 1 = flagged spike, 0 = normal
    hour                    INTEGER        -- hour of day, 0-23
);

-- If using SQLite and the CSV directly:
-- .mode csv
-- .import aeso_electricity_data.csv electricity_prices  (then delete the duplicate header row)
-- (The notebook already writes this table for you via df.to_sql — this CREATE TABLE
--  is here mainly for reference and for loading into SQL Server/Postgres instead.)


-- ---------------------------------------------------------------------
-- 2. BASIC SANITY CHECKS
-- ---------------------------------------------------------------------

-- Row count and date range
SELECT
    COUNT(*)              AS total_rows,
    MIN(time_local)       AS earliest_hour,
    MAX(time_local)       AS latest_hour
FROM electricity_prices;

-- Any missing prices?
SELECT COUNT(*) AS missing_price_rows
FROM electricity_prices
WHERE pool_price IS NULL;


-- ---------------------------------------------------------------------
-- 3. DAILY SUMMARY (feeds a Power BI daily trend chart)
-- ---------------------------------------------------------------------

SELECT
    DATE(time_local)             AS day,
    ROUND(AVG(pool_price), 2)    AS avg_price,
    ROUND(MIN(pool_price), 2)    AS min_price,
    ROUND(MAX(pool_price), 2)    AS max_price,
    ROUND(AVG(demand_mw), 0)     AS avg_demand_mw,
    SUM(is_price_spike)          AS spike_hours
FROM electricity_prices
GROUP BY DATE(time_local)
ORDER BY day;


-- ---------------------------------------------------------------------
-- 4. AVERAGE PRICE BY HOUR OF DAY (shows daily demand/price pattern)
-- ---------------------------------------------------------------------

SELECT
    hour,
    ROUND(AVG(pool_price), 2) AS avg_price,
    ROUND(AVG(demand_mw), 0)  AS avg_demand_mw
FROM electricity_prices
GROUP BY hour
ORDER BY hour;


-- ---------------------------------------------------------------------
-- 5. TOP 20 MOST EXTREME PRICE-SPIKE HOURS
-- ---------------------------------------------------------------------

SELECT
    time_local,
    pool_price,
    rolling_mean_7d,
    price_zscore,
    demand_mw
FROM electricity_prices
WHERE is_price_spike = 1
ORDER BY price_zscore DESC
LIMIT 20;


-- ---------------------------------------------------------------------
-- 6. PRICE VS DEMAND CORRELATION CHECK (bucketed)
-- ---------------------------------------------------------------------
-- Buckets demand into 1000 MW ranges and shows average price per bucket —
-- a quick way to see whether price rises with demand, without needing a
-- statistics library.

SELECT
    CAST(demand_mw / 1000 AS INTEGER) * 1000 AS demand_bucket_mw,
    ROUND(AVG(pool_price), 2)                 AS avg_price,
    COUNT(*)                                  AS n_hours
FROM electricity_prices
GROUP BY demand_bucket_mw
ORDER BY demand_bucket_mw;


-- ---------------------------------------------------------------------
-- 7. WEEK-OVER-WEEK PRICE CHANGE (simple trend query)
-- ---------------------------------------------------------------------

WITH weekly AS (
    SELECT
        STRFTIME('%Y-%W', time_local) AS iso_week,
        AVG(pool_price)                AS avg_price
    FROM electricity_prices
    GROUP BY iso_week
)
SELECT
    iso_week,
    ROUND(avg_price, 2)                                        AS avg_price,
    ROUND(avg_price - LAG(avg_price) OVER (ORDER BY iso_week), 2) AS change_vs_prior_week
FROM weekly
ORDER BY iso_week;


-- =====================================================================
-- PORTABILITY NOTES
-- =====================================================================
-- SQLite  : everything above runs as-is (this is what the notebook exports to).
-- PostgreSQL:
--   - DATE(time_local)      -> already works
--   - STRFTIME('%Y-%W', x)  -> replace with TO_CHAR(x, 'IYYY-IW')
--   - CAST(x/1000 AS INTEGER) -> works, but use FLOOR(x/1000)::INT for clarity
-- SQL Server:
--   - DATE(time_local)      -> replace with CAST(time_local AS DATE)
--   - STRFTIME(...)         -> replace with DATEPART(ISO_WEEK, time_local)
--   - LIMIT 20               -> replace with TOP 20 in the SELECT clause
-- MySQL:
--   - STRFTIME(...)         -> replace with DATE_FORMAT(time_local, '%Y-%u')
-- =====================================================================
