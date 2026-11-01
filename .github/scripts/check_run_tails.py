#!/usr/bin/env python3
"""Fail if a shell `run:` block ends with a bare `cond && cmd` line.

GitHub runs bash with `-e`, and the exit status of a script is that of its
last command. A last line such as `[ -n "$X" ] && echo "..."` therefore
fails the step whenever the condition is false, even though `-e` ignores the
same line anywhere else. actionlint and shellcheck do not report this.

Usage: check_run_tails.py FILE...   (workflow files or composite action.yml)
"""

from __future__ import annotations

import re
import sys

import yaml

SHELLS = {None, "bash", "sh"}


def steps_of(doc: dict):
    if isinstance(doc.get("runs"), dict):  # composite action
        for step in doc["runs"].get("steps") or []:
            yield "runs", step
        return
    for job_id, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        default_shell = ((job.get("defaults") or {}).get("run") or {}).get("shell")
        for step in job.get("steps") or []:
            if isinstance(step, dict) and default_shell and "shell" not in step:
                step = {**step, "shell": default_shell}
            yield job_id, step


def last_command(script: str) -> str | None:
    lines = [ln.strip() for ln in script.splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith("#")]
    return lines[-1] if lines else None


def bad_tail(line: str) -> bool:
    if "&&" not in line or "||" in line or line.endswith("\\"):
        return False
    # `fi`, `done`, `esac`, `}` end compound commands and are fine.
    return not re.fullmatch(r"(fi|done|esac|\}|\))", line)


def main(paths: list[str]) -> int:
    failures = 0
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        for where, step in steps_of(doc):
            if not isinstance(step, dict) or "run" not in step:
                continue
            shell = step.get("shell")
            shell_name = shell.split()[0] if isinstance(shell, str) else None
            if shell_name not in SHELLS:
                continue
            line = last_command(str(step["run"]))
            if line and bad_tail(line):
                name = step.get("name") or step.get("id") or "(unnamed step)"
                print(f"::error file={path}::{where} / {name}: last line `{line}` exits 1 when its condition "
                      "is false; use an `if ...; then ...; fi` block or append `|| true`")
                failures += 1
    if failures:
        print(f"{failures} run block(s) end with a bare `&&` list")
        return 1
    print(f"checked {len(paths)} file(s): no run block ends with a bare `&&` list")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
