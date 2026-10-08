"""RSI(2) 5/95 (and 10/90) on forex, daily vs 4H, 2 and 7 pairs (Jeff wants faster charts, Oct 8 2026)."""
import f39_both as f
import forex_dxy as fx  # noqa
PAIRS7 = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
per = ((f.FX0, None), (f.FX0, f.FXCUT), (f.FXCUT, None))
h4 = {p: f.fx.fxcm(p) for p in PAIRS7}
print("| Chart | Pairs | RSI | 2012-now | 2012-18 | 2019-now | trades/yr |\n|---|---|---|---|---|---|---|")
for tf in ("1D", "4H"):
    data = {p: (h4[p] if tf == "4H" else f.fx.fx_daily(h4[p])) for p in PAIRS7}
    for name, ps in (("EUR+GBP", ["EURUSD", "GBPUSD"]), ("7 majors", PAIRS7)):
        for lo in (5, 10):
            d = {p: data[p] for p in ps}
            sig = {p: f.rsi2_signals(d[p], lo, True) for p in ps}
            rs = [f.fx_sim(sig, d, a, b) for a, b in per]
            print(f"| {tf} | {name} | {lo}/{100-lo} | " + " | ".join(f.cell(r) for r in rs) + f" | {rs[0]['trades']/14.6:.0f} |", flush=True)
