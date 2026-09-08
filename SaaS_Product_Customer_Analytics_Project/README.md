# SaaS Product & Customer Analytics

## Goal
Analyze the full customer lifecycle: acquisition, subscription revenue, product engagement, support experience, retention and revenue-at-risk.

## Dataset
A reproducible synthetic B2B SaaS dataset with 1,200 accounts plus monthly subscription snapshots, product-usage events and support tickets. It is intentionally structured so the project can demonstrate relational analytics without exposing real customer data.

## Questions
1. How is MRR changing?
2. Which plans and industries have the highest churn?
3. How much recurring revenue is at risk?
4. Do low product engagement and heavier support load correlate with churn?
5. Which customer segments should Customer Success prioritize?

## Tools
Python, SQL, Power BI.

## Refresh
Run `python src/refresh_data.py`. Change the SEED to create a new reproducible dataset. For a truly live company deployment, the same schema can be connected to Stripe/PostHog/HubSpot APIs using credentials supplied by the company. The project does not pretend synthetic data is live production data.

## Resume positioning
Use this project for Product Analytics, SaaS, Technology, E-commerce, Customer Analytics and Business Analyst roles.
