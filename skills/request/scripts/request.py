#!/usr/bin/env python3
"""Cross-project work requests: a mailbox outside every checkout.

  request.py send <to> <title> [--body TEXT|--body-file F] [--repro TEXT] [--hunch TEXT]
                                [--priority blocking|normal|low] [--from NAME]
  request.py inbox [--all]            requests addressed to this project
  request.py sent  [--all]            requests this project has sent
  request.py show <id>
  request.py accept  <id> [--note TEXT]
  request.py decline <id> --reason TEXT
  request.py done    <id> --ref SHA|branch|PR [--note TEXT]

Files live in $CLAUDE_REQUESTS_DIR (default ~/.claude/requests)/<to>/<id>.md.
Project identity = basename of the MAIN checkout (git --git-common-dir), so a
worktree resolves to its project. Override with --project or $CLAUDE_REQUESTS_PROJECT.
Writes are atomic (temp + rename). Ids are prefix-matchable like git SHAs.
"""
import argparse, os, re, secrets, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_REQUESTS_DIR", Path.home() / ".claude" / "requests"))
STATUSES = ("open", "accepted", "done", "declined")


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def project_name(override=None, cwd=None):
    if override:
        return override
    if os.environ.get("CLAUDE_REQUESTS_PROJECT"):
        return os.environ["CLAUDE_REQUESTS_PROJECT"]
    cwd = cwd or os.getcwd()
    try:
        common = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        return Path(common).parent.name
    except subprocess.CalledProcessError:
        return Path(cwd).name


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def parse(path: Path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"malformed request file: {path}")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, m.group(2)


def render(meta, body):
    fm = "\n".join(f"{k}: {v}" for k, v in meta.items())
    return f"---\n{fm}\n---\n{body}"


def all_requests():
    if not ROOT.exists():
        return []
    return sorted(p for p in ROOT.glob("*/*.md") if not p.name.startswith(".tmp-"))


def find(id_prefix):
    hits = [p for p in all_requests() if p.stem.startswith(id_prefix)]
    if not hits:
        raise SystemExit(f"no request matching '{id_prefix}'")
    if len(hits) > 1:
        raise SystemExit("ambiguous id, matches:\n  " + "\n  ".join(p.stem for p in hits))
    return hits[0]


def age(iso):
    try:
        delta = datetime.now(timezone.utc) - datetime.fromisoformat(iso).astimezone(timezone.utc)
    except ValueError:
        return "?"
    h = int(delta.total_seconds() // 3600)
    return f"{h}h" if h < 48 else f"{h // 24}d"


def cmd_send(a):
    me = project_name(a.frm)
    body = Path(a.body_file).read_text() if a.body_file else (a.body or "")
    if not body.strip():
        raise SystemExit("a request needs a body: what you observed and what you need (--body or --body-file)")
    rid = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{me}-{secrets.token_hex(2)}"
    meta = {"id": rid, "from": me, "to": a.to, "status": "open", "priority": a.priority,
            "created": now(), "updated": now(), "title": a.title,
            "from_path": os.getcwd(), "ref": ""}
    sections = [f"# {a.title}\n", "## Observation and goal\n", body.strip() + "\n"]
    if a.repro:
        sections += ["## Reproduce\n", a.repro.strip() + "\n"]
    if a.hunch:
        sections += ["## Requester's hunch — unverified; form your own view first\n", a.hunch.strip() + "\n"]
    sections += ["## Response\n", "_(the receiving project appends here on accept / decline / done)_\n"]
    path = ROOT / a.to / f"{rid}.md"
    atomic_write(path, render(meta, "\n".join(sections)))
    print(f"sent {rid}\n  to:   {a.to}\n  file: {path}")
    print(f"\nIf {a.to} has a live session, ping it (content stays in the file):\n"
          f"  SendMessage to '{a.to}': \"New request in your inbox: {rid} — {a.title}\"")
    print(f"Record the dependency in your own tracker: \"Waiting on {a.to} {rid}: {a.title}\"")


def list_reqs(rows, header):
    print(header)
    if not rows:
        print("  (none)")
        return
    for meta in rows:
        flag = "‼" if meta.get("priority") == "blocking" else " "
        print(f"  {flag} {meta['id']}  [{meta['status']:8s}]  {age(meta['updated'])}  "
              f"{meta['from']} → {meta['to']}  {meta['title'][:70]}")


def cmd_inbox(a):
    me = project_name(a.project)
    rows = [parse(p)[0] for p in all_requests()]
    rows = [m for m in rows if m["to"] == me and (a.all or m["status"] in ("open", "accepted"))]
    rows.sort(key=lambda m: ({"blocking": 0, "normal": 1, "low": 2}.get(m.get("priority"), 1), m["created"]))
    list_reqs(rows, f"Inbox for {me} ({len(rows)}):")


def cmd_sent(a):
    me = project_name(a.project)
    rows = [parse(p)[0] for p in all_requests()]
    rows = [m for m in rows if m["from"] == me and (a.all or m["status"] in ("open", "accepted"))]
    rows.sort(key=lambda m: m["created"])
    list_reqs(rows, f"Sent by {me} ({len(rows)}):")


def cmd_show(a):
    print(find(a.id).read_text())


def transition(a, status, line):
    path = find(a.id)
    meta, body = parse(path)
    me = project_name(a.project)
    if meta["to"] != me:
        print(f"warning: this request is addressed to {meta['to']}, you are {me}", file=sys.stderr)
    meta["status"], meta["updated"] = status, now()
    if getattr(a, "ref", None):
        meta["ref"] = a.ref
    body = body.rstrip() + f"\n\n- **{status}** {now()} by {me}: {line}\n"
    atomic_write(path, render(meta, body))
    print(f"{meta['id']} → {status}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send"); s.add_argument("to"); s.add_argument("title")
    s.add_argument("--body"); s.add_argument("--body-file"); s.add_argument("--repro"); s.add_argument("--hunch")
    s.add_argument("--priority", choices=("blocking", "normal", "low"), default="normal")
    s.add_argument("--from", dest="frm"); s.set_defaults(fn=cmd_send)
    for name, fn in (("inbox", cmd_inbox), ("sent", cmd_sent)):
        p = sub.add_parser(name); p.add_argument("--all", action="store_true"); p.add_argument("--project"); p.set_defaults(fn=fn)
    p = sub.add_parser("show"); p.add_argument("id"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("accept"); p.add_argument("id"); p.add_argument("--note", default="accepted"); p.add_argument("--project")
    p.set_defaults(fn=lambda a: transition(a, "accepted", a.note))
    p = sub.add_parser("decline"); p.add_argument("id"); p.add_argument("--reason", required=True); p.add_argument("--project")
    p.set_defaults(fn=lambda a: transition(a, "declined", a.reason))
    p = sub.add_parser("done"); p.add_argument("id"); p.add_argument("--ref", required=True); p.add_argument("--note", default="done"); p.add_argument("--project")
    p.set_defaults(fn=lambda a: transition(a, "done", f"{a.note} (ref: {a.ref})"))
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
