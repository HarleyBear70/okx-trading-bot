# Chrome Claude's trade requests (paper)

Add one line per action at the bottom, starting with "- [ ] ". The hourly bot run carries it out with
analyst/ledger.py --account chrome and rewrites the line as "- [x] ... -> result" or "- [!] ... -> REFUSED: reason".
Coins: BTC ETH SOL XRP BNB LINK. Every BUY/ORDER needs "| why: ... | wrong: ...".

    - [ ] ORDER SOL above 125.3 stop 118.5 hours 72 | why: ... | wrong: ...
    - [ ] ORDER LINK below 13.55 stop 12.85 | why: ... | wrong: ...
    - [ ] BUY BTC stop 84000 | why: ... | wrong: ...
    - [ ] STOP SOL 121.5
    - [ ] SELL SOL | why: ...
    - [ ] CANCEL SOL

## Requests
- [x] ORDER BTC above 87300 stop 84950 hours 48 | why: higher lows since the Oct 2 dip to 83.9k, coiling in an 85k-87k range; a break over the Oct 3 high (87.2k) opens a move up | wrong: falls back under the Oct 5 low (~84.98k) -> 2026-10-06 14:13 UTC: ORDER BTC: buy if price goes above 87300, stop 84950, expires in 48h
- [x] ORDER SOL above 122.4 stop 118.8 hours 48 | why: holding a 119-122 range after the Oct 2 low at 117.1; a break over 122.3 clears the last two days' highs | wrong: loses today's low (~118.86) -> 2026-10-06 14:13 UTC: ORDER SOL: buy if price goes above 122.4, stop 118.8, expires in 48h
