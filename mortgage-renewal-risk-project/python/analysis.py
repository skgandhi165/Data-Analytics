"""
analysis.py
-----------
The core analytical logic of the project:

  1. Reads rate_history + mortgage_scenario from the database.
  2. For each sample borrower, estimates their mortgage renewal rate today
     using the current spread between their original rate and the BoC's
     current rate/bond-yield environment.
  3. Computes the actual monthly payment impact (the "renewal shock")
     using the standard Canadian mortgage payment formula.
  4. Writes results into renewal_shock table.
  5. Produces two charts:
       - charts/rate_history.png     (BoC rate over time)
       - charts/renewal_shock.png    (payment increase by scenario)

Run:
    python analysis.py
(run load_to_db.py first)
"""

import sqlite3
from pathlib import Path
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mortgage_risk.db"
CHARTS_DIR = ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# Approximate spread that 5-year FIXED mortgage rates trade above the
# 5yr GoC bond yield / BoC overnight rate environment in Canada.
# This is a simplifying assumption for the project -- real bank pricing
# also reflects lender risk premium, term, and borrower credit profile.
ASSUMED_TODAY_FIXED_RATE = 4.29  # illustrative current 5yr fixed rate, %, edit as needed


def monthly_payment(principal: float, annual_rate_pct: float, amortization_years: int) -> float:
    """Standard Canadian mortgage payment calc (semi-annual compounding, monthly payments)."""
    if annual_rate_pct == 0:
        return principal / (amortization_years * 12)
    # Canadian mortgages compound semi-annually by law/convention
    i_semi = annual_rate_pct / 100 / 2
    i_monthly_equiv = (1 + i_semi) ** (2 / 12) - 1
    n = amortization_years * 12
    payment = principal * (i_monthly_equiv * (1 + i_monthly_equiv) ** n) / ((1 + i_monthly_equiv) ** n - 1)
    return payment


def compute_renewal_shock(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        "SELECT scenario_id, borrower_label, origination_date, term_years, "
        "mortgage_amount, amortization_years, original_rate FROM mortgage_scenario"
    )
    scenarios = cur.fetchall()

    results = []
    for (scenario_id, label, origination_date, term_years, amount,
         amortization_years, original_rate) in scenarios:
        orig_date = date.fromisoformat(origination_date)
        renewal_date = date(orig_date.year + term_years, orig_date.month, orig_date.day)

        estimated_renewal_rate = ASSUMED_TODAY_FIXED_RATE
        rate_delta_bps = round((estimated_renewal_rate - original_rate) * 100)

        orig_payment = monthly_payment(amount, original_rate, amortization_years)

        # Remaining amortization at renewal (years already paid down)
        years_elapsed = term_years
        remaining_amort = max(amortization_years - years_elapsed, 5)
        # Rough remaining balance estimate: assume linear paydown of principal
        # (simplification -- good enough for an illustrative project)
        pct_principal_remaining = remaining_amort / amortization_years
        remaining_balance = amount * pct_principal_remaining

        renewal_payment = monthly_payment(remaining_balance, estimated_renewal_rate, remaining_amort)

        increase = renewal_payment - orig_payment
        pct_increase = (increase / orig_payment) * 100

        results.append((
            scenario_id, renewal_date.isoformat(), original_rate, estimated_renewal_rate,
            rate_delta_bps, round(orig_payment, 2), round(renewal_payment, 2),
            round(increase, 2), round(pct_increase, 2)
        ))

    cur.executemany(
        """INSERT OR REPLACE INTO renewal_shock
           (scenario_id, renewal_date, original_rate, estimated_renewal_rate, rate_delta_bps,
            original_monthly_payment, renewal_monthly_payment, monthly_payment_increase, pct_payment_increase)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        results,
    )
    conn.commit()
    print(f"Computed renewal shock for {len(results)} scenarios.")
    for r in results:
        print(f"  scenario {r[0]}: {r[2]}% -> {r[3]}%  |  +${r[7]}/mo ({r[8]}%)")


def plot_rate_history(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT decision_date, overnight_rate FROM rate_history ORDER BY decision_date"
    ).fetchall()
    dates = [date.fromisoformat(r[0]) for r in rows]
    rates = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.step(dates, rates, where="post", color="#1f4e79", linewidth=2)
    ax.set_title("Bank of Canada Target Overnight Rate, 2020-2026")
    ax.set_xlabel("Date")
    ax.set_ylabel("Overnight Rate (%)")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out_path = CHARTS_DIR / "rate_history.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def plot_renewal_shock(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """SELECT m.borrower_label, r.pct_payment_increase
           FROM renewal_shock r JOIN mortgage_scenario m ON m.scenario_id = r.scenario_id
           ORDER BY r.pct_payment_increase"""
    ).fetchall()
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#c0392b" if v > 20 else "#e67e22" if v > 0 else "#27ae60" for v in values]
    ax.barh(labels, values, color=colors)
    ax.set_title("Estimated Mortgage Payment Change at Renewal, by Scenario")
    ax.set_xlabel("% Change in Monthly Payment")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    out_path = CHARTS_DIR / "renewal_shock.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        compute_renewal_shock(conn)
        plot_rate_history(conn)
        plot_renewal_shock(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
