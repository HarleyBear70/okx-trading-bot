"""
Wake the Beekeeper (Jeff, Oct 7 2026: "a worker not working is money lost"). The last step of the hourly bot run.

The Beekeeper routine wakes when an issue labeled "bot-failed" is OPENED (its GitHub trigger; claude.ai routines can't
fire on "workflow run failed"). So:
  - real problem this run -> open a "bot-failed" issue (or, if one is already open, add a comment: no new wake-up
    every hour for the same trouble)
  - clean run while a "bot-failed" issue is open -> comment "back to normal" and close it
A bot sitting out by its own rules (no signal, guard, fear filter, too small, no cash) is NOT a problem.

Real problem = the bot step failed, a Python traceback, an ERROR or ATTENTION line from a LIVE (real-money) bot, or
5+ ERROR lines from any bots in one run (one or two network blips on paper/demo bots are normal and retried hourly).

  FAILED=true|false python tools/wake_beekeeper.py [bot_run.log]
"""
import json
import os
import re
import subprocess
import sys

LABEL = "bot-failed"
MANY_ERRORS = 5


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def problems(log_text, failed):
    lines = log_text.splitlines()
    errs = [x for x in lines if "ERROR" in x]
    live = [x for x in lines if "LIVE" in x and ("ERROR" in x or "ATTENTION" in x)]
    tb = [x for x in lines if x.startswith("Traceback") or re.match(r"^\w*(Error|Exception):", x)]
    why = []
    if failed:
        why.append("the bot step failed (non-zero exit)")
    if tb:
        why.append("a Python crash (traceback)")
    if live:
        why.append(f"{len(live)} problem line(s) from a REAL-MONEY bot")
    if len(errs) >= MANY_ERRORS:
        why.append(f"{len(errs)} ERROR lines in one run")
    detail = (live + tb + errs)[:25]
    return why, list(dict.fromkeys(detail))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "bot_run.log"
    text = open(path, errors="replace").read() if os.path.exists(path) else ""
    failed = os.environ.get("FAILED", "false").lower() == "true" or not text
    run_url = (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}"
               f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}")
    why, detail = problems(text, failed)
    open_issues = json.loads(gh("issue", "list", "--label", LABEL, "--state", "open", "--json", "number", "-L", "5"))

    if not why:
        for i in open_issues:
            gh("issue", "comment", str(i["number"]), "--body", f"Back to normal: this run was clean ({run_url}). Closing.")
            gh("issue", "close", str(i["number"]))
            print(f"bot-failed issue #{i['number']} closed: run is clean")
        if not open_issues:
            print("clean run: Beekeeper not needed")
        return

    body = (f"**Why:** {'; '.join(why)}.\n\n**Run:** {run_url}\n\n**Problem lines:**\n```\n"
            + "\n".join(detail or ["(no log - the bot step did not finish)"]) + "\n```\n\n"
            "Beekeeper: fix what can be fixed (no strategy, key or real-money changes), then close this issue. "
            "It also closes by itself after the next clean run.")
    if open_issues:
        n = open_issues[0]["number"]
        gh("issue", "comment", str(n), "--body", "Still a problem in the next run.\n\n" + body)
        print(f"bot-failed issue #{n} already open: added a comment")
    else:
        url = gh("issue", "create", "--label", LABEL, "--title", f"Bot run failed: {why[0]}", "--body", body).strip()
        print(f"opened {url} -> wakes the Beekeeper")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never fail the bot run because of this step
        print(f"wake_beekeeper: could not reach GitHub issues ({e})")
