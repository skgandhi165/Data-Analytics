-- SaaS Product & Customer Analytics
-- Assumes tables: accounts, subscriptions_monthly, feature_usage, support_tickets.

-- 1. MRR and active customers
SELECT month, SUM(mrr) AS mrr, COUNT(DISTINCT account_id) AS active_customers
FROM subscriptions_monthly
GROUP BY month ORDER BY month;

-- 2. Churn by plan
SELECT plan,
       COUNT(*) AS accounts,
       AVG(CASE WHEN churn_flag=1 THEN 1.0 ELSE 0 END) AS churn_rate,
       SUM(CASE WHEN churn_flag=1 THEN mrr ELSE 0 END) AS revenue_at_risk
FROM accounts
GROUP BY plan ORDER BY churn_rate DESC;

-- 3. Revenue at risk by industry
SELECT industry,
       SUM(CASE WHEN churn_flag=1 THEN mrr ELSE 0 END) AS mrr_at_risk,
       COUNT(CASE WHEN churn_flag=1 THEN 1 END) AS churned_accounts
FROM accounts
GROUP BY industry ORDER BY mrr_at_risk DESC;

-- 4. Customer health: usage + support
WITH usage AS (
  SELECT account_id, SUM(usage_count) AS feature_uses
  FROM feature_usage GROUP BY account_id
),
support AS (
  SELECT account_id, COUNT(*) AS tickets,
         AVG(resolution_hours) AS avg_resolution,
         AVG(satisfaction_score) AS avg_satisfaction
  FROM support_tickets GROUP BY account_id
)
SELECT a.account_id, a.plan, a.mrr, a.churn_flag,
       COALESCE(u.feature_uses,0) AS feature_uses,
       COALESCE(s.tickets,0) AS tickets,
       COALESCE(s.avg_resolution,0) AS avg_resolution,
       COALESCE(s.avg_satisfaction,0) AS avg_satisfaction
FROM accounts a
LEFT JOIN usage u ON a.account_id=u.account_id
LEFT JOIN support s ON a.account_id=s.account_id;
