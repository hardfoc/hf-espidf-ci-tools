"""Generated regions for the workflow pages, read from the workflow files themselves.

``<!-- generated: inputs-ru-build -->`` (one per ``ru-*.yml``) is the inputs table, built by the same function that
fills the README tables (``.github/scripts/gen_readme_inputs.py``), so the site and the README cannot disagree.
``inputs-ensure-tools-directory`` is the composite action's inputs table. ``permissions`` copies the permissions
contract table from the README, which ``.github/scripts/check_permissions.py`` checks against every job.
"""

from __future__ import annotations

import importlib.util
import re

import yaml

from hardfoc_mkdocs_theme.paths import repo_root

ROOT = repo_root()


def _readme_gen():
    spec = importlib.util.spec_from_file_location("gen_readme_inputs", ROOT / ".github/scripts/gen_readme_inputs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _workflow_inputs(name: str):
    def fill() -> str:
        doc = yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8")) or {}
        return _readme_gen().table(doc)

    return fill


def _action_inputs() -> str:
    gen = _readme_gen()
    doc = yaml.safe_load((ROOT / ".github/actions/ensure-tools-directory/action.yml").read_text(encoding="utf-8"))
    rows = ["| Input | Required | Default | Description |", "| --- | --- | --- | --- |"]
    for name, spec in (doc.get("inputs") or {}).items():
        spec = spec or {}
        rows.append(f"| `{name}` | {'yes' if spec.get('required') else 'no'} | {gen.default_cell(spec)} | "
                    f"{gen.cell(spec.get('description', ''))} |")
    rows += ["", "| Output | Description |", "| --- | --- |"]
    for name, spec in (doc.get("outputs") or {}).items():
        rows.append(f"| `{name}` | {gen.cell((spec or {}).get('description', ''))} |")
    return "\n".join(rows) + "\n"


def _permissions(page) -> str:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    block = text.split("<!-- permissions-table:start -->", 1)[1].split("<!-- permissions-table:end -->", 1)[0]
    # README links point at .github/workflows/...; make them relative to the page being filled.
    return re.sub(r"\]\((\.github/[^)]+)\)", lambda m: f"]({page.rel(m.group(1))})", block.strip("\n")) + "\n"


REGIONS = {
    f"inputs-{p.stem}": _workflow_inputs(p.name) for p in sorted((ROOT / ".github/workflows").glob("ru-*.yml"))
}
REGIONS["inputs-ensure-tools-directory"] = _action_inputs
REGIONS["permissions"] = _permissions
