# F1 results: the bots at the user's real OKX fees

Plan: research/FEES_PLAN.md. Script: research/fees_test.py. Run 2026-10-05. Fee setups: **T** = market orders, 0.35% buy + 0.35% sell (what the bots pay now); **M** = limit buy 0.20% + market sell 0.35% (optimistic: assumes every limit buy fills). Each bot uses its live settings ($1,000, v4 at 0.4% risk and the others at 0.5%, no half sell). The breakeven buffer equals the real round-trip fee.

| Bot / variant | Fees | 2018-now return / DD / PF | 1st half (2018-21) | 2nd half (2022-now) | Pass? |
|---|---|---|---|---|---|
| SP-12 v4 (as now) | T | −2% / −31.3% / 0.99 | +29% | −24% | no |
| SP-12 v4 (as now) | M | +42% / −21.8% / 1.20 | +36% | +4% | no (DD, PF) |
| v4 V1 min stop 2% | T | +6% / −28.1% / 1.03 | +30% | −19% | no |
| v4 V1 min stop 2% | M | +47% / −18.5% / 1.23 | +37% | +7% | no (DD, PF) |
| v4 V2 stop 3-6% | T | +18% / −19.8% / 1.09 | +20% | −2% | no |
| v4 V2 stop 3-6% | M | +35% / −16.9% / 1.17 | +27% | +6% | no (DD, PF) |
| v4 V3 score ≥ 3 | T | +1% / −22.3% / 1.01 | +16% | −13% | no |
| v4 V3 score ≥ 3 | M | +12% / −20.1% / 1.13 | +19% | −6% | no |
| Trend Rider | T | **+185% / −11.8% / 1.69** | +64% | +74% | yes (DD 1.8 points over 10%; the user accepted 10.6% at 0.5% risk) |
| Trend Rider | M | **+231% / −10.9% / 1.85** | +69% | +96% | yes |
| NNFX Aroon (daily) | T | **+45% / −7.6% / 2.00** | +20% | +21% | yes |
| NNFX Aroon (daily) | M | **+48% / −7.5% / 2.08** | +21% | +23% | yes |

Combined by month at T (each bot with half the money, monthly closes, so the drop is understated next to the per-bot DD above):
- Trend Rider + SP-12 v4: +92%, worst monthly drop −9.8%
- Trend Rider + NNFX: +115%, worst monthly drop −6.5% (TR/NNFX monthly correlation 0.56). Every year 2019-2025 was positive except 2022 (−4%).

## What it means
1. **SP-12 v4 has no edge at the user's fees.** All 8 versions fail. It makes about 750 trades in 8 years, so 0.7% a round trip costs it roughly 5R a year, and since 2022 its edge is smaller than that.
2. **Trend Rider is the bot.** It still makes about 13% a year at full market-order fees, and limit buys add about 46 points over 8 years.
3. **NNFX Aroon is the best partner.** It is daily with few trades (193 in 8 years), so fees barely touch it. It passed in both halves, and it lowers the combined drop.
4. **Limit buys help every bot,** but this test assumes every limit buy fills. A forward test on demo is needed before trusting the gain.

Superseded by F1b below. Suggested (needs the user's OK and the Oct 19 review; bot.py not changed): move v4 to PAUSED, promote NNFX Aroon from paper to OKX demo, keep Trend Rider, and set FEE to 0.0035 so paper results and backtests match real costs.

## F1b results (T fees: market orders, 0.35% a side)

| Bot / setting | 2018-now return / DD / PF | 1st half | 2nd half | Pass? |
|---|---|---|---|---|
| Trend Rider at 0.4% risk | **+134% / −9.6% / 1.71** | +49% | +57% | **yes, all rules** |
| NNFX at 0.75% risk | +72% / −10.9% / 1.97 | +31% | +32% | DD just over 10% |
| NNFX at 1% risk | +103% / −13.8% / 1.95 | +43% | +43% | no (DD) |
| B3 pairs (daily) | +11% / −5.6% / 1.39 | +5% | +6% | yes, but small |
| B1c breakout retest (1H) | −9% / −11.7% / 0.85 | +1% | −10% | no |

Line-up that passes every rule at real fees: Trend Rider at 0.4% risk and NNFX at 0.5% (+45%, DD −7.6%), with B3 pairs as an optional small, low-correlation extra. Stop: SP-12 v4 and B1c.
