import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=pd.read_csv(ROOT/"data/raw/saas_accounts_seed.csv",parse_dates=["signup_date","churn_date"])
u=pd.read_csv(ROOT/"data/raw/saas_feature_usage_seed.csv",parse_dates=["usage_date"])
s=pd.read_csv(ROOT/"data/raw/saas_support_seed.csv",parse_dates=["ticket_date"])
a["churn_flag"]=a.churn_date.notna()
u1=u.groupby("account_id").agg(usage_events=("usage_id","count"),feature_uses=("usage_count","sum"))
s1=s.groupby("account_id").agg(tickets=("ticket_id","count"),avg_resolution_hours=("resolution_hours","mean"),avg_satisfaction=("satisfaction_score","mean"))
out=a.join(u1).join(s1).fillna(0)
out["revenue_at_risk"]=out.mrr.where(out.churn_flag,0)
out["health_score"]=(50+(out.feature_uses/10).clip(0,20)-(out.tickets*2).clip(0,12)+(out.avg_satisfaction-3).clip(-2,2)*5).clip(0,100)
out.to_csv(ROOT/"data/processed/account_health_live.csv",index=False)
print("Wrote account health table.")
