"""
F16: bounded adaptation (research/F16_PLAN.md). Research only.

  python research/f16_adapt.py <A1|A2> [u]      u = never-seen coins
"""
import bisect
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import engine as e  # noqa: E402
import f10_exits as f10  # noqa: E402

UTC = dt.timezone.utc


def shadow_curves(test, unseen):
    """{name: [(ts, equity)]} for every allowed setting, full history; the first name is the default."""
    if test == "A1":
        out = {}
        for name, trail in (("trail 3 ATR", 3.0), ("trail 4 ATR", 4.0)):
            cs, per, risk, mo = f10.prepare("TR", trail, unseen=unseen)
            out[name] = f10.sim(cs, per, risk, mo, False, e.START)["curve"]
        return out
    cs, per, _, mo = f10.prepare("DC", 3.0, unseen=unseen)
    return {name: f10.sim(cs, per, 0.0032, mo, pyr, e.START)["curve"]
            for name, pyr in (("plain", False), ("pyramid", True))}


def value_at(curve, ts_list, t):
    j = bisect.bisect_right(ts_list, t) - 1
    return curve[max(j, 0)][1]


def ret_dd(curve, ts_list, t0, t1):
    seg = [v for ts, v in curve if t0 <= ts < t1]
    if len(seg) < 2:
        return 0.0, 0.0
    peak, dd = seg[0], 0.0
    for v in seg:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return seg[-1] / seg[0] - 1, dd


def quarters(t0, t1):
    out, y, q = [], t0.year, (t0.month - 1) // 3
    d = dt.datetime(y, q * 3 + 1, 1, tzinfo=UTC)
    while d < t1:
        out.append(d)
        m = d.month + 3
        d = dt.datetime(d.year + (m > 12), (m - 1) % 12 + 1, 1, tzinfo=UTC)
    return out


def adaptive(curves):
    names = list(curves)
    tsl = {n: [ts for ts, _ in c] for n, c in curves.items()}
    qs = quarters(e.START, e.now())
    picks, eq, out = [], 1000.0, []
    for qi, q in enumerate(qs):
        q0 = e.ms(q)
        q1 = e.ms(qs[qi + 1]) if qi + 1 < len(qs) else e.ms(e.now()) + 1
        choice = names[0]
        if q - dt.timedelta(days=365) >= e.START:
            best = None
            for n in names:
                r, d = ret_dd(curves[n], tsl[n], q0 - 365 * 86400000, q0)
                score = r / abs(d) if d < 0 else r * 100
                if best is None or score > best + 1e-12:
                    best, choice = score, n
        picks.append((q.strftime("%Y-%m"), choice))
        c = curves[choice]
        base = value_at(c, tsl[choice], q0)
        for ts, v in c:
            if q0 <= ts < q1:
                out.append((ts, eq * v / base))
        eq = out[-1][1] if out else eq
    return out, picks


def slice_stats(curve, t0, t1):
    seg = [(ts, v) for ts, v in curve if e.ms(t0) <= ts < e.ms(t1)]
    peak, dd = seg[0][1], 0.0
    for _, v in seg:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return round((seg[-1][1] / seg[0][1] - 1) * 100, 1), round(dd * 100, 1)


def main():
    test, unseen = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "u"
    curves = shadow_curves(test, unseen)
    ad, picks = adaptive(curves)
    default = list(curves)[0]
    out = {"test": test, "unseen": unseen, "picks": picks}
    for name, cv in (("default " + default, curves[default]), ("other " + list(curves)[1], curves[list(curves)[1]]),
                     ("adaptive", ad)):
        out[name] = {lab: slice_stats(cv, t0, t1 or e.now()) for lab, t0, t1 in [("full", e.START, None), *e.HALVES]}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
