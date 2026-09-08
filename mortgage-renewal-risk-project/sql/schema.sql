-- ============================================================
-- schema.sql
-- Canadian Mortgage Renewal Risk Project
-- ============================================================
-- Design notes (why it's built this way):
--   * rate_history is the FACT table: one row per BoC rate decision date.
--   * mortgage_scenario is a small DIMENSION/reference table you define
--     yourself: sample borrowers with different origination dates and
--     mortgage sizes, used to model "renewal shock."
--   * renewal_shock is a derived table (built by analysis.py) that joins
--     the two and stores the calculated payment impact per scenario.
-- ============================================================

DROP TABLE IF EXISTS renewal_shock;
DROP TABLE IF EXISTS mortgage_scenario;
DROP TABLE IF EXISTS rate_history;

-- Fact table: every BoC policy rate decision
CREATE TABLE rate_history (
    decision_date   TEXT PRIMARY KEY,   -- YYYY-MM-DD
    overnight_rate  REAL NOT NULL,      -- target overnight rate, %
    change_bps      INTEGER NOT NULL,   -- change from prior decision, basis points
    decision_type   TEXT NOT NULL       -- 'hike' | 'cut' | 'hold'
);

-- Reference table: sample mortgage scenarios (edit / extend as you like)
CREATE TABLE mortgage_scenario (
    scenario_id       INTEGER PRIMARY KEY,
    borrower_label    TEXT NOT NULL,     -- e.g. 'First-time buyer, Toronto'
    origination_date  TEXT NOT NULL,     -- when they signed their mortgage
    term_years        INTEGER NOT NULL,  -- typically 5 for Canadian fixed terms
    mortgage_amount   REAL NOT NULL,     -- original principal, CAD
    amortization_years INTEGER NOT NULL, -- typically 25 or 30
    original_rate     REAL NOT NULL      -- the fixed rate they locked in, %
);

-- Derived/output table: filled in by analysis.py
CREATE TABLE renewal_shock (
    scenario_id         INTEGER NOT NULL REFERENCES mortgage_scenario(scenario_id),
    renewal_date         TEXT NOT NULL,
    original_rate         REAL NOT NULL,
    estimated_renewal_rate REAL NOT NULL,
    rate_delta_bps         INTEGER NOT NULL,
    original_monthly_payment   REAL NOT NULL,
    renewal_monthly_payment    REAL NOT NULL,
    monthly_payment_increase   REAL NOT NULL,
    pct_payment_increase       REAL NOT NULL,
    PRIMARY KEY (scenario_id)
);

CREATE INDEX idx_rate_history_date ON rate_history(decision_date);
