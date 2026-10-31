---
layout: default
title: "🛡️ Security Workflow Guide"
description: "Comprehensive security auditing for HardFOC ESP32 projects - Dependencies, secrets, and CodeQL analysis with automatic requirements discovery"
nav_order: 4
parent: "📚 Documentation"
permalink: /docs/security-workflow/
---

# Security Workflow Guide

**🛡️ Dependencies, Secrets, CodeQL**

---

The Security workflow provides comprehensive security auditing including dependency scanning, secret
detection, and optional CodeQL analysis.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔒 Security Features](#-security-features)
- [⚙️ Inputs](#-inputs)
- [📤 Outputs](#-outputs)
- [🚀 Usage Examples](#-usage-examples)
- [⚙️ Configuration](#-configuration)
- [🛡️ Security Best Practices](#-security-best-practices)
- [🔧 Troubleshooting](#-troubleshooting)
- [📚 Related Workflows](#-related-workflows)

## 🎯 Overview

**Purpose**: Comprehensive security auditing  
**Key Features**:

- **Automatic Requirements Discovery**: Finds all `requirements.txt` and `requirements.in` files automatically
- **Python dependency vulnerability scanning**: Uses pip-audit and safety
- **Secret and credential detection**: Uses gitleaks to find accidentally committed secrets
- **Optional CodeQL analysis**: Static code analysis for C/C++ and other languages
- **Configurable scan types**: Choose specific security checks to run

**Use Case**: Security compliance and vulnerability detection for mixed-language projects

## 🔒 Security Features

### Repository Security

- **Trusted Source Only**: Tools are only cloned from the trusted hardfoc/hf-espidf-project-tools repository
- **No External URLs**: Users cannot specify arbitrary repository URLs, preventing supply chain attacks
- **Main Branch Only**: Always uses the main branch for consistency and stability
- **Shallow Cloning**: Uses `--depth 1` to minimize attack surface and reduce clone time

### Input Validation

- **Path Sanitization**: All file paths are validated and sanitized
- **Parameter Validation**: Input parameters are validated before use
- **Error Handling**: Secure error messages that don't leak sensitive information

### Automatic Discovery

- **Requirements Files**: Automatically finds all `requirements*.txt` and `requirements*.in` files
- **No Manual Configuration**: Scans entire repository without user input
- **Comprehensive Coverage**: Covers all Python dependencies in the project

## ⚙️ Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_dir` | string | ✅ | - | Path to ESP-IDF project (contains CMakeLists.txt) |
| `scripts_dir` | string | ❌ | `nt-espidf-tools` | Path to nt-espidf-tools directory |
| `scan_type` | string | ❌ | `all` | `all \| dependencies \| secrets \| codeql` |
| `run_codeql` | boolean | ❌ | `true` | Enable CodeQL analysis |
| `codeql_languages` | string | ❌ | `cpp` | Comma-separated languages |
| `auto_clone_tools` | boolean | ❌ | `false` | Auto-clone tools repo if missing |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| Dependency reports | pip-audit, safety, bandit results |
| Secret detection | gitleaks, truffleHog reports |
| CodeQL analysis | Security database and SARIF files |
| Artifacts | All security reports stored |

## 🚀 Usage Examples

### Full Security Audit

```yaml
jobs:
  security:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/security.yml@v1
    with:
      project_dir: examples/esp32
      scripts_dir: nt-espidf-tools
      scan_type: "all"
      run_codeql: true
      codeql_languages: "cpp,python"
```

### Dependencies Only

```yaml
jobs:
  security:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/security.yml@v1
    with:
      project_dir: examples/esp32
      scripts_dir: nt-espidf-tools
      scan_type: "dependencies"
      run_codeql: false
```

### CodeQL with Auto-clone Tools

```yaml
jobs:
  security:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/security.yml@v1
    with:
      project_dir: examples/esp32
      scripts_dir: nt-espidf-tools
      auto_clone_tools: true
      scan_type: "codeql"
      run_codeql: true
      codeql_languages: "cpp"
```

## ⚙️ Configuration

### Scan Types

- **`all`**: Run all security checks
- **`dependencies`**: Python dependency scanning only
- **`secrets`**: Secret detection only  
- **`codeql`**: CodeQL analysis only

### CodeQL Languages

Supported languages: `cpp`, `python`, `javascript`, `go`, `java`, `csharp`

### Matrix-Based CodeQL Analysis

The workflow automatically generates the same build matrix as your build workflow and analyzes **all** build configurations:

1. **Same matrix generation**: Uses `generate_matrix.py` from your tools repo
2. **Same build process**: Calls `build_app.sh` with matrix parameters
3. **Comprehensive coverage**: Analyzes all ESP-IDF versions, build types, and targets
4. **Build consistency**: Each matrix job uses the exact same build configuration

**Matrix Parameters Used**:

- `matrix.app_name` - Application name
- `matrix.build_type` - Build type (debug/release)
- `matrix.idf_version` - ESP-IDF version
- `matrix.target` - Target chip (esp32, esp32c6, etc.)

**Example Integration**:

```yaml
# In your CI workflow, ensure consistency:
jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      scripts_dir: nt-espidf-tools
      # ... other inputs

  security:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/security.yml@v1
    with:
      project_dir: examples/esp32
      scripts_dir: nt-espidf-tools
      scan_type: "codeql"
      # CodeQL will analyze ALL matrix combinations automatically
```

## 🛡️ Security Best Practices

### For Production Environments

1. **Disable auto-clone**: Set `auto_clone_tools: false` and include tools in your repository
2. **Regular updates**: Periodically update the tools in your repository after reviewing changes
3. **Version control**: Track tool versions in your project's dependency management
4. **Code review**: Review all tool updates before applying them

### For Development Environments

1. **Enable auto-clone**: Set `auto_clone_tools: true` for convenience
2. **Monitor changes**: Keep track of tool updates and security advisories
3. **Test updates**: Verify tool updates don't break your build process
4. **Use staging**: Test changes in staging before production

### For CI/CD Pipelines

1. **Audit trail**: Log which tools version is being used
2. **Dependency scanning**: Use tools like Dependabot to monitor for vulnerabilities
3. **Access controls**: Limit who can modify the tools repository
4. **Regular updates**: Keep tools up to date with security patches

### Requirements File Management

- **Use specific versions**: Pin dependencies to specific versions in `requirements.txt`
- **Regular updates**: Update dependencies regularly and test thoroughly
- **Security scanning**: Run the security workflow regularly to catch vulnerabilities
- **Separate environments**: Use different requirements files for dev/staging/production

## 🔧 Troubleshooting

### Common Issues

**Dependency Scan Fails**

- Check Python version compatibility
- Verify requirements files exist
- Review pip installation logs

**Secret Detection Issues**

- Ensure full git history is available
- Check gitleaks installation
- Review false positive suppressions

**CodeQL Analysis Fails**

- Verify `project_dir` and `scripts_dir` are correct
- Check `build_app.sh` exists in scripts directory
- Ensure matrix generation works (same as build workflow)
- Check ESP-IDF version compatibility

### Debug Mode

Enable debug output:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

## 📚 Related Workflows

- **[Build](build-workflow.md)** - ESP-IDF application builds (uses same matrix and build process)

## 🔗 Related Resources

- [CodeQL Documentation](https://codeql.github.com/)
- [GitLeaks](https://github.com/gitleaks/gitleaks)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Safety](https://github.com/pyupio/safety)

---

[← Previous: Build Workflow](build-workflow.md) | [Next: Example Workflows →](example-workflows.md)

**📚 [All Documentation](index.md)** | **🏠 [Main README](../README.md)**

