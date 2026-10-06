"""
Chrome Claude's trade inbox (Oct 6 2026). Chrome Claude couldn't save files on GitHub, so it posts trade lines as
comments on the "Chrome Claude trades" issue instead. Runs in the hourly bot.yml, around ledger.py:

  python analyst/chrome_inbox.py pull    # new comments by the repo owner's account -> analyst/chrome/requests.md
  python analyst/ledger.py --account chrome requests
  python analyst/chrome_inbox.py reply   # results of those lines -> one reply comment on the issue

Only comments written by the repo owner's account count (Chrome Claude posts as Jeff); the bot's own replies and
anyone else's comments are ignored. A line counts when it starts with ORDER, BUY, STOP, SELL or CANCEL (a leading
"-" or "- [ ]" is fine); everything else in a comment is ignored. Uses the gh CLI (GH_TOKEN in Actions).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.path.join(HERE, "chrome")
INBOX = os.path.join(CHROME, "inbox.json")
REQUESTS = os.path.join(CHROME, "requests.md")
TITLE = "Chrome Claude trades"
ACTIONS = ("ORDER", "BUY", "STOP", "SELL", "CANCEL")
REPO = os.environ.get("GITHUB_REPOSITORY") or "HarleyBear70/okx-trading-bot"
OWNER = os.environ.get("OWNER") or REPO.split("/")[0]


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def load():
    if os.path.exists(INBOX):
        with open(INBOX) as f:
            return json.load(f)
    return {"issue": None, "last_comment_id": 0, "pending": []}


def save(st):
    with open(INBOX, "w") as f:
        json.dump(st, f, indent=1)


def issue_number(st):
    if not st["issue"]:
        found = json.loads(gh("issue", "list", "-R", REPO, "--state", "open", "--limit", "200", "--json", "number,title"))
        st["issue"] = next((i["number"] for i in found if i["title"] == TITLE), None)
    return st["issue"]


def trade_lines(body):
    out = []
    for raw in body.replace("\r", "").split("\n"):
        line = raw.strip().strip("`").strip()
        for pre in ("- [ ] ", "- [x] ", "* ", "- "):
            if line.startswith(pre):
                line = line[len(pre):].strip()
        if line.split(" ", 1)[0].upper() in ACTIONS:
            out.append(" ".join(line.split()))
    return out


def pull():
    st = load()
    num = issue_number(st)
    if not num:
        print("no open 'Chrome Claude trades' issue")
        return
    comments = json.loads(gh("api", "--paginate", f"repos/{REPO}/issues/{num}/comments?per_page=100"))
    added = []
    for c in sorted(comments, key=lambda c: c["id"]):
        if c["id"] <= st["last_comment_id"]:
            continue
        st["last_comment_id"] = c["id"]
        if c["user"]["login"] != OWNER:
            continue
        for line in trade_lines(c["body"]):
            added.append(line)
            st["pending"].append({"line": line, "comment": c["html_url"]})
    if added:
        with open(REQUESTS) as f:
            text = f.read().rstrip("\n")
        with open(REQUESTS, "w") as f:
            f.write(text + "\n" + "\n".join(f"- [ ] {x}" for x in added) + "\n")
    save(st)
    print(f"{len(added)} new trade line(s) from issue #{num}")


def reply():
    st = load()
    if not st["pending"] or not issue_number(st):
        return
    with open(REQUESTS) as f:
        done = [x for x in f.read().split("\n") if x.startswith(("- [x] ", "- [!] "))]
    results, still = [], []
    for p in st["pending"]:
        hit = next((x for x in done if x[6:].startswith(p["line"] + " -> ")), None)
        if hit:
            done.remove(hit)
            results.append(("✅ " if hit.startswith("- [x]") else "❌ ") + hit[6:])
        else:
            still.append(p)
    if results:
        gh("issue", "comment", str(st["issue"]), "-R", REPO, "--body",
           "Results from this hour's run (paper account: Chrome Claude):\n\n" + "\n".join(f"- {r}" for r in results))
    st["pending"] = still
    save(st)
    print(f"replied with {len(results)} result(s)")


if __name__ == "__main__":
    {"pull": pull, "reply": reply}[sys.argv[1]]()
