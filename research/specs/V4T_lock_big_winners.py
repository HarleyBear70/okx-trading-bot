"""
V4T: lock in big winners on SP-12 v4 (idea from job 2e: v4's worst drawdowns were open profit given back by the SAR
trail on huge winners, e.g. DOGE 2021 +67R). Written by Terminal Claude on 2026-10-05 BEFORE any run; queued.

After the normal v4 stop update each candle, if the trade has reached a big open profit, its stop is raised further:
- VT1: once the high since entry reaches +10R, the stop never goes below entry + 6R.
- VT2: once the high since entry reaches +10R, the stop never goes below (highest high since entry - 3R).
- VT3: once the high since entry reaches +5R, the stop never goes below entry + 3R.
(R = entry - original stop.) v4 only; entries and everything else untouched.
Pass: spec_runner overlay rules (both halves incl. the 2022-now holdout, DD within 10%, never-seen coins not worse).
Expect few trades affected (+10R is rare), so a pass needs a real effect, not noise.
"""
SPEC = {"id": "V4T", "title": "Lock in big winners on SP-12 v4", "written": "2026-10-05", "author": "Terminal Claude",
        "kind": "overlay", "bots": ["v4"]}


def wrap(trigger_r, rule):
    def make(orig):
        def manage_on_close(api, b, bs, coin, a, i, bar, bars_in):
            closed = orig(api, b, bs, coin, a, i, bar, bars_in)
            pos = bs["positions"].get(coin)
            if closed or not pos or b["strat"] != "v4":
                return closed
            r = pos["entry_px"] - pos["sl"]
            hi = pos.get("hi") or bar["h"]
            if r > 0 and hi >= pos["entry_px"] + trigger_r * r:
                floor = pos["entry_px"] + rule * r if rule > 0 else hi + rule * r
                pos["stop"] = max(pos["stop"], floor)
            return closed
        return manage_on_close
    return make


VARIANTS = {"VT1: at +10R lock +6R": {"manage_wrap": wrap(10, 6)},
            "VT2: at +10R trail 3R under the high": {"manage_wrap": wrap(10, -3)},
            "VT3: at +5R lock +3R": {"manage_wrap": wrap(5, 3)}}
