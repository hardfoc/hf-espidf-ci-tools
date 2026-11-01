#!/usr/bin/env python3
"""Run shellcheck on the bash `run:` steps of composite actions.

actionlint checks workflows only, not action.yml files. This extracts each
bash run step, replaces any remaining ${{ ... }} expression with a plain
placeholder word, and runs shellcheck on it. Any finding fails.

Usage: shellcheck_actions.py ACTION_YML...
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

import yaml


def main(paths: list[str]) -> int:
    failed = 0
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        for i, step in enumerate((doc.get("runs") or {}).get("steps") or []):
            if not isinstance(step, dict) or "run" not in step or step.get("shell", "bash") not in ("bash", "sh"):
                continue
            script = re.sub(r"\$\{\{.*?\}\}", "GITHUB_EXPRESSION", str(step["run"]))
            name = step.get("name") or step.get("id") or f"step {i}"
            with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as tmp:
                tmp.write("#!/usr/bin/env bash\n" + script)
            r = subprocess.run(["shellcheck", "--format=gcc", tmp.name], capture_output=True, text=True)
            os.unlink(tmp.name)
            if r.returncode != 0:
                failed += 1
                for line in r.stdout.splitlines():
                    print(f"::error file={path}::{name}: {line.split(':', 1)[1] if ':' in line else line}")
    if failed:
        print(f"shellcheck findings in {failed} composite action step(s)")
        return 1
    print(f"shellcheck clean: {len(paths)} composite action file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
