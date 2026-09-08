"""
Refreshable SaaS product analytics data.

Primary mode: regenerate a realistic, reproducible customer/event dataset locally.
This avoids API keys and keeps the project portable. Change SEED for a new refresh.
Optional external-source mode can be added later if a company supplies Stripe/PostHog data.

Run:
    python src/refresh_data.py
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data/raw"; RAW.mkdir(exist_ok=True)
SEED=42

def generate():
    rng=np.random.default_rng(SEED)
    n=1200
    ids=np.arange(10001,10001+n)
    signup=pd.to_datetime("2025-01-01")+pd.to_timedelta(rng.integers(0,600,n),unit="D")
    plans=rng.choice(["Starter","Pro","Business","Enterprise"],n,p=[.42,.32,.20,.06])
    price={"Starter":79,"Pro":199,"Business":499,"Enterprise":1299}
    base=np.array([{"Starter":3,"Pro":8,"Business":18,"Enterprise":45}[p] for p in plans])
    seats=np.maximum(1,np.round(rng.lognormal(np.log(base),.35)).astype(int))
    mrr=np.array([price[p] for p in plans])*seats
    churn=(rng.random(n)<(.08+.05*(plans=="Starter")+.04*(plans=="Pro")))
    churn_date=signup+pd.to_timedelta(rng.integers(60,500,n),unit="D")
    churn_date=pd.to_datetime(np.where(churn & (churn_date<=pd.Timestamp("2026-08-26")),churn_date,np.datetime64("NaT")))
    a=pd.DataFrame({"account_id":ids,"signup_date":signup,"plan":plans,"seats":seats,"mrr":mrr,"churn_date":churn_date,"churn_flag":pd.notna(churn_date)})
    a.to_csv(RAW/"saas_accounts_live.csv",index=False)
    print("Refreshed:",len(a),"accounts. Change SEED in this file to create another reproducible refresh.")

if __name__=="__main__": generate()
