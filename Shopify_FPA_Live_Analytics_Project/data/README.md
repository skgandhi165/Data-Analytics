# Data notes

Seed files are source-backed snapshots used so the project can be opened without internet access.

`shopify_financials_seed.csv`
- Revenue, gross profit, OpEx and operating income are US$ millions.
- GMV and MRR are Shopify operating indicators, also US$ millions.
- FCF is reported where available.

`shopify_market_seed.csv`
- Daily SHOP price snapshot for context only.

For the live version, run `src/fetch_data.py`. New SEC facts and market data are written to separate `*_live.csv` files so the seed data remains reproducible.
