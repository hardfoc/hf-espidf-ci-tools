# ru-build

Build every ESP32 example app of a repository across ESP-IDF versions and build types, upload the firmware and
report its size on pull requests.

**File:** [`.github/workflows/ru-build.yml`](../.github/workflows/ru-build.yml)

## Caller

```yaml
---
name: ESP32 examples build
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
    inputs:
      clean_build:
        type: boolean
        default: false

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    permissions:
      contents: read
      pull-requests: write
    with:
      project_dir: examples/esp32
      project_tools_dir: examples/esp32/scripts
      clean_build: ${{ inputs.clean_build || false }}
      max_dec_total: "0"
```

## Inputs

<!-- generated: inputs-ru-build -->
| Input | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `project_dir` | string | yes | - | Path to the ESP-IDF project (contains CMakeLists.txt) |
| `project_tools_dir` | string | no | - | Path to project tools directory (contains scripts directly). Leave empty to auto-detect. |
| `clean_build` | boolean | no | `false` | Skip caches for a clean build. |
| `auto_clone_tools` | boolean | no | `true` | Auto-clone tools repo if project_tools_dir is missing |
| `max_dec_total` | string | no | `0` | Maximum total dec size in bytes for size budget enforcement (0 to disable) |
<!-- /generated -->

## Jobs and permissions

| Job | Runs | Permissions |
| --- | --- | --- |
| `generate-matrix` | always | `contents: read` |
| `build` | once per matrix entry, `fail-fast: false`, 30 min limit | `contents: read` |
| `size-report` | pull requests only | `pull-requests: write` |

- **`generate-matrix`** checks out with submodules, finds the project tools (below), runs `generate_matrix.py`
  and outputs the matrix.
- **`build`** frees runner disk space, checks out, restores the pip cache (skipped with `clean_build`), installs
  the tools' `requirements.txt`, pulls `espressif/idf:<version>` (4 attempts, 10 / 30 / 60 s apart), runs
  `build_app.sh` inside the image with `espressif/esp-idf-ci-action` and uploads the build folder.
- **`size-report`** downloads every `fw-*` artifact, writes a size table from `size.info` / `size.txt`, comments
  it on the pull request and enforces `max_dec_total` when it is not `0`.

The caller grants the union: `contents: read` and `pull-requests: write`. See the
[permissions contract](permissions.md).

## Finding the project tools

The `generate-matrix` job needs `generate_matrix.py`, `build_app.sh` and `config_loader.sh` from
[hf-espidf-project-tools](https://github.com/hardfoc/hf-espidf-project-tools). It looks, in this order:

| Case | Path used |
| --- | --- |
| `project_tools_dir` set | That path; the job fails if it does not exist (no clone) |
| `project_tools_dir` empty and `<project_dir>/hf-espidf-project-tools` exists | That folder |
| Otherwise | `hf-espidf-project-tools` at the repository root, cloned from `main` (depth 1) when it is missing and `auto_clone_tools` is true |

A submodule is the reproducible choice: the clone follows the tools' `main` branch.

## The matrix

`generate_matrix.py` reads `app_config.yml` and emits one entry per app, ESP-IDF version and build type:

| `app_config.yml` | Effect |
| --- | --- |
| `metadata.idf_versions` | ESP-IDF branches or tags, for example `release/v5.5`; default `release/v5.5` |
| `metadata.build_types` | One list per IDF version, by index: `[["Debug", "Release"], ["Debug"]]` |
| `metadata.target` | Chip passed to the build, default `esp32c6` |
| `apps.<name>.idf_versions`, `apps.<name>.build_types` | Per-app overrides; a flat `build_types` list applies to every version |
| `apps.<name>.ci_enabled: false` | Leaves the app out of CI |
| `ci_config.exclude_combinations` | Entries whose keys all match are dropped, for example `{app_name: x, build_type: Release}` |

!!! warning "Where app_config.yml is found"
    The workflow runs `generate_matrix.py` without `--project-path`, so the script looks for
    `examples/esp32/app_config.yml` from the repository root, then for `app_config.yml` in the folder above the
    script. Keep the project in `examples/esp32`, or keep the tools inside the project folder, so both point at
    the same file.

## Artifacts

Each build uploads `<project_dir>/build*` as **`fw-<app_name>-<idf_version_docker>-<build_type>`**, for example
`fw-gpio_test-release-v5.5-Debug`, kept for 7 days. `build_app.sh` writes `size.info` and `size.txt` into the
build folder; the size report reads them. The upload runs even when the build fails, so a failed build's logs are
in the artifact.

## Size report and budget

On pull requests the `size-report` job comments a table with one row per build (app, IDF, target, build type and
the `idf.py size` summary). Set `max_dec_total` to a byte count to fail the job when any build's total `dec`
size is larger; `0` turns the check off.

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `startup_failure`, no job ran | The calling job grants less than `contents: read`, `pull-requests: write` | Add the permissions to the calling job |
| `Project tools directory not found` | `project_tools_dir` points at a missing folder, or the submodule was not added | Add the submodule, or leave `project_tools_dir` empty to clone |
| `Required script ... not found` | The tools folder is not hf-espidf-project-tools, or is an old copy | Update the submodule |
| `Configuration file not found` | No `app_config.yml` where `generate_matrix.py` looks (see the warning above) | Move the project to `examples/esp32` or the tools into the project |
| `Could not pull espressif/idf:...` after 4 attempts | Docker Hub outage, or an IDF version with no image | Check the version name; start a new run |
| `No build directory found!` | `build_app.sh` failed before creating `build*` | Read the build step log; reproduce locally with `build_app.sh` |
| Size budget exceeded | A build's `dec` total is above `max_dec_total` | Shrink the firmware or raise the budget |
| A fix here does not apply | "Re-run failed jobs" reuses the workflow revision of the first run | Start a new run (see [Versioning](versioning.md#re-runs-use-the-old-revision)) |

Next: [ru-release-with-artifacts](ru-release-with-artifacts.md), which ships these artifacts.
