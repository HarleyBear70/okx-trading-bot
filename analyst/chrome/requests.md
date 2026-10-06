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
