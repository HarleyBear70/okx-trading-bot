"""Fetch a YouTube video's English captions as plain text: python tools/yt_transcript.py URL OUTDIR (needs yt-dlp)."""
import glob, os, re, subprocess, sys, tempfile

url, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
tmp = tempfile.mkdtemp()
subprocess.run(["yt-dlp", "-q", "--no-warnings", "--skip-download", "--write-auto-subs", "--write-subs",
                "--sub-langs", "en", "--sub-format", "vtt", "-o", os.path.join(tmp, "%(id)s__%(title)s"), url], check=True)
files = glob.glob(os.path.join(tmp, "*.vtt"))
if not files:
    sys.exit("no English captions found")
for f in files:
    lines, last = [], None
    for l in open(f, encoding="utf-8"):
        l = re.sub(r"<[^>]+>", "", l.strip())
        if not l or "-->" in l or l.startswith(("WEBVTT", "Kind:", "Language:")) or l == last:
            continue
        if not lines or l not in lines[-1]:
            lines.append(l)
        last = l
    vid, title = os.path.basename(f).split("__", 1)
    title = title.rsplit(".en", 1)[0]
    name = re.sub(r"[^A-Za-z0-9 ]", "", title)[:60].strip() + ".txt"
    text = re.sub(r"(.{1,100})(\s|$)", r"\1\n", " ".join(lines))
    open(os.path.join(out, name), "w").write(f"{title}\nhttps://www.youtube.com/watch?v={vid}\n\n{text}")
    print(os.path.join(out, name))
