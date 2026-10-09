# Brad Goh, "Market Mechanics": the exact rulebook
Built Oct 8 2026 from the full word-for-word transcripts of all 35 episodes (Ep 0–33 + Bonus).
Transcripts: `Claude Files/From Claude/transcripts/Market Mechanics/`

**How to read this**
- Plain text = Brad's rule, as he says it.
- **⚙️ BOT CHOICE** = Brad is vague here, so a bot has to pick a number. Test it, don't guess.
- **⚠️ NOTE** = something Jeff should know (cost, sales, missing data).

---

## 1. The building blocks (definitions a computer can follow)

**Trend (Ep 5)**
- Up = higher highs + higher lows. Down = lower highs + lower lows. Otherwise = sideways = **no trade**.

**Break of structure, BOS (Ep 5)**
- A candle **BODY CLOSES** beyond the last structural high (uptrend) or low (downtrend).
- **A wick through it does NOT count.**

**Swing range (Ep 5)**
- Uptrend: the **swing low** = the LOWEST point that led to the latest BOS (the "strong low").
- The **swing high** = the highest point before the pullback starts. You only know it once price starts pulling back. This is the "weak high".
- Only care about price inside this range. When a new BOS happens, redraw it.

**Internal structure (Ep 5, Bonus)**
- Everything inside the swing range, read with the same rules.
- Internal structure always turns before swing structure does ("fractal").

**Market shift, MS (Ep 5, Bonus)**
- A body close through the **strong** point: the strong low in an uptrend, or the strong lower high in a downtrend. It means the trend flipped.
- Until an MS happens, any move against the trend is just a pullback.
- An MS with **no follow-through** (no next BOS in the new direction) is unconfirmed. It may just be a liquidity sweep.

**Premium / Discount (Ep 8)**
- Put 0 / 50% / 100% on the swing range. Above 50% = premium (sell zone). Below 50% = discount (buy zone).

**Supply / Demand zone (Ep 7)**
- The origin of a strong move (big candles).
- Two ways to draw it: the **range method** (the whole consolidation, high to low) or the **pivot method** (just the reversal candle, high to low).
- **⚙️ BOT CHOICE:** range or pivot. Brad says to test both over 100 trades and stick with one.

**Order block, OB (Ep 10)**
- The pivot candle right before a sharp move. It must meet all three:
  1. It leaves a **fair value gap**. No gap = not an OB.
  2. The move is sharp and V-shaped.
  3. The move causes a **BOS**.
- The bull OB candle should also take out the previous candle's low.

**Fair value gap, FVG (Ep 9)**
- A 3-candle pattern. Bull FVG = the gap between candle 1's HIGH and candle 3's LOW.
- Candle 2 must be clearly bigger than its neighbours.
- Price may react at the near edge, the 50% line, the far edge, or right through it.

**Flip zone (Ep 14)**
- It forms when an opposing zone FAILS. Example for a demand flip:
  - In a downtrend, price reaches supply but can't make a lower low (a "failed reaction").
  - Then a body closes above that reaction point AND structure breaks.
- **All 3 are required.** The box = the high to low of the failed reaction.

**Liquidity (Ep 13, 15)**
- Stops sit above swing highs and below swing lows.
- The obvious spots: any untouched high or low, **equal highs/lows**, trendline touches, obvious support/resistance, and the **prior day's high and low**.

**Liquidity sweep (Ep 13)**
- Price takes out one of those levels, then snaps back in a V. **A sweep alone is NOT a reversal.**

**Liquidity zone (Ep 13)**
- A supply/demand zone or OB whose own move swept liquidity. This makes it stronger.

**Inducement (Ep 13)**
- Bait. Examples: a double top or bottom, a minor high or low just before a zone, the first touch of an obvious zone.
- If untaken liquidity sits just beyond your zone, expect price to run it first. **Don't buy the first touch.**

**Mitigation (Ep 7)**
- A zone is "used up" once price has come back to its **50% line**.
- A shallow touch does not count, so the zone is still fresh.
- Used zones usually fail the next time.

---

## 2. Picking which zone (Ep 8, 10, 13, 17, 25)

Score each zone. **Only take zones that pass the first two:**
1. **In the right half:** demand in discount, supply in premium. A zone in the wrong half is expected to fail.
2. **With the trend:** demand in an uptrend, supply in a downtrend (the trend price is in *right now*).
3. **Most extreme wins:** the zone at the strong low/high beats nearer zones. Nearer zones often get run straight through.
4. **Swept liquidity / caused a BOS:** this makes the zone stronger.
5. **Fresh:** price hasn't been back to its 50% line yet.
6. **Higher timeframe wins:** a 15m zone beats a 5m zone.

Brad does **not** guess which of the good zones will hold (Ep 17: "I don't know and I don't care"). He waits for the entry signal at whichever one price reaches.

---

## 3. THE TRADE PLAN, step by step (Ep 11, 15, 17, 18, 25)

### Timeframes he uses (Ep 11, 18)
| Style | Trend (HTF) | Zones (MTF) | Entry (LTF) |
|---|---|---|---|
| Day trader | 4H (he adds 1H) | 15m | 5m (1m to fine-tune) |
| Scalper | 1H | 5m / 15m | 1m |
| Swing | Daily | 4H | 1H / 15m |

### Step 1: Bias on the HTF (Ep 15)
- Map the trend, swing range and premium/discount.
- **Middle of the range = no trade** (or smaller size).
- Mark the liquidity: prior-day high/low and equal highs/lows. Which side is the obvious magnet?
- Ask: is price continuing the trend, or pulling back?
- Write it as one sentence plus what would prove it wrong: "Bearish; wrong if a candle closes and holds above X."

### Step 2: Zones on the MTF
- Mark the zones that pass section 2. Set an alert at the zone's edge.
- **Do nothing until price touches a zone.** "Middle of nowhere = no trade."

### Step 3: Entry on the LTF, only after a zone is touched
His non-negotiables (Ep 18, 25, Bonus):
- (a) A **liquidity sweep** at or near the zone. "No sweep, no entry."
- (b) A **market shift** on the LTF: a body close through the last internal high (for longs).

**Entry model A, "Market Shift" (his main one)**
- After the MS, mark the LTF zone that caused it (the extreme zone at the sweep low).
- Put a limit order there.
- **If price never comes back to it: no trade.**

**Entry model B, "Flip"**
- If a failed reaction formed during the MS, enter when price comes back to that flip zone.
- His rule: if BOTH a flip zone and an extreme zone exist, **use the extreme zone**. The liquidity under the flip usually gets swept first.

**Aggressive version (Ep 17, 20, Bonus)**
- Enter right after the sweep, before any MS.
- Only allowed when internal structure is already on your side and liquidity on both sides has been taken.
- Target only the nearest opposing level.

**False MS warning (Ep 18)**
- If price takes out the low again after an MS, that was a liquidity grab. Wait for a fresh sweep and a new MS.

### Step 4: Stop loss (Ep 17, 18, 20)
- A few pips beyond the **protected high/low** (the one that swept liquidity), OR a few pips beyond the entry zone.
- Use whichever is closer.
- Never exactly at the zone edge, because wicks will take you out.
- Set it before entry. **Never move it further away** (Ep 22).

### Step 5: Take profit (Ep 15, 17, 18, 20, Bonus)
- **ONE target only:**
  - the next opposing zone or structural high/low **on the entry timeframe or one timeframe above it**, or
  - the prior-day high/low, or
  - an unfilled FVG.
- "Be pessimistic on TP." Don't aim for a big higher-timeframe level from a small-timeframe entry.
- Simple version for beginners (Ep 18, 25): **fixed 2R**.
- **Skip the trade if the logical target is less than 2R away** (Ep 25).

### Step 6: Management (Ep 17)
- **Set and forget.** No partial profits, no trailing stop. It ends at full target or full stop.

---

## 4. A+ checklist (Ep 25): all 5 = A+. Missing one = at most an A. B and C setups = no trade.
1. The trade agrees with the current (LTF) bias, and ideally the HTF too. If they disagree, beginners stay out.
2. Price is **inside** a strong zone (section 2), not just near it.
3. Liquidity sweep + market shift.
4. Inside his session window (killzone).
5. At least 2R to the logical target.

---

## 5. When NOT to trade (Ep 12, 19, 22, 30)
- Price not at a zone, or price in the middle of the range.
- Choppy, sideways price with no clear bias.
- **Mondays and Fridays** (day trades). Exception: a true A+ setup. Swing trades already open are kept.
- **All of December.**
- **The last trading day of the month.**
- **15–30 min before AND after high-impact news.** After that, wait 30–60 min for things to settle.
- Outside your one chosen session.
- Not in the right frame of mind, or after a losing streak of 5–10 (take about a week off and review).
- **After any loss: wait 10 minutes, and never enter on the very next candle** (Ep 22).

### Sessions (Ep 12, New York / ET time)
- **Asia** 8pm–12am (AUD/NZD/JPY, choppy).
- **London** 2–5am (EUR/GBP). This is HIS session, about 90% of his trades.
- **New York** 7–10am (USD pairs, news).
- **London close** 10am–12pm.
- **Asia sweep idea:** London often sweeps one side of the Asia range, then reverses.
- **Nothing in the series is crypto-specific.**

---

## 6. Risk rules (Ep 21, 25, 31)
- **0.5–1% per trade, never changed because of mood.** Optional: 0.5% on an A setup, 1% on an A+ (only once you have data).
- Daily loss cap **2–3%**. Total drawdown **5–10%**, then cut size or pause.
- **At most 3 trades a day**, win or lose.
- Daily profit cap (he uses 5–10%; 1% on prop-firm challenges).
- Prop-firm settings (Ep 31): 0.5% risk, 3 trades a day, 2% daily stop, trade only your best session window.

## 7. Improving the plan (Ep 16, 23, 24, 26, 27)
- Don't change a rule until you have **100 trades or 3 months** of data (30–50 at the very least). A losing streak alone is not a reason.
- Change at most **1–3 things a quarter**. Every change means re-testing the whole plan.
- High win rate but small wins → stop cutting winners early. Low win rate but big wins → be pickier (A+ only).
- Grade trades by **following the plan**, not by profit. A "good loss" followed the plan. A win where you broke rules is not something to celebrate.

---

## 8. ⚙️ The numbers Brad never gives (a bot must test these)
| Question | Brad says | Options to test |
|---|---|---|
| What counts as a swing high/low? | "the obvious ones" | fractal 2/3/5 bars, or the Smoke Detector engine |
| How far back can the sweep be? | "liquidity on the left" | 12 / 24 / 48 candles (already tested, see below) |
| Range or pivot zone? | test both | both |
| Displacement size? | "clearly bigger" | body > 1.5× / 2× average body |
| How long a zone stays valid | until 50% mitigated | also try 1–2 day / 5-day expiry (from the S&D video) |
| How long to wait for the pullback after MS | not given | 6 / 12 / 24 LTF candles |
| Stop buffer | "a few pips" | 0.1 / 0.15 / 0.25 ATR |
| Target | next opposing zone OR 2R | structural target with a 2R minimum vs fixed 2R / 3R |

---

## 9. What we ALREADY tested vs what's NEW
**Already tested** (research/BRAD_RULES.md, using Gemini summaries of his other videos):
- sweep + MS + FVG limit entry, fixed 2R/3R.
- **15m loses on crypto AND forex** (profit factor 0.6–0.9).
- **1H is barely positive**: crypto across 23 coins PF ~1.2–1.3, about +0.15–0.2R a trade, and that's at a **0.07% fee each side**.
- brad_bot.py runs that 1H version on paper. jeff_bot.py runs a 15m top-down version.

**New from the full series (never tested yet):**
1. **Entry at the zone that caused the MS**, and *no trade if price doesn't come back*. brad_bot uses the top of the FVG instead.
2. **Extreme zone beats flip zone.**
3. **Only fresh zones** (the 50% rule) that **sit in the right premium/discount half AND caused a BOS**.
4. **Target = next opposing zone, skip if under 2R.** We've only tested fixed R so far.
5. **Body-close-only BOS/MS, with follow-through** for the MS.
6. **No-trade filters:** Mon/Fri, December, last day of the month, max 3 trades/day, 2% daily stop, the 10-minute rule.
7. **Prior-day high/low** as the liquidity to sweep and as the target.
8. **Asia-range sweep in London** (forex only).

---

## 10. ⚠️ Honest notes for Jeff
- **Brad shows NO win rates or backtest numbers** for any rule, anywhere in 35 episodes. The only numbers are his personal profit claims ($3M+, "80%" for premium/discount as a feel).
- **He says himself the free series is "maybe 10%" of what paid students get** (Bonus). He says he has ~10 entry models but only shows 2. Every episode pushes EdgeFlow or the 1% Club.
- **It's built for forex sessions.** Crypto never closes, and he says nothing crypto-specific.
- **Fees:** in Ep 3 he says "don't worry too much about transaction costs." Only true at low fees. Our 1H edge is about +0.2R at **Binance.US costs (0.02% fee + slippage = 0.05-0.07% a side)**, which is where the live bots trade. At **OKX's 0.35%** it would very likely go negative, so Brad-style bots belong on Binance.US, not OKX.
- **Good news:** many of his rules are filters (fewer, pickier trades, fixed risk, a daily stop). That *suits* high fees, because fewer trades means less paid in fees.
- His best numbers-free advice matches the Alpha Agents lesson: **test over 100+ trades, change one thing at a time.**
