# Migrating to v1

Move a caller from `@main` (or an older copy of these workflows) to the versioned `@v1`.

## Steps

<div class="hf-steps" markdown>

1. **Change the ref** in every `uses:` line:

    ```yaml
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    ```

2. **Grant the contract** on the calling job: `contents: read` and `pull-requests: write` for `ru-build`,
   `contents: write` for `ru-release-with-artifacts`. `ru-build` no longer needs `actions: read`; you can remove
   it.

3. **Remove callers of workflows that do not exist.** Older documentation showed a `security.yml` reusable
   workflow; there has never been one in this repository. Use the C++ analysis workflows of
   [hf-general-ci-tools](https://github.com/hardfoc/hf-general-ci-tools) instead.

4. **Drop references to the composite action at `@main`** in your own jobs; pin it to `@v1` too.

5. **Start a new run** after the change. "Re-run failed jobs" keeps the old workflow revision.

</div>

## What changed for callers in v1

| Before | In v1 |
| --- | --- |
| Actions pinned to tags, some on runtimes GitHub no longer runs | Every action pinned to a commit SHA |
| `ru-build` asked for `actions: read` | `contents: read`, `pull-requests: write` only |
| `ru-build` called `ensure-tools-directory@main` | The script is inlined, so `@v1` runs the `v1` copy |
| A Docker Hub error failed the build with exit 125 | The image is pulled up to four times first |
| The size report ran a command named `size.txt` when the file was missing | It prints the message |

No input was removed or made required, so a caller that worked on `@main` works on `@v1` once it grants the
permissions above. The full list is in the [changelog](changelog.md).
