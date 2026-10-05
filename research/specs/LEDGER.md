# Test ledger (keeps data-mining honest)

Every strategy / filter variant ever judged against pass rules is counted here. The more variants we test, the more
will pass by luck, so a pass is only worth a PAPER trial, never real money on its own.

Variants tested so far: 133
Rule passes so far: 10
(expected lucky passes at a 5% false-pass rate: about 7)

Before the Scout loop (Oct 5 2026, by hand, research/*.md): score lines 4 (SCORE), drawdown fixes 13, forex + DXY 13,
crypto DXY 3, v2 repair 3, gold repair 3, coin picks 11, volatility guard 3, N1 3, N2 3, N3 3, B1 3, B2 3, D1 6, N4 3,
B3 3, S1 6, H1 4, H2 3, H3 3, H5 2, hold pile 2, TRX 2, Q1 3, NNFX 13, R1 3, W1 9 = 127.
Passes among them: 0.5% risk, XLM, BNB, S1 F2 (Trend Rider fear filter), H3 G1 and G3 (marginal), dip DCA, TRX for v4,
TRX for Trend Rider, W1 v4 volume (then failed the never-seen check) = 10. About 6 would be expected by luck, which is
why every pass also has to hold on never-seen coins and in the 2022-now holdout, then prove itself on paper.

| Date | Spec | Variant | Result |
|---|---|---|---|
<!-- rows -->
| 2026-10-05 | T1 | SP-12 v4 / TS1: 4H ADX | fail |
| 2026-10-05 | T1 | SP-12 v4 / TS2: daily ADX | fail |
| 2026-10-05 | T1 | SP-12 v4 / TS3: 4H EMA50 slope | fail |
| 2026-10-05 | T1 | Trend Rider / TS1: 4H ADX | fail |
| 2026-10-05 | T1 | Trend Rider / TS2: daily ADX | fail |
| 2026-10-05 | T1 | Trend Rider / TS3: 4H EMA50 slope | fail |
