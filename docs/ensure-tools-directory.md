# ensure-tools-directory

Find hf-espidf-project-tools in a checkout, or clone it, from a job of your own.

**File:** [`.github/actions/ensure-tools-directory/action.yml`](../.github/actions/ensure-tools-directory/action.yml)

`ru-build` runs the same script inline: a reusable workflow cannot use an action of its own repository at the
caller's ref, so `uses: ...@main` inside it would run `main`'s copy for callers pinned to `@v1`. The self-CI fails
when the two copies differ. Use the action only in jobs you write yourself.

## Usage

```yaml
steps:
  - uses: actions/checkout@v4
    with:
      submodules: recursive
  - id: tools
    uses: hardfoc/hf-espidf-ci-tools/.github/actions/ensure-tools-directory@v1
    with:
      project_dir: examples/esp32
  - run: python3 "${{ steps.tools.outputs.project_tools_path }}/generate_matrix.py" --validate
```

## Inputs and outputs

<!-- generated: inputs-ensure-tools-directory -->
| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `project_tools_dir` | no | - | Path to project tools directory (contains scripts directly). Leave empty to auto-detect. |
| `project_dir` | no | `.` | Path to the ESP-IDF project (contains CMakeLists.txt) |
| `auto_clone_tools` | no | `true` | Auto-clone tools repo if project_tools_dir is missing |

| Output | Description |
| --- | --- |
| `project_tools_path` | Resolved path to the project tools directory |
<!-- /generated -->

The search order is the one on the [ru-build](ru-build.md#finding-the-project-tools) page. The action checks that
`generate_matrix.py`, `build_app.sh` and `config_loader.sh` exist and makes them executable; it fails with a hint
when the folder is missing and cloning is not allowed.
