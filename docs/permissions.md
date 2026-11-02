# Permissions contract

What each workflow needs from its caller, why a missing grant fails before any job starts, and how the contract
is kept.

## What to grant

A called workflow's jobs can use at most the permissions the calling job grants. Grant at least:

<!-- generated: permissions -->
| Workflow | Caller must grant | Why |
| --- | --- | --- |
| [`ru-build.yml`](../.github/workflows/ru-build.yml) | `contents: read`, `pull-requests: write` | checkout; firmware size comment on pull requests |
| [`ru-release-with-artifacts.yml`](../.github/workflows/ru-release-with-artifacts.yml) | `contents: write` | create the release and upload the firmware |
<!-- /generated -->

Set them on the calling job, as in the [Quickstart](quickstart.md). A top-level `permissions:` block in the
caller also works, but then every job in that file gets them.

## What happens when a grant is missing

GitHub checks the permissions before it starts the called workflow. If a job asks for more than the caller
grants, the run ends with **startup_failure**, shows no jobs and no logs, and only the run summary names the
problem. This is why the contract is part of the version: a new permission on `@v1` would break every caller at
once.

## How the contract is kept

- Every job in a `ru-*.yml` declares its own `permissions:`; a top-level block is not allowed.
- `.github/scripts/check_permissions.py` (self-CI) fails when the union of a workflow's job permissions differs
  from the table above in either direction, when a workflow has no row, or when a caller in this repository grants
  less.
- `.github/scripts/check_contract.py` fails a pull request that widens a permission without a `### Breaking`
  entry in the changelog; that change needs a new major. See [Versioning](versioning.md#what-is-breaking).

The table above is the README's, copied when the site is built, so the site and the checked table are the same.
