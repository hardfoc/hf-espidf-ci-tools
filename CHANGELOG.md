# Changelog

All notable changes to the reusable workflows in this repository are
documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and releases follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as described in [docs/versioning.md](docs/versioning.md).

A change that breaks callers pinned to the current major goes under a
`### Breaking` heading in **Unreleased**, and the next release must then be a
major bump. Breaking means: a workflow or input removed, an input's type
changed, an input or secret made required, an output removed, or a job
needing a permission it did not need before. The self-CI
(`check_contract.py`) fails a pull request that makes such a change without
that heading.

## [Unreleased]

### Changed

- Documentation moved to the HardFOC MkDocs platform: one page per workflow, inputs tables and the permissions
  contract generated from the workflow files, published with `ru-mkdocs-publish.yml`. The README follows the
  HardFOC README standard; its license badge now names the repository's real license (GPL-3.0).

## [1.1.0] - 2026-11-02

### Added

- Self-CI (`ci-self.yml`):
  - pinned actionlint and shellcheck;
  - shellcheck for the composite actions;
  - a check for `run:` blocks ending in a bare `cond && cmd`;
  - the permissions contract check and the breaking-change check;
  - a check that ru-build's inlined tools-directory step matches the action;
  - unit tests.
- README permissions table, listing exactly what each caller must grant.
- `release.yml`: on a `vX.Y.Z` tag, creates a GitHub Release with generated
  notes and moves the `vX` major tag.
- Dependabot for GitHub Actions (weekly).

### Changed

- Every third-party action is pinned to a full commit SHA with a version
  comment. `dawidd6/action-download-artifact` moves v2 → v28 and
  `softprops/action-gh-release` moves v1 → v3.0.3; the old majors used
  runtimes GitHub no longer supports.
- Permissions are declared per job. `ru-build` asks for `contents: read`
  and `pull-requests: write`, and no longer for `actions: read`.
- `ru-build.yml` runs the tools-directory logic inline instead of calling
  `ensure-tools-directory@main`. A caller pinned to `@v1` therefore runs the
  `v1` copy. The composite action stays available for direct use.

### Fixed

- `ru-build.yml` size report: `` "`size.txt missing`" `` ran a command named
  `size.txt` instead of printing the text.

## [1.0.0] - 2026-11-01

The first tagged release: the workflows as callers used them from `@main`.

### Added

- `ru-build.yml`: the ESP-IDF Docker image is pulled before the build, with
  up to 4 attempts (10/30/60 s backoff). A transient Docker Hub error no
  longer fails the build with exit 125.
- `ru-build.yml` frees runner disk space before the build.
