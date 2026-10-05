# Risk step-ups off vs on (Oct 5 2026)

Same footing as SCOREBOARD.md: $1,000, 0.5% base risk, 0.1% fee, max 3 open. Each cell: return / worst drop / return ÷ drop. Made by `python research/steps_compare.py`. Only bots that size trades through `bot.risk_pct()` are here (B1c, B3 and the research bots use a fixed 0.5%).

| Bot | Period | Step-ups off: return / max DD / return÷DD | Step-ups on: return / max DD / return÷DD |
|---|---|---|---|
| SP-12 v4 (BTC ETH XRP XLM BNB) | full | +93% / -10.2% / 9.17 | +82% / -15.8% / 5.19 |
| SP-12 v4 (BTC ETH XRP XLM BNB) | 1st half | +50% / -6.3% / 8.06 | +46% / -12.0% / 3.85 |
| SP-12 v4 (BTC ETH XRP XLM BNB) | 2nd half | +28% / -10.2% / 2.80 | +27% / -13.5% / 2.02 |
| SP-12 v4 (Kraken paper) (BTC ETH XRP) | full | +55% / -9.9% / 5.61 | +44% / -15.3% / 2.87 |
| SP-12 v4 (Kraken paper) (BTC ETH XRP) | 1st half | +29% / -5.6% / 5.23 | +28% / -10.5% / 2.66 |
| SP-12 v4 (Kraken paper) (BTC ETH XRP) | 2nd half | +20% / -9.9% / 2.03 | +13% / -12.7% / 1.05 |
| Trend Rider (BTC ETH SOL BNB SUI TRX) | full | +195% / -8.4% / 23.08 | +527% / -13.9% / 37.78 |
| Trend Rider (BTC ETH SOL BNB SUI TRX) | 1st half | +59% / -7.4% / 7.97 | +121% / -13.5% / 8.96 |
| Trend Rider (BTC ETH SOL BNB SUI TRX) | 2nd half | +86% / -6.7% / 12.81 | +149% / -12.4% / 12.01 |
| SP-12 v2 (ETH SOL XAUT) | full | +5% / -20.9% / 0.22 | +5% / -20.9% / 0.22 |
| SP-12 v2 (ETH SOL XAUT) | 1st half | -12% / -20.3% / -0.59 | -12% / -20.3% / -0.59 |
| SP-12 v2 (ETH SOL XAUT) | 2nd half | +19% / -9.1% / 2.11 | +40% / -11.9% / 3.34 |
| Trend Rider gold (pivot 3) (XAUT (from 2020)) | full | -1% / -16.3% / -0.08 | -1% / -16.3% / -0.08 |
| Trend Rider gold (pivot 3) (XAUT (from 2020)) | 1st half | -3% / -5.6% / -0.54 | -3% / -5.6% / -0.54 |
| Trend Rider gold (pivot 3) (XAUT (from 2020)) | 2nd half | +2% / -12.2% / 0.17 | +2% / -12.2% / 0.17 |
| NNFX Aroon (BTC ETH XRP, daily) | full | +56% / -7.3% / 7.64 | +62% / -11.3% / 5.47 |
| NNFX Aroon (BTC ETH XRP, daily) | 1st half | +23% / -7.3% / 3.19 | +30% / -9.7% / 3.08 |
| NNFX Aroon (BTC ETH XRP, daily) | 2nd half | +27% / -5.4% / 5.01 | +32% / -10.5% / 3.01 |
