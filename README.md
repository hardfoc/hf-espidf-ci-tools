---
layout: default
title: "🔧 HardFOC ESP32 CI Tools"
description: "Advanced CI/CD Tools for HardFOC ESP32 Projects - Comprehensive GitHub Actions workflows for ESP-IDF development with matrix builds, security auditing, and automated documentation"
nav_order: 1
permalink: /
---

# 🔧 HardFOC ESP32 CI Tools

**🚀 Advanced CI/CD Tools for HardFOC ESP32 Projects**

---

[![ESP-IDF](https://img.shields.io/badge/ESP--IDF-Matrix%20Builds-green?logo=espressif)](https://docs.espressif.com/projects/esp-idf/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://hardfoc.github.io/hf-espidf-ci-tools)


*Comprehensive GitHub Actions workflows for ESP-IDF development with matrix builds, security auditing, and automated documentation*

---

## 📚 Documentation

**🌐 [Live Documentation Site](https://hardfoc.github.io/hf-espidf-ci-tools/)**  
*Published documentation with enhanced navigation and search*

| Workflow | Purpose | Key Features | Documentation |
|----------|---------|--------------|---------------|
| **🏗️ Build** | Matrix ESP-IDF builds | Parallel builds, caching, size reports | [Build Guide](docs/build-workflow.md) |
| **🛡️ Security** | Security auditing | CodeQL, dependency scan, secrets | [Security Guide](docs/security-workflow.md) |
| **📦 Release** | Firmware releases with artifacts | Auto artifacts, ESP32 binaries, GitHub releases | [Release Guide](docs/release-workflow.md) |

📖 **Start here**: [Documentation Index](docs/index.md) - Complete guide with examples and navigation  
🚀 **Examples**: [Example Workflows](docs/example-workflows.md) - Ready-to-use workflow templates

---

## 🏷️ Versioning

Pin the moving major tag: `uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1`.
Releases are semver tags (`v1.0.0`, ...). `v1` always points at the newest
`v1.x.y`. Breaking changes only arrive with a new major. See
[docs/VERSIONING.md](docs/VERSIONING.md) and [CHANGELOG.md](CHANGELOG.md).

> After a fix lands here, start a **new** run. "Re-run failed jobs" reuses the
> reusable-workflow revision that the original run resolved.

---

## 🔐 Permissions Contract

Each reusable workflow declares minimal `permissions` on every job. A called
workflow cannot ask for more than its caller grants: if it does, the run
fails before any job starts (`startup_failure`). Grant **at least** the
following on the calling job, or at the top of the calling workflow. The
self-CI (`.github/scripts/check_permissions.py`) fails if a workflow's job
permissions ever differ from this table.

<!-- permissions-table:start -->
| Workflow | Caller must grant | Why |
|----------|-------------------|-----|
| [`ru-build.yml`](.github/workflows/ru-build.yml) | `contents: read`, `pull-requests: write` | checkout; firmware size comment on pull requests |
| [`ru-release-with-artifacts.yml`](.github/workflows/ru-release-with-artifacts.yml) | `contents: write` | create the release and upload the firmware |
<!-- permissions-table:end -->

---

## 🎯 What This Repository Provides

### **Reusable GitHub Actions Workflows**

- ✅ **Matrix-based ESP-IDF builds** across multiple versions and configurations
- ✅ **Comprehensive security auditing** with CodeQL and dependency scanning

### **Smart Project Tools Integration**

- ✅ **Single composite action** for project tools directory management
- ✅ **Automatic tool cloning** with security validation
- ✅ **Dynamic matrix generation** from project configuration
- ✅ **Intelligent caching** for faster builds

### **HardFOC Project Support**

- ✅ **ESP32-C6 optimized** for HardFOC interface projects
- ✅ **Multi-application support** with YAML configuration
- ✅ **Parallel execution** for maximum CI efficiency
- ✅ **Comprehensive documentation** with examples and troubleshooting

---

## 🚀 Quick Start

### **1. Basic Usage**

```yaml
# .github/workflows/ci.yml
name: ESP32 CI

on: [push, pull_request]

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
```

### **2. Advanced Parallel Workflow**

```yaml
name: 🚀 Advanced ESP32 CI

on: [push, pull_request]

jobs:
  # Build firmware across multiple configurations
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32

  # Security audit
  security:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/security.yml@v1
    with:
      project_dir: examples/esp32
      scan_type: "all"
      run_codeql: true

  # Release with firmware artifacts (on tags)
  release:
    if: startsWith(github.ref, 'refs/tags/')
    needs: [build]
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-release-with-artifacts.yml@v1
    with:
      build_workflow: "esp32-examples-build-ci.yml"
      artifact_pattern: "fw-.*"
    permissions:
      contents: write
```

### **3. Complete Examples**

For comprehensive examples including development, release, and security-focused workflows, see [**Example Workflows**](docs/example-workflows.md).

### Consumer usage (examples)

CI combining build + security:

```yaml
name: CI
on:
  push: { branches: [ main ] }
  pull_request: { branches: [ main ] }

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32   # Change to where your esp32 project directory is
      project_tools_dir: hf-espidf-project-tools  
      auto_clone_tools: true
      clean_build: false

  security:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/security.yml@v1
    with:
      project_dir: examples/esp32
      project_tools_dir: hf-espidf-project-tools
      scan_type: "all"
      run_codeql: true
      codeql_languages: "cpp"
```

---

📖 **Next**: [Documentation Index](docs/index.md) - Complete navigation and examples
