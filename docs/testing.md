# Testing and CI

How this repository checks its own workflows on every pull request, and how callers gate on them.

## Self-CI

[`ci-self.yml`](../.github/workflows/ci-self.yml) runs on every pull request, on any base branch:

| Check | Fails on |
| --- | --- |
| actionlint with shellcheck (pinned versions, SHA-256 verified) | Any finding in a workflow, including shell in `run:` blocks |
| `shellcheck_actions.py` | Any shellcheck finding in a composite action |
| `check_run_tails.py` | A `run:` block that ends in a bare `cond && cmd`, which fails the step when `cond` is false |
| `check_permissions.py` | A job permission that differs from the [permissions contract](permissions.md) |
| `gen_readme_inputs.py --check` | A README inputs table that no longer matches its workflow |
| Inlined tools step | `ru-build`'s tools-directory script differing from the composite action |
| `check_contract.py` | A removed input, a new required input, a changed type or a wider permission without a `### Breaking` changelog entry |
| `test_checks.py` | The check scripts themselves |

Run the Python checks locally:

```bash
pip install 'PyYAML==6.0.2'
python .github/scripts/check_permissions.py
python .github/scripts/gen_readme_inputs.py --check
python .github/scripts/test_checks.py
```

## Documentation and text

| Workflow | Checks |
| --- | --- |
| `ci-docs-publish.yml` | Strict site build, generated tables and figure drift, link check, Lighthouse; publishes on `main` |
| `ci-markdown-lint.yml`, `ci-yaml-lint.yml`, `ci-docs-linkcheck.yml` | Markdown style, YAML style, links in the repository's Markdown |

These call the versioned workflows of [hf-general-ci-tools](https://github.com/hardfoc/hf-general-ci-tools).
After editing a workflow's inputs, refresh both copies of its table:

```bash
python .github/scripts/gen_readme_inputs.py     # README.md
hardfoc-docs gen                                # this site
```

## Gating a caller's pull requests

A caller that wants one required status check for its branch protection adds the CI gate of hf-general-ci-tools
(`ru-ci-gate.yml`) as the last job, and requires only the gate's check:

```yaml
jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    permissions:
      contents: read
      pull-requests: write
    with:
      project_dir: examples/esp32

  ci-gate:
    name: CI gate
    needs: [build]
    if: always()
    uses: hardfoc/hf-general-ci-tools/.github/workflows/ru-ci-gate.yml@v1
    permissions:
      contents: read
    with:
      needs_json: ${{ toJSON(needs) }}
```

The gate fails when a job it waits for failed or was cancelled. `if: always()` makes it run, and report, even
then. See [ru-ci-gate](https://github.com/hardfoc/hf-general-ci-tools/blob/main/docs/ru-ci-gate.md).
