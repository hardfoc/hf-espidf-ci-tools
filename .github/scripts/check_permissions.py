#!/usr/bin/env python3
"""Check the permissions contract of the reusable workflows.

A called workflow that asks for a permission the caller did not grant fails
at startup (startup_failure) in every calling repository. To make that
impossible to introduce silently, the README lists exactly what each
reusable workflow needs, between the markers

    <!-- permissions-table:start -->  ...  <!-- permissions-table:end -->

as a Markdown table whose first column names the workflow file
(ru-*.yml) and whose second column lists `scope: read|write` pairs (or
`none`). This script fails when:

  * a reusable workflow sets top-level `permissions:` (they must be per job);
  * a job in a reusable workflow has no `permissions:` mapping;
  * the union of a workflow's job permissions is not exactly what the README
    row documents (more = callers break; less = the table asks too much);
  * a reusable workflow has no row, or a row names no existing workflow;
  * a caller in this repository (`uses: ./.github/workflows/ru-*.yml`)
    grants less than the documented contract.

Usage: check_permissions.py [--readme README.md] [--workflows .github/workflows]
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import yaml

LEVEL = {"none": 0, "read": 1, "write": 2}
START = "<!-- permissions-table:start -->"
END = "<!-- permissions-table:end -->"


def parse_perm_cell(cell: str) -> dict[str, str]:
    pairs = re.findall(r"([a-z][a-z-]*)\s*:\s*(read|write|none)", cell)
    return {scope: level for scope, level in pairs if level != "none"}


def parse_readme(path: str) -> dict[str, dict[str, str]]:
    text = open(path, encoding="utf-8").read()
    if START not in text or END not in text:
        raise SystemExit(f"::error file={path}::permissions table markers not found ({START} ... {END})")
    block = text.split(START, 1)[1].split(END, 1)[0]
    table: dict[str, dict[str, str]] = {}
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        m = re.search(r"(ru-[A-Za-z0-9_-]+\.ya?ml)", cells[0])
        if not m:
            continue  # header or separator row
        if m.group(1) in table:
            raise SystemExit(f"::error file={path}::{m.group(1)} is listed twice in the permissions table")
        table[m.group(1)] = parse_perm_cell(cells[1])
    return table


def as_perm_map(value, where: str, errors: list[str]) -> dict[str, str] | None:
    if value is None:
        return None
    if value == {} or value == "{}":
        return {}
    if isinstance(value, str):
        if value == "read-all":
            errors.append(f"{where}: `permissions: read-all` is too broad for a reusable workflow; list scopes")
        elif value == "write-all":
            errors.append(f"{where}: `permissions: write-all` is not allowed; list scopes")
        else:
            errors.append(f"{where}: unrecognised permissions value {value!r}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{where}: permissions must be a mapping")
        return None
    out = {}
    for scope, level in value.items():
        if level not in LEVEL:
            errors.append(f"{where}: {scope}: {level!r} is not read, write or none")
            continue
        if level != "none":
            out[str(scope)] = level
    return out


def union(maps) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in maps:
        for scope, level in m.items():
            if LEVEL[level] > LEVEL.get(out.get(scope, "none"), 0):
                out[scope] = level
    return out


def fmt(perms: dict[str, str]) -> str:
    return ", ".join(f"{k}: {v}" for k, v in sorted(perms.items())) or "none"


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--workflows", default=".github/workflows")
    args = ap.parse_args()

    errors: list[str] = []
    documented = parse_readme(args.readme)
    reusable = sorted(glob.glob(os.path.join(args.workflows, "ru-*.yml")))
    actual: dict[str, dict[str, str]] = {}

    for path in reusable:
        name = os.path.basename(path)
        doc = load(path)
        if "permissions" in doc:
            errors.append(f"{path}: top-level `permissions:` found; declare minimal permissions on each job instead")
        job_maps = []
        for job_id, job in (doc.get("jobs") or {}).items():
            where = f"{path}: job {job_id}"
            if not isinstance(job, dict) or "permissions" not in job:
                errors.append(f"{where}: no `permissions:` (use `permissions: {{}}` if it needs none)")
                continue
            perms = as_perm_map(job["permissions"], where, errors)
            if perms is not None:
                job_maps.append(perms)
        actual[name] = union(job_maps)

        if name not in documented:
            errors.append(f"{args.readme}: no permissions-table row for {name} (needs: {fmt(actual[name])})")
            continue
        want = documented[name]
        for scope, level in actual[name].items():
            if LEVEL[level] > LEVEL.get(want.get(scope, "none"), 0):
                errors.append(f"{path}: jobs ask for `{scope}: {level}` but {args.readme} documents "
                              f"`{fmt(want)}`; callers granting only what is documented would hit startup_failure")
        for scope, level in want.items():
            if LEVEL[level] > LEVEL.get(actual[name].get(scope, "none"), 0):
                errors.append(f"{args.readme}: row for {name} documents `{scope}: {level}` but the jobs only "
                              f"need `{fmt(actual[name])}`; shrink the row")

    for name in documented:
        if name not in actual:
            errors.append(f"{args.readme}: permissions-table row for {name}, which does not exist")

    # Callers inside this repository must grant at least the contract.
    for path in sorted(glob.glob(os.path.join(args.workflows, "*.yml"))):
        doc = load(path)
        top = doc.get("permissions")
        for job_id, job in (doc.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            m = re.fullmatch(r"\./\.github/workflows/(ru-[A-Za-z0-9_-]+\.ya?ml)", str(job.get("uses", "")))
            if not m or m.group(1) not in documented:
                continue
            where = f"{path}: job {job_id}"
            granted_raw = job.get("permissions", top)
            if granted_raw is None:
                print(f"::warning file={path}::{where} grants no explicit permissions; it relies on the "
                      "repository default token permissions")
                continue
            if granted_raw == "write-all":
                continue
            granted = as_perm_map(granted_raw, where, errors) or {}
            for scope, level in documented[m.group(1)].items():
                if LEVEL[level] > LEVEL.get(granted.get(scope, "none"), 0):
                    errors.append(f"{where}: calls {m.group(1)}, which needs `{scope}: {level}`, but grants "
                                  f"`{fmt(granted)}`")

    for e in errors:
        print(f"::error::{e}")
    if errors:
        print(f"{len(errors)} permissions-contract error(s)")
        return 1
    for name in sorted(actual):
        print(f"{name}: {fmt(actual[name])}")
    print("permissions contract OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
