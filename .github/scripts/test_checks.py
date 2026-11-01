#!/usr/bin/env python3
"""Tests for the self-CI check scripts. Run: python .github/scripts/test_checks.py"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script: str, *args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(HERE, script), *args],
                          cwd=cwd, capture_output=True, text=True)


README = textwrap.dedent("""\
    <!-- permissions-table:start -->
    | Workflow | Caller must grant |
    |---|---|
    | `ru-x.yml` | {row} |
    <!-- permissions-table:end -->
    """)

WORKFLOW = textwrap.dedent("""\
    on: {{ workflow_call: {{}} }}
    {top}jobs:
      a:
        runs-on: ubuntu-latest
        {perms}
        steps: [{{ run: "true" }}]
    """)


class PermissionsContract(unittest.TestCase):
    def check(self, row: str, perms: str, top: str = "", caller: str | None = None) -> subprocess.CompletedProcess:
        d = tempfile.mkdtemp()
        wf = os.path.join(d, "wf")
        os.makedirs(wf)
        with open(os.path.join(d, "README.md"), "w") as fh:
            fh.write(README.format(row=row))
        with open(os.path.join(wf, "ru-x.yml"), "w") as fh:
            fh.write(WORKFLOW.format(top=top, perms=perms))
        if caller is not None:
            with open(os.path.join(wf, "ci-x.yml"), "w") as fh:
                fh.write(caller)
        return run("check_permissions.py", "--readme", os.path.join(d, "README.md"), "--workflows", wf)

    def test_match_passes(self):
        r = self.check("`contents: read`", "permissions: { contents: read }")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_job_asks_more_than_documented_fails(self):
        r = self.check("`contents: read`", "permissions: { contents: read, pull-requests: write }")
        self.assertEqual(r.returncode, 1)
        self.assertIn("startup_failure", r.stdout)

    def test_documented_more_than_needed_fails(self):
        r = self.check("`contents: write`", "permissions: { contents: read }")
        self.assertEqual(r.returncode, 1)
        self.assertIn("shrink the row", r.stdout)

    def test_missing_job_permissions_fails(self):
        r = self.check("`contents: read`", "")
        self.assertEqual(r.returncode, 1)

    def test_top_level_permissions_fails(self):
        r = self.check("`contents: read`", "permissions: { contents: read }", top="permissions: { contents: read }\n")
        self.assertEqual(r.returncode, 1)

    def test_empty_permissions_is_none(self):
        r = self.check("none", "permissions: {}")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_local_caller_granting_too_little_fails(self):
        caller = "on: push\npermissions: { contents: read }\njobs:\n  c:\n    uses: ./.github/workflows/ru-x.yml\n"
        r = self.check("`contents: write`", "permissions: { contents: write }", caller=caller)
        self.assertEqual(r.returncode, 1)
        self.assertIn("grants", r.stdout)


class RunTails(unittest.TestCase):
    def check(self, script: str) -> subprocess.CompletedProcess:
        d = tempfile.mkdtemp()
        p = os.path.join(d, "w.yml")
        with open(p, "w") as fh:
            fh.write("jobs:\n  a:\n    steps:\n      - run: |\n" + textwrap.indent(script, " " * 10))
        return run("check_run_tails.py", p)

    def test_bare_and_list_at_end_fails(self):
        self.assertEqual(self.check('echo a\n[ -n "$X" ] && echo set\n').returncode, 1)

    def test_and_list_with_or_passes(self):
        self.assertEqual(self.check('[ -n "$X" ] && echo set || true\n').returncode, 0)

    def test_and_list_not_last_passes(self):
        self.assertEqual(self.check('[ -n "$X" ] && echo set\necho done\n').returncode, 0)

    def test_if_block_passes(self):
        self.assertEqual(self.check('if [ -n "$X" ]; then\n  echo set\nfi\n').returncode, 0)


if __name__ == "__main__":
    unittest.main()
