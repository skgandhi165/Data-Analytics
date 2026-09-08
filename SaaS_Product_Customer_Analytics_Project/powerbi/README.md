# Power BI build guide

## Pages
1. Executive Growth: MRR, active customers, ARPA, MRR trend
2. Retention: churn rate, churn by plan, cohort retention
3. Customer Health: usage, support load, satisfaction, revenue at risk

## Core measures
MRR = SUM(subscriptions_monthly[mrr])
Active Customers = DISTINCTCOUNT(subscriptions_monthly[account_id])
ARPA = DIVIDE([MRR],[Active Customers])
Churned Accounts = CALCULATE(DISTINCTCOUNT(accounts[account_id]), accounts[churn_flag]=TRUE())
Churn Rate = DIVIDE([Churned Accounts], DISTINCTCOUNT(accounts[account_id]))
Revenue at Risk = CALCULATE(SUM(accounts[mrr]), accounts[churn_flag]=TRUE())

## Analyst view
Add slicers for plan, industry, acquisition channel and cohort month.
The dashboard should answer: where is churn concentrated, how much recurring revenue is exposed, and which customer behaviors correlate with risk?
