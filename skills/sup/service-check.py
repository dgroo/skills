#!/usr/bin/env python3
"""Expected-services probe for /sup.

Reads .groot-project.toml in the cwd (repo root) and reports whether the
project's long-lived services are actually running. Two sources:

  1. `[[services]]` entries — each declares a long-lived service beyond the
     dev server (a compose stack, a tunnel, a daemon):

         [[services]]
         name  = "prod stack"
         check = "docker ps -q --filter name=myapp-prod | grep -q ."
         start = "make prod-up"

     `check` runs in a shell; exit 0 = up. `start` is surfaced as the
     remediation hint, never executed here.

  2. The `[dev]` table — if present and the `dev` launcher is on PATH,
     re-emits `dev status` for the project's dev server.

Prints nothing when the project declares no services (no [[services]] and no
[dev]). One line per service: `● <name> — up` / `⛔ <name> — DOWN (start: <cmd>)`.
Exit code is always 0; this is a report, not a gate.

NOTE: the checks probe processes/daemons/sockets, so /sup must run this
sandbox-disabled — inside the sandbox every service reads as down.
"""

import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # pre-3.11 python — degrade silently
    sys.exit(0)

CHECK_TIMEOUT_SECONDS = 10

toml_path = Path.cwd() / ".groot-project.toml"
if not toml_path.is_file():
    sys.exit(0)

try:
    config = tomllib.loads(toml_path.read_text())
except (OSError, tomllib.TOMLDecodeError):
    sys.exit(0)

lines = []

for service in config.get("services", []):
    name = service.get("name", "<unnamed service>")
    check = service.get("check")
    start = service.get("start")
    if not check:
        continue
    try:
        up = (
            subprocess.run(
                check,
                shell=True,
                capture_output=True,
                timeout=CHECK_TIMEOUT_SECONDS,
            ).returncode
            == 0
        )
    except subprocess.TimeoutExpired:
        up = False
    if up:
        lines.append(f"● {name} — up")
    else:
        hint = f" (start: {start})" if start else ""
        lines.append(f"⛔ {name} — DOWN{hint}")

if "dev" in config and shutil.which("dev"):
    try:
        dev_status = subprocess.run(
            ["dev", "status"],
            capture_output=True,
            text=True,
            timeout=CHECK_TIMEOUT_SECONDS,
        ).stdout.strip()
        if dev_status:
            lines.extend(dev_status.splitlines())
    except (subprocess.TimeoutExpired, OSError):
        pass

if lines:
    print("\n".join(lines))
