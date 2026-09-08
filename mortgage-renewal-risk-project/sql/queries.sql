-- ============================================================
-- queries.sql
-- Analyst-style SQL queries against mortgage_risk.db
-- Run with: sqlite3 db/mortgage_risk.db < sql/queries.sql
-- ============================================================

-- 1. Full rate history, most recent first
SELECT decision_date, overnight_rate, change_bps, decision_type
FROM rate_history
ORDER BY decision_date DESC
LIMIT 10;

-- 2. Every rate HIKE or CUT (ignore holds) -- shows the actual cycle turns
SELECT decision_date, overnight_rate, change_bps, decision_type
FROM rate_history
WHERE decision_type != 'hold'
ORDER BY decision_date;

-- 3. Rolling 12-month-equivalent average rate using a window function
--    (average of each decision and the 5 decisions before it)
SELECT
    decision_date,
    overnight_rate,
    ROUND(AVG(overnight_rate) OVER (
        ORDER BY decision_date
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ), 3) AS rolling_avg_rate
FROM rate_history
ORDER BY decision_date;

-- 4. Rate change velocity: total basis points moved within each rolling
--    12-month window -- highlights how fast a cycle is moving, not just
--    the level of rates
SELECT
    decision_date,
    change_bps,
    SUM(change_bps) OVER (
        ORDER BY decision_date
        RANGE BETWEEN 365 PRECEDING AND CURRENT ROW
    ) AS bps_moved_last_12mo
FROM rate_history
ORDER BY decision_date;

-- 5. Peak and trough of each rate cycle (useful for the write-up)
WITH ranked AS (
    SELECT
        decision_date,
        overnight_rate,
        LAG(decision_type) OVER (ORDER BY decision_date) AS prev_type,
        decision_type
    FROM rate_history
)
SELECT decision_date, overnight_rate, decision_type
FROM ranked
WHERE decision_type != 'hold'
  AND (prev_type IS NULL OR prev_type != decision_type)
ORDER BY decision_date;

-- 6. Days between consecutive rate decisions (pace of Governing Council action)
SELECT
    decision_date,
    julianday(decision_date) - julianday(LAG(decision_date) OVER (ORDER BY decision_date)) AS days_since_last_decision
FROM rate_history
ORDER BY decision_date DESC
LIMIT 15;

-- 7. Mortgage renewal shock summary, once analysis.py has populated
--    the renewal_shock table
SELECT
    m.borrower_label,
    m.origination_date,
    r.original_rate,
    r.estimated_renewal_rate,
    r.rate_delta_bps,
    ROUND(r.monthly_payment_increase, 2) AS monthly_increase_cad,
    ROUND(r.pct_payment_increase, 1) AS pct_increase
FROM renewal_shock r
JOIN mortgage_scenario m ON m.scenario_id = r.scenario_id
ORDER BY r.pct_payment_increase DESC;

-- 8. Which scenarios face the worst renewal shock, ranked with a window function
SELECT
    m.borrower_label,
    ROUND(r.pct_payment_increase, 1) AS pct_increase,
    RANK() OVER (ORDER BY r.pct_payment_increase DESC) AS risk_rank
FROM renewal_shock r
JOIN mortgage_scenario m ON m.scenario_id = r.scenario_id;
