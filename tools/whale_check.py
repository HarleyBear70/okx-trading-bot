"""
Whale check (Jeff, Oct 7 2026): what the most profitable traders on Hyperliquid are betting on right now, plus funding
and open interest for Jeff's coins. Hyperliquid's data is public (no key). US residents can't trade there; this is
CONTEXT for the News Watch, not a trade signal: a few big wallets dominate, and some are hedges, not bets.

  python tools/whale_check.py
"""
import json, urllib.request
def post(body):
    r = urllib.request.Request("https://api.hyperliquid.xyz/info", data=json.dumps(body).encode(),
                               headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "LINK", "SUI"]
meta, ctx = post({"type": "metaAndAssetCtxs"})
names = [u["name"] for u in meta["universe"]]
print("| Coin | Price | Funding (per hour) | Yearly equiv. | Open interest ($M) | 24h volume ($M) |")
print("|---|---|---|---|---|---|")
for c in COINS:
    if c in names:
        x = ctx[names.index(c)]
        px, f = float(x["markPx"]), float(x["funding"])
        print(f"| {c} | {px:,.6g} | {f*100:+.4f}% | {f*24*365*100:+.1f}% | {float(x['openInterest'])*px/1e6:,.0f} | {float(x['dayNtlVlm'])/1e6:,.0f} |")
lb = json.loads(urllib.request.urlopen(urllib.request.Request("https://stats-data.hyperliquid.xyz/Mainnet/leaderboard",
                headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
rows = lb.get("leaderboardRows", lb)
def pnl(r, w):
    for k, v in r.get("windowPerformances", []):
        if k == w: return float(v.get("pnl", 0))
    return 0.0
top = sorted(rows, key=lambda r: pnl(r, "allTime"), reverse=True)[:40]
agg = {c: [0.0, 0.0, 0, 0] for c in COINS}  # long $, short $, long traders, short traders
seen = 0
for r in top:
    try:
        st = post({"type": "clearinghouseState", "user": r["ethAddress"]})
    except Exception:
        continue
    seen += 1
    for ap in st.get("assetPositions", []):
        p = ap["position"]; c = p["coin"]
        if c in agg:
            sz = float(p["szi"]); val = abs(float(p["positionValue"]))
            if sz > 0: agg[c][0] += val; agg[c][2] += 1
            elif sz < 0: agg[c][1] += val; agg[c][3] += 1
print(f"\nTop {seen} all-time most profitable Hyperliquid traders - their positions now (one big wallet can dominate):")
print("| Coin | Long $ (traders) | Short $ (traders) | Net |")
print("|---|---|---|---|")
for c, (l, s, nl, ns) in agg.items():
    if l or s:
        print(f"| {c} | ${l/1e6:,.1f}M ({nl}) | ${s/1e6:,.1f}M ({ns}) | {'LONG' if l > s else 'SHORT'} {abs(l-s)/(l+s)*100:.0f}% |")
