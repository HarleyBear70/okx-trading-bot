"""
Write CHAT.md: the Claude chat (issue #4) newest first, so Jeff doesn't have to scroll to the bottom on GitHub.
Everyone posts with Jeff's login, so who wrote it comes from how the comment starts.

  python3 tools/chat_page.py        (needs the gh CLI; GH_TOKEN in GitHub Actions)
"""
import datetime as dt
import json
import subprocess

REPO = "HarleyBear70/okx-trading-bot"
KEEP = 30
ET = dt.timezone(dt.timedelta(hours=-4))  # US Eastern daylight time; good enough for a chat page
TERMINAL = ("From terminal Claude", "Reply from terminal Claude", "Note from terminal Claude", "Terminal Claude",
            "**From terminal Claude", "**Reply from terminal Claude", "Transcript saved", "Linux transcript")


def who(c):
    body = c["body"].lstrip()
    if c["user"]["login"].endswith("[bot]") or c["user"]["login"] == "sp12-bot":
        return "Bot"
    if c["user"]["login"] != "HarleyBear70":  # public repo: a stranger's comment is never shown as Jeff or a Claude
        return None
    if body.startswith(TERMINAL):
        return "Terminal Claude"
    if body.startswith(("From Chrome Claude", "**From Chrome Claude", "Chrome Claude")):
        return "Chrome Claude"
    return "Jeff"


def main():
    out = subprocess.run(["gh", "api", f"repos/{REPO}/issues/4/comments", "--paginate"],
                         capture_output=True, text=True, check=True).stdout
    comments = json.loads(out.replace("][", ","))
    comments = [c for c in comments if who(c)]  # strangers' comments left out (public repo)
    comments = sorted(comments, key=lambda c: c["created_at"], reverse=True)[:KEEP]
    lines = ["# Claude chat - NEWEST FIRST", "",
             f"Last {KEEP} messages from [issue #4](https://github.com/{REPO}/issues/4). "
             "Rewritten automatically every time someone posts. To reply, post on issue #4.", ""]
    for c in comments:
        t = dt.datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")).astimezone(ET)
        lines += ["---", "", f"## {who(c)} - {t:%a %b %-d, %-I:%M %p} ET", "", c["body"].strip(), ""]
    lines += ["---", "", f"Older messages: https://github.com/{REPO}/issues/4", ""]
    with open("CHAT.md", "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
