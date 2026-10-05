# Ideas folder

Two kinds of things live here:

- IDEAS.md: the running list of ideas not yet tested (or waiting on Jeff), with status.
- Any `*.py` file that defines `run()` returning a list of Markdown lines. The weekly Scout
  (research/scout.py) runs each one and puts its output in reports/weekly-YYYY-MM-DD.md. These are
  quick looks only. Anything promising still needs a plan-first backtest before a bot trades it.
  Idea scripts must not place orders or edit bot.py; they get public market data only.
