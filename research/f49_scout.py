"""F49 research scout 2026-11-21. Rules fixed BEFORE testing. Reuses F46 crypto sim (Binance.US daily, halves 2022-01-01) and F47 forex close-only sim (Fed H.10).
H crypto 52-week-high nearness (George & Hwang 2004, 252-day window as for BTC): close >= 0.95*highest close of last 252 days, close > SMA200, and yesterday was NOT (fresh) -> long.
  Exit close < 0.85*highest close of 252 days. Stop 3 ATR(20).
X forex EUR/GBP cross reversion (pairs-trading idea; synthetic EURGBP = EURUSD/GBPUSD): r=ln(GBPUSD/EURUSD), z=(r-mean60)/sd60. z<-2 -> long synthetic (long GBP/USD, short EUR/USD), z>2 -> short.
  Exit when z crosses 0 or 20 bars. Stop 3 ATR (20d mean abs change of ratio). Cost 0.02% a side (two legs).
V forex value / 2-year mean reversion: z of ln price vs 500-day mean/sd. z<-1.5 -> long, z>1.5 -> short. Exit z crosses 0 or 60 bars. Stop 10 ATR(20d mean abs close change). Each pair separately, 0.01% a side.
Forex: risk 0.5%, leverage cap 10x, halves 2012-18 / 2019-now (closes only). Crypto fees 0.35% and 0.02%."""
import sys, os, math, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f46_scout as c46, f47_fx_close as f47

def hsig(b):
    c=[x["c"] for x in b]; a=c46.atr(b); n=len(b); sig=[None]*n
    for k in range(260,n-1):
        if not a[k]: continue
        hi=max(c[k-251:k+1]); hi1=max(c[k-252:k]); s200=sum(c[k-199:k+1])/200
        if c[k]>=0.95*hi and c[k]>s200 and not (c[k-1]>=0.95*hi1):
            sig[k]=(c[k]-3*a[k], lambda j: c[j] < 0.85*max(c[j-251:j+1]))
    return sig

def zsig(c, win, thr, maxbars, stopmult, ex_cross=0.0):
    n=len(c); out=[None]*n; l=[math.log(x) for x in c]
    tr=[0]+[abs(c[i]-c[i-1]) for i in range(1,n)]
    def z(i):
        w=l[i-win+1:i+1]; sd=st.pstdev(w); return (l[i]-sum(w)/win)/sd if sd else 0
    for k in range(win+5,n-1):
        a=sum(tr[k-19:k+1])/20; zk=z(k)
        if zk<-thr: out[k]=(1,c[k]-stopmult*a, lambda j,k=k: z(j)>=0 or j-k>=maxbars)
        elif zk>thr: out[k]=(-1,c[k]+stopmult*a, lambda j,k=k: z(j)<=0 or j-k>=maxbars)
    return out

def crypto():
    data={c:c46.load(c) for c in c46.SEEN+c46.UNSEEN}
    for fee in (0.0035,0.0002):
        for grp,coins in (("seen",c46.SEEN),("unseen",c46.UNSEEN)):
            for name,t0,t1 in (("1st",0,c46.CUT),("2nd",c46.CUT,None)):
                rs=[c46.sim(data[c],hsig(data[c]),fee,t0,t1) for c in coins]
                print("H fee %.2f%% %-6s %s half: avg %+6.1f%% worst dd %5.1f%% avg PF %.2f trades %4d coins+ %d/%d"%(fee*100,grp,name,
                    sum(r["ret"] for r in rs)/len(rs),max(r["dd"] for r in rs),sum(r["pf"] for r in rs)/len(rs),sum(r["n"] for r in rs),sum(r["ret"]>0 for r in rs),len(rs)))
def forex():
    E=dict(zip(*f47.load("Euro"))); G=dict(zip(*f47.load("United Kingdom")))
    ds=sorted(set(E)&set(G)); e=[E[d] for d in ds]; g=[G[d] for d in ds]
    ratio=[g[i]/e[i] for i in range(len(ds))]
    H=[("2012-18","2012-03-01","2019-01-01"),("2019-now","2019-01-01","2099")]
    sg=zsig(ratio,60,2.0,20,3)
    for hn,a,b in H: print("X cross GBP/EUR", hn, "ret %+6.1f%% dd %4.1f%% PF %.2f trades %d"%f47.sim(ds,ratio,sg,a,b,cost=0.0002))
    for p,(d,c) in {"EURUSD":f47.load("Euro"),"GBPUSD":f47.load("United Kingdom")}.items():
        sg=zsig(c,500,1.5,60,10)
        for hn,a,b in H: print("V value",p,hn,"ret %+6.1f%% dd %4.1f%% PF %.2f trades %d"%f47.sim(d,c,sg,a,b))
if __name__=="__main__":
    crypto(); forex()
