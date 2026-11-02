# ru-release-with-artifacts

Create a GitHub Release for a tag and attach the firmware that `ru-build` built and tested for the same commit.

**File:** [`.github/workflows/ru-release-with-artifacts.yml`](../.github/workflows/ru-release-with-artifacts.yml)

## Caller

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
      fail_on_no_artifacts: true
```

## Inputs

<!-- generated: inputs-ru-release-with-artifacts -->
| Input | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `build_workflow` | string | no | `esp32-examples-build-ci.yml` | Name of the ESP32 build workflow |
| `artifact_pattern` | string | no | `fw-.*` | Pattern for firmware artifacts |
| `draft` | boolean | no | `false` | Create as draft release |
| `prerelease` | boolean | no | `false` | Mark as pre-release |
| `tag_name` | string | no | `""` | Tag name for release (defaults to github.ref_name) |
| `fail_on_no_artifacts` | boolean | no | `false` | Fail if no firmware artifacts found |
<!-- /generated -->

## Jobs and permissions

One job, `release`, with `contents: write`. It checks out with full history, downloads every artifact whose
name matches `artifact_pattern` from the run of `build_workflow` on `github.sha`
(`dawidd6/action-download-artifact`), and creates the release for `tag_name` (default: the pushed tag) with
generated notes and the files attached (`softprops/action-gh-release`).

The workflow does not ask for `actions: read`: existing callers grant only `contents: write`, and the token can
read artifacts of its own repository without it.

## When it finds no firmware

The release only reuses artifacts; it never builds. It finds none when:

- the build workflow has not run on the tagged commit (tag a commit that was pushed to a branch the build runs on,
  and wait for that build to finish);
- the artifacts expired (`ru-build` keeps them 7 days);
- `build_workflow` names a different file than the caller of `ru-build`;
- `artifact_pattern` (a regular expression, default `fw-.*`) does not match.

With `fail_on_no_artifacts: false` (the default) the release is still created, without firmware, and the step
logs a warning. Set it to `true` to fail instead.

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `startup_failure` | The calling job does not grant `contents: write` | Grant it in the calling job |
| `Resource not accessible by integration` when creating the release | The repository restricts the workflow token to read | Grant `contents: write` in the caller; check **Settings > Actions > Workflow permissions** |
| Release has no files | See [above](#when-it-finds-no-firmware) | Set `fail_on_no_artifacts: true` to catch it |

Next: [ensure-tools-directory](ensure-tools-directory.md), for your own jobs that need the project tools.
