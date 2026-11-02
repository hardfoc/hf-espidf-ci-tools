# Quickstart

Add an ESP32 build to a repository in three files: the app list, the tools and a fifteen-line workflow.

## What the workflow expects

| File | Purpose |
| --- | --- |
| `examples/esp32/CMakeLists.txt` | The ESP-IDF project: `idf.py build` works in this folder |
| `examples/esp32/app_config.yml` | The apps to build, with the ESP-IDF versions, build types and target |
| `examples/esp32/scripts/` | [hf-espidf-project-tools](https://github.com/hardfoc/hf-espidf-project-tools) as a submodule (or let the workflow clone it) |

`examples/esp32` is the HardFOC convention and the path the matrix script looks in first; see
[The matrix](ru-build.md#the-matrix) before you put the project anywhere else.

<div class="hf-steps" markdown>

1. **Add the tools** as a submodule:

    ```bash
    git submodule add https://github.com/hardfoc/hf-espidf-project-tools.git examples/esp32/scripts
    ```

2. **List the apps** in `examples/esp32/app_config.yml`:

    ```yaml
    ---
    metadata:
      target: esp32c6
      idf_versions: ["release/v5.5"]
      build_types: [["Debug", "Release"]]
    apps:
      gpio_test:
        description: GPIO self-test
        source_file: GpioTest.cpp
    ```

3. **Call the workflow** from `.github/workflows/esp32-examples-build-ci.yml`:

    ```yaml
    ---
    name: ESP32 examples build
    on:
      push:
        branches: [main]
      pull_request:

    jobs:
      build:
        uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
        permissions:
          contents: read
          pull-requests: write
        with:
          project_dir: examples/esp32
          project_tools_dir: examples/esp32/scripts
    ```

4. **Open a pull request.** The run shows one job per app, ESP-IDF version and build type, uploads a
   `fw-<app>-<idf>-<build type>` artifact for each and comments a size table on the pull request.

</div>

!!! warning "Grant the permissions in the calling job"
    A reusable workflow cannot use more permissions than its caller grants. Without `pull-requests: write` the
    run fails before any job starts (`startup_failure`). See the [permissions contract](permissions.md).

## Add releases

To attach the firmware to a GitHub Release on every `v*` tag, add `.github/workflows/release.yml`:

```yaml
---
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  release:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-release-with-artifacts.yml@v1
    permissions:
      contents: write
    with:
      build_workflow: esp32-examples-build-ci.yml
```

The build must have run on the tagged commit first; see
[ru-release-with-artifacts](ru-release-with-artifacts.md#when-it-finds-no-firmware).

Next: [ru-build](ru-build.md), every input and what can go wrong.
