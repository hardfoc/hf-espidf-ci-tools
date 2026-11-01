#!/usr/bin/env python3
"""Generate the per-workflow inputs tables in README.md from the ru-*.yml files.

Each table lives between `<!-- inputs:ru-NAME.yml:start -->` and
`<!-- inputs:ru-NAME.yml:end -->`. With --check, nothing is written and the
script fails if any table is out of date (the self-CI runs this), so the
README cannot drift from the workflows.

Usage: gen_readme_inputs.py [--check] [--readme README.md] [--workflows .github/workflows]
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import yaml


def cell(value) -> str:
    text = " ".join(str(value).split())
    return text.replace("|", "\\|")


def default_cell(spec: dict) -> str:
    if "default" not in spec:
        return "-"
    d = spec["default"]
    if isinstance(d, bool):
        d = "true" if d else "false"
    d = str(d)
    return f"`{cell(d)}`" if d != "" else '`""`'


def table(doc: dict) -> str:
    on = doc.get(True, doc.get("on")) or {}
    inputs = ((on.get("workflow_call") or {}).get("inputs")) or {}
    if not inputs:
        return "_No inputs._\n"
    rows = ["| Input | Type | Required | Default | Description |", "| --- | --- | --- | --- | --- |"]
    for name, spec in inputs.items():
        spec = spec or {}
        rows.append(f"| `{name}` | {spec.get('type', '')} | {'yes' if spec.get('required') else 'no'} | "
                    f"{default_cell(spec)} | {cell(spec.get('description', ''))} |")
    return "\n".join(rows) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--workflows", default=".github/workflows")
    args = ap.parse_args()

    text = open(args.readme, encoding="utf-8").read()
    new = text
    stale = []
    for path in sorted(glob.glob(os.path.join(args.workflows, "ru-*.yml"))):
        name = os.path.basename(path)
        start, end = f"<!-- inputs:{name}:start -->", f"<!-- inputs:{name}:end -->"
        if start not in new:
            stale.append(f"{name}: no inputs table in {args.readme} (add {start} ... {end})")
            continue
        with open(path, encoding="utf-8") as fh:
            body = table(yaml.safe_load(fh) or {})
        pattern = re.compile(re.escape(start) + r"\n.*?" + re.escape(end), re.S)
        replacement = f"{start}\n{body}{end}"
        current = pattern.search(new)
        if current and current.group(0) != replacement:
            stale.append(f"{name}: inputs table is out of date")
        new = pattern.sub(lambda _m: replacement, new)

    if args.check:
        for s in stale:
            print(f"::error file={args.readme}::{s}; run python .github/scripts/gen_readme_inputs.py")
        if stale:
            return 1
        print("README inputs tables are up to date")
        return 0
    if new != text:
        with open(args.readme, "w", encoding="utf-8") as fh:
            fh.write(new)
    for s in stale:
        if "no inputs table" in s:
            print(f"warning: {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
