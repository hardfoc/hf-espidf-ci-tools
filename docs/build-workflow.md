---
layout: default
title: "🏗️ ESP-IDF Build Workflow Guide"
description: "Advanced ESP32 Build System for HardFOC Projects - Matrix-based building across multiple ESP-IDF versions, build types, and applications with intelligent caching and artifact management"
nav_order: 3
parent: "📚 Documentation"
permalink: /docs/build-workflow/
---

# 🏗️ ESP-IDF Build Workflow Guide

[![Build](https://img.shields.io/badge/Build-Matrix%20ESP--IDF-blue?logo=espressif)](https://docs.espressif.com/projects/esp-idf/)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange?logo=github)
![Matrix](https://img.shields.io/badge/Matrix-Parallel%20Builds-green?logo=matrix)

**🚀 Advanced ESP32 Build System for HardFOC Projects**

*Matrix-based building across multiple ESP-IDF versions, build types, and applications with
intelligent caching and artifact management*

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [⚙️ Inputs & Configuration](#-inputs--configuration)
- [📤 Outputs & Artifacts](#-outputs--artifacts)
- [🚀 Usage Examples](#-usage-examples)
- [🔧 Configuration](#-configuration)
- [🏗️ Build Process](#-build-process)
- [🔍 Troubleshooting](#-troubleshooting)
- [📚 Related Documentation](#-related-documentation)

---

## 🎯 Overview

### **Purpose**

The ESP-IDF Build workflow provides **matrix-based building** across multiple ESP-IDF versions,
build types, and applications with intelligent caching and artifact management for HardFOC ESP32
projects.

### **Key Features**

- 🔄 **Dynamic Matrix Generation** - From your project's `app_config.yml` configuration
- 🚀 **Parallel Execution** - Multiple builds run simultaneously for maximum efficiency
- 💾 **Intelligent Caching** - pip and ccache optimization for faster builds
- 📦 **Artifact Management** - Automatic upload and organization of build outputs
- 🛡️ **ESP-IDF Environment** - Official Espressif actions for reliable builds
- 📊 **Size Reporting** - Automatic PR comments with firmware size analysis
- 🔧 **Project Tools Integration** - Seamless integration with HardFOC project tools
- 🔒 **Secure Tool Management** - Automatic tool cloning from trusted repository with validation

### **Use Cases**

- ✅ **CI/CD for ESP32 applications** requiring multiple build configurations
- ✅ **Multi-version testing** across different ESP-IDF releases
- ✅ **Parallel builds** for faster development cycles
- ✅ **Automated artifact management** for releases and testing
- ✅ **Size optimization tracking** with PR integration

---

## ⚙️ Inputs & Configuration

### **Required Inputs**

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `project_dir` | string | ✅ | Path to ESP-IDF project (contains `CMakeLists.txt`, `app_config.yml`) |

### **Optional Inputs**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `project_tools_dir` | string | Auto-detect | Path to project tools directory (contains scripts directly). Leave empty to auto-detect. |
| `clean_build` | boolean | `false` | Skip caches for a clean build |
| `auto_clone_tools` | boolean | `true` | Auto-clone tools repo if project_tools_dir is missing |
| `max_dec_total` | string | `"0"` | Maximum total dec size in bytes for size budget enforcement (0 to disable) |

### **Path Configuration**

**Important:** All paths are resolved relative to the repository root where the workflow runs.

### **Secure Tool Management**

The workflow includes a built-in `ensure-tools-directory` action that provides:

- **🔒 Trusted Source Only**: Only clones from the verified `hardfoc/hf-espidf-project-tools` repository
- **🛡️ Security Validation**: Validates submodule URLs and ensures scripts are from trusted sources
- **⚡ Automatic Resolution**: Intelligently detects and resolves tool directory paths
- **🔧 Script Validation**: Ensures all required scripts exist and are executable
- **📁 Flexible Setup**: Supports submodules, direct clones, and custom tool locations
- **🔄 Multi-Project Support**: Tools can be shared across multiple projects since all scripts accept `--project-path` argument

### **Size Budget Enforcement**

The workflow includes optional size budget enforcement to prevent firmware from exceeding specified limits:

- **📊 Automatic Size Analysis**: Analyzes firmware size from all build configurations
- **🚫 Budget Enforcement**: Fails the build if any configuration exceeds the specified limit
- **⚙️ Configurable Limits**: Set custom size limits via `max_dec_total` parameter
- **🔍 Detailed Reporting**: Shows which builds exceeded limits and by how much
- **✅ Optional Feature**: Disabled by default (set to "0"), enable by setting a positive value

#### **What the Size Budget Measures**

The size budget is based on the **`dec` (decimal) size** from ESP-IDF's size analysis, which
represents the **total memory footprint** of your firmware. This includes:

- **📝 Text Segment**: Executable code, functions, and program logic
- **📊 Data Segment**: Initialized global and static variables
- **🗃️ BSS Segment**: Uninitialized global and static variables (zero-initialized)

**Size Analysis Format:**

```
text    data     bss     dec     hex filename
12345   6789     1234   20368   4f90 your_app.bin
```

Where:

- **`text`**: Code size (instructions, functions, constants)
- **`data`**: Initialized variables (global/static with initial values)
- **`bss`**: Uninitialized variables (global/static set to zero)
- **`dec`**: **Total size** = text + data + bss (this is what the budget measures)
- **`hex`**: Same as dec but in hexadecimal format

**Why Use `dec` Size:**

- **🎯 Total Memory Usage**: Represents the complete RAM footprint
- **📱 Device Constraints**: ESP32 devices have limited flash and RAM
- **⚖️ Resource Management**: Helps ensure firmware fits within device capabilities
- **🔍 Build Comparison**: Consistent metric across different build configurations

#### **Common Size Budget Values**

| Device | Typical Budget | Description |
|--------|----------------|-------------|
| **ESP32** | `1,600,000` bytes (1.6MB) | Standard ESP32 with 4MB flash |
| **ESP32-S2** | `1,600,000` bytes (1.6MB) | ESP32-S2 with 4MB flash |
| **ESP32-S3** | `1,600,000` bytes (1.6MB) | ESP32-S3 with 4MB flash |
| **ESP32-C3** | `1,600,000` bytes (1.6MB) | ESP32-C3 with 4MB flash |
| **ESP32-C6** | `1,600,000` bytes (1.6MB) | ESP32-C6 with 4MB flash |
| **Small Flash** | `800,000` bytes (800KB) | ESP32 with 2MB flash |
| **Large Flash** | `3,200,000` bytes (3.2MB) | ESP32 with 8MB+ flash |

**Size Budget Guidelines:**

- **🟢 Conservative**: 50-60% of available flash (leaves room for OTA updates)
- **🟡 Moderate**: 70-80% of available flash (good balance)
- **🔴 Aggressive**: 90%+ of available flash (minimal room for updates)

**Example Size Analysis:**

```
text    data     bss     dec     hex filename
456789  12345    8901   477035  746ab my_app.bin
```

- **Total Size**: 477,035 bytes (~466 KB)
- **Status**: ✅ Within 1.6MB budget
- **Remaining**: 1,122,965 bytes available

#### **How Size Budget Enforcement Works**

The workflow analyzes the `size.txt` files generated by ESP-IDF for each build configuration:

1. **📊 Size Analysis**: Parses the `dec` value from each `size.txt` file
2. **🔍 Comparison**: Compares each build's size against the `max_dec_total` limit
3. **⚠️ Violation Detection**: Identifies builds that exceed the budget
4. **📝 Error Reporting**: Reports specific builds and their sizes
5. **🚫 Build Failure**: Fails the entire workflow if any build exceeds the limit

**Error Example:**

```
::error file=build-app-gpio_test-type-Release-target-esp32c6-idf-release_v5_5/size.txt::build-app-gpio_test-type-Release-target-esp32c6-idf-release_v5_5 dec=1800000 exceeds MAX_DEC_TOTAL=1600000
::error::Size budget exceeded in 1 build(s). Check individual errors above.
```

**Success Example:**

```
✅ All builds within size budget (1600000 bytes)
```

#### **Project Directory (`project_dir`)**

- **Purpose**: Points to your ESP-IDF project directory (contains `CMakeLists.txt`, `app_config.yml`)
- **Examples**:
  - `examples/esp32` (most common)
  - `firmware/esp32-project`
  - `src/esp32-app`

#### **Tools Directory (`project_tools_dir`)**

- **Purpose**: Points to directory containing the build scripts (`build_app.sh`, `generate_matrix.py`, etc.)
- **Auto-detection**: If not specified, looks for `hf-espidf-project-tools` subdirectory in project directory
- **Multi-Project Support**: Can be shared across multiple projects since all scripts accept `--project-path` argument
- **Examples**:
  - `examples/esp32/scripts` (when using submodule)
  - `examples/esp32/hf-espidf-project-tools` (when cloned directly)
  - `tools/esp32-build-scripts` (custom location)
  - `shared-tools` (shared across multiple projects)

#### **Common Configuration Patterns**

**Pattern 1: Submodule Setup (Recommended)**

```yaml
# Repository structure:
# your-repo/
# ├── examples/esp32/           # ESP-IDF project
# │   ├── CMakeLists.txt
# │   ├── app_config.yml
# │   └── hf-espidf-project-tools/  # Submodule containing project tools
# │       ├── build_app.sh
# │       └── generate_matrix.py

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      project_tools_dir: examples/esp32/hf-espidf-project-tools  # Points to submodule
      # auto_clone_tools not needed - workflow respects explicit project_tools_dir
```

**✅ Automatic Behavior:**

- When `project_tools_dir` is specified, the workflow uses that path directly
- No auto-cloning occurs when explicit path is provided
- Submodule detection and validation happens automatically

**Pattern 2: Direct Clone Setup**

```yaml
# Repository structure:
# your-repo/
# ├── examples/esp32/           # ESP-IDF project
# │   ├── CMakeLists.txt
# │   ├── app_config.yml
# │   └── hf-espidf-project-tools/  # Cloned directly
# │       ├── build_app.sh
# │       └── generate_matrix.py

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      # project_tools_dir not needed - auto-detects hf-espidf-project-tools
```

**Pattern 3: Custom Tools Location**

```yaml
# Repository structure:
# your-repo/
# ├── firmware/esp32/           # ESP-IDF project
# │   ├── CMakeLists.txt
# │   └── app_config.yml
# └── build-tools/              # Custom tools location
#     ├── build_app.sh
#     └── generate_matrix.py

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: firmware/esp32
      project_tools_dir: build-tools
```

**Pattern 4: Shared Tools for Multiple Projects**

```yaml
# Repository structure:
# your-repo/
# ├── projects/
# │   ├── project-a/            # ESP-IDF project A
# │   │   ├── CMakeLists.txt
# │   │   └── app_config.yml
# │   └── project-b/            # ESP-IDF project B
# │       ├── CMakeLists.txt
# │       └── app_config.yml
# └── shared-tools/             # Shared tools directory
#     ├── build_app.sh
#     └── generate_matrix.py
#
jobs:
  build-project-a:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: projects/project-a
      project_tools_dir: shared-tools  # Shared across all projects
      
  build-project-b:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: projects/project-b
      project_tools_dir: shared-tools  # Same shared tools directory
```

**✅ Why This Works:**

- All scripts (`build_app.sh`, `generate_matrix.py`, etc.) accept `--project-path` argument
- The workflow automatically passes the correct project directory to each script
- Tools can be shared across multiple projects without duplication
- Each project maintains its own `app_config.yml` and build configuration

---

## 📤 Outputs & Artifacts

### **Workflow Outputs**

| Output | Description |
|--------|-------------|
| `matrix` | JSON matrix from `generate_matrix.py` with all build combinations |
| `project_tools_path` | Resolved path to project tools directory (from generate-matrix job) |

### **Build Artifacts**

| Artifact | Description | Retention | Location |
|----------|-------------|-----------|----------|
| `fw-{app}-{version}-{build}` | Complete build directory with all outputs | 7 days | Root artifact |
| `size.txt` | Human-readable firmware size analysis | 7 days | Inside build directory |
| `size.json` | Machine-readable size data (JSON format) | 7 days | Inside build directory |
| `size.info` | Build metadata for PR reporting | 7 days | Inside build directory |
| `size.meta` | Additional metadata (ELF/MAP file paths) | 7 days | Inside build directory |
| `*.bin` | Firmware binary files | 7 days | Inside build directory |
| `*.elf` | ELF executable files | 7 days | Inside build directory |

**Artifact Structure:**

```
fw-gpio_test-release_v5_5-Release/
└── build-app-gpio_test-type-Release-target-esp32c6-idf-release_v5_5/  # ESP-IDF build directory
    ├── size.txt                      # Size analysis
    ├── size.json                     # JSON size data
    ├── size.info                     # PR metadata
    ├── size.meta                     # Additional metadata
    ├── gpio_test.bin                 # Firmware binary
    ├── gpio_test.elf                 # ELF file
    └── ...                           # Other build outputs
```

**Build Directory Naming:**
The build directory follows the pattern: `build-app-{app_type}-type-{build_type}-target-{target}-idf-{idf_version}`

Examples:

- `build-app-gpio_test-type-Release-target-esp32c6-idf-release_v5_5`
- `build-app-adc_test-type-Debug-target-esp32c6-idf-release_v5_4`

### **PR Integration**

- 📊 **Automatic Size Reports** - PR comments with firmware size analysis
- 📈 **Size Budget Enforcement** - Optional size limit checking with configurable limits
- 🔍 **Build Status** - Clear success/failure indicators
- ⚠️ **Budget Violations** - Detailed error reporting when size limits are exceeded

---

## 🚀 Usage Examples

### **Basic Usage**

```yaml
name: Build ESP32 Firmware

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
```

### **Advanced Configuration**

```yaml
name: Advanced ESP32 Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      clean_build:
        description: 'Clean build (no cache)'
        required: false
        default: false
        type: boolean

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      project_tools_dir: hf-espidf-project-tools
      clean_build: ${{ github.event.inputs.clean_build == 'true' }}
      auto_clone_tools: true
```

### **Clean Build (No Caching)**

```yaml
jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      clean_build: true  # Skip all caches for fresh build
```

### **Custom Tools Directory**

```yaml
jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      project_tools_dir: custom-tools  # Use custom tools directory
      auto_clone_tools: false  # Don't auto-clone, use existing
```

### **Size Budget Enforcement**

```yaml
jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      max_dec_total: "1600000"  # 1.6MB size limit (in bytes)
```

### **Advanced Configuration with Size Budget**

```yaml
name: ESP32 Build with Size Budget

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      size_limit:
        description: 'Size limit in MB'
        required: false
        default: '1.6'
        type: string

jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      project_tools_dir: hf-espidf-project-tools
      clean_build: false
      max_dec_total: ${% raw %}{{ github.event.inputs.size_limit != '' && format('{0}{1}', github.event.inputs.size_limit, '000000') || '1600000' }}{% endraw %}
```

---

## 🔧 Configuration

### **Project Structure Requirements**

Your ESP32 project must have this structure:

```
your-project/
├── examples/
│   └── esp32/                    # ESP-IDF project directory
│       ├── CMakeLists.txt        # Project-level CMakeLists.txt
│       ├── app_config.yml        # Build configuration
│       ├── main/                 # Application source code
│       │   ├── AppTest1.cpp      # An independent application that we can build target for
│       │   ├── AppTest2.cpp      # An independent application that we can build target for
│       │   └── CMakeLists.txt    # Component-level CMakeLists.txt
│       ├── components/           # Custom components
│       └── hf-espidf-project-tools/  # Project tools (submodule)
│           ├── generate_matrix.py    # Matrix generator
│           ├── build_app.sh          # Application builder
│           ├── config_loader.sh      # Configuration loader
│           └── requirements.txt      # Python dependencies
```

### **How the CI System Works with app_config.yml**

The CI scripts are designed to capitalize on the `app_config.yml` configuration and the
`hf-espidf-project-tools` submodule to enable **parallel building** of multiple applications.
Here's how it works:

#### **1. Configuration-Driven Matrix Generation**

The `app_config.yml` file defines all available applications and their build configurations:

```yaml
# app_config.yml example
version: "1.0"
metadata:
  project: "ESP32 HardFOC Interface Wrapper"
  default_app: "ascii_art"
  target: "esp32c6"
  idf_versions: ["release/v5.5", "release/v5.4"]
  build_types: [["Debug", "Release"], ["Debug"]]

apps:
  ascii_art:
    description: "ASCII art generator example"
    source_file: "AsciiArtComprehensiveTest.cpp"
    category: "utility"
    idf_versions: ["release/v5.5"]
    build_types: ["Debug", "Release"]
    ci_enabled: true
    featured: true

  gpio_test:
    description: "GPIO peripheral comprehensive testing"
    source_file: "GpioComprehensiveTest.cpp"
    category: "peripheral"
    idf_versions: ["release/v5.5"]
    build_types: ["Debug", "Release"]
    ci_enabled: true
    featured: true
```

#### **2. Dynamic Matrix Generation**

The `generate_matrix.py` script reads `app_config.yml` and creates a build matrix:

```python
# Generated matrix example
{
  "include": [
    {
      "idf_version": "release/v5.5",
      "idf_version_docker": "v5.5",
      "idf_version_file": "release_v5_5",
      "build_type": "Debug",
      "app_name": "ascii_art",
      "target": "esp32c6",
      "config_source": "app"
    },
    {
      "idf_version": "release/v5.5",
      "idf_version_docker": "v5.5", 
      "idf_version_file": "release_v5_5",
      "build_type": "Release",
      "app_name": "ascii_art",
      "target": "esp32c6",
      "config_source": "app"
    },
    {
      "idf_version": "release/v5.5",
      "idf_version_docker": "v5.5",
      "idf_version_file": "release_v5_5", 
      "build_type": "Debug",
      "app_name": "gpio_test",
      "target": "esp32c6",
      "config_source": "app"
    }
    // ... more combinations
  ]
}
```

#### **3. Two-Level CMakeLists.txt Structure**

The system uses a **two-level CMakeLists.txt structure** to enable dynamic app type selection:

**Level 1: Project-Level CMakeLists.txt** (in project root)

- Sets up global variables (`APP_TYPE`, `BUILD_TYPE`)
- Validates app types against `app_config.yml`
- Includes ESP-IDF build system
- Sets project name dynamically

**Level 2: Component-Level CMakeLists.txt** (in main/ folder)

- Gets source file from `app_config.yml` based on `APP_TYPE`
- Registers component with dynamic source file
- Sets up include paths and compile definitions
- Handles build type-specific compiler flags

**Project-Level CMakeLists.txt** (in project root):

```cmake
cmake_minimum_required(VERSION 3.16)

# CRITICAL: Set variables BEFORE any other processing
# This ensures they are available during component configuration
if(DEFINED APP_TYPE)
    message(STATUS "APP_TYPE from command line: ${APP_TYPE}")
else()
    set(APP_TYPE "ascii_art")
    message(STATUS "APP_TYPE defaulting to: ${APP_TYPE}")
endif()

if(DEFINED BUILD_TYPE)
    message(STATUS "BUILD_TYPE from command line: ${BUILD_TYPE}")
else()
    set(BUILD_TYPE "Release")
    message(STATUS "BUILD_TYPE defaulting to: ${BUILD_TYPE}")
endif()

# Validate app type by reading from app_config.yml (single source of truth)
execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/scripts/get_app_info.py" list
    OUTPUT_VARIABLE VALID_APP_TYPES_STRING
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE APP_LIST_RESULT
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

if(NOT APP_LIST_RESULT EQUAL 0)
    message(FATAL_ERROR "Failed to read valid app types from app_config.yml")
endif()

# Convert space-separated string to CMake list
string(REPLACE " " ";" VALID_APP_TYPES "${VALID_APP_TYPES_STRING}")

if(NOT APP_TYPE IN_LIST VALID_APP_TYPES)
    message(FATAL_ERROR "Invalid APP_TYPE: ${APP_TYPE}. Valid types: ${VALID_APP_TYPES}")
endif()

# Validate build type
set(VALID_BUILD_TYPES "Debug;Release")
if(NOT BUILD_TYPE IN_LIST VALID_BUILD_TYPES)
    message(FATAL_ERROR "Invalid BUILD_TYPE: ${BUILD_TYPE}. Valid types: ${VALID_BUILD_TYPES}")
endif()

# CRITICAL: Set these as global variables for all components
set(APP_TYPE "${APP_TYPE}" CACHE STRING "App type to build" FORCE)
set(BUILD_TYPE "${BUILD_TYPE}" CACHE STRING "Build type (Debug/Release)" FORCE)

# Include ESP-IDF build system
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Set project name based on app type
project(esp32_iid_${APP_TYPE}_app)
```

**Component-Level CMakeLists.txt** (in main/ folder):

```cmake
# Flexible main component for different app types
# Determine source file based on APP_TYPE

# Get app type from parent (set by project-level CMakeLists.txt)
if(NOT DEFINED APP_TYPE)
    set(APP_TYPE "main")
endif()

# Get source file from centralized configuration
execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/../scripts/get_app_info.py" validate "${APP_TYPE}"
    RESULT_VARIABLE VALIDATE_RESULT
    OUTPUT_QUIET
    ERROR_QUIET
)

if(NOT VALIDATE_RESULT EQUAL 0)
    message(FATAL_ERROR "Unknown APP_TYPE: ${APP_TYPE}")
endif()

execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/../scripts/get_app_info.py" source_file "${APP_TYPE}"
    OUTPUT_VARIABLE MAIN_SOURCE
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE SOURCE_RESULT
)

if(NOT SOURCE_RESULT EQUAL 0)
    message(FATAL_ERROR "Failed to get source file for APP_TYPE: ${APP_TYPE}")
endif()

# Check if source file exists and handle path resolution
set(SOURCE_FILE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/${MAIN_SOURCE}")
if(NOT EXISTS "${SOURCE_FILE_PATH}")
    set(SOURCE_FILE_PATH "${CMAKE_CURRENT_LIST_DIR}/${MAIN_SOURCE}")
    if(NOT EXISTS "${SOURCE_FILE_PATH}")
        message(FATAL_ERROR "Source file not found: ${MAIN_SOURCE}")
    endif()
endif()

# Determine include paths based on environment
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../inc")
    set(INC_BASE_PATH "../inc")
elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../../../inc")
    set(INC_BASE_PATH "../../../inc")
else()
    message(FATAL_ERROR "Cannot find inc directory")
endif()

# Register component with dynamic source file
idf_component_register(
    SRCS "${MAIN_SOURCE}"
    INCLUDE_DIRS "." "${INC_BASE_PATH}" "${INC_BASE_PATH}/base" "${INC_BASE_PATH}/mcu/esp32"
    REQUIRES driver esp_timer freertos iid-espidf
)

# Set C++ standard
target_compile_features(${COMPONENT_LIB} PRIVATE cxx_std_17)

# Set compiler flags based on build type
if(BUILD_TYPE STREQUAL "Debug")
    target_compile_options(${COMPONENT_LIB} PRIVATE
        -Wall -Wextra -Wpedantic -O0 -g3 -DDEBUG
    )
else()
    target_compile_options(${COMPONENT_LIB} PRIVATE
        -Wall -Wextra -Wpedantic -O2 -g -DNDEBUG
    )
endif()

# Add compile definitions for each example type
target_compile_definitions(${COMPONENT_LIB} PRIVATE 
    "EXAMPLE_TYPE_${APP_TYPE}=1"
)
```

#### **4. Parallel Build Execution**

The CI workflow executes each matrix combination in parallel:

1. **Matrix Generation**: Creates build combinations from `app_config.yml`
2. **Parallel Jobs**: Each combination runs as a separate GitHub Actions job
3. **Dynamic Building**: Each job builds a specific app with specific settings
4. **Artifact Collection**: All builds are collected and organized

#### **5. Key Benefits of This Approach**

- **🔄 Parallel Execution**: Multiple apps build simultaneously
- **⚙️ Configuration-Driven**: All settings centralized in `app_config.yml`
- **🎯 Flexible**: Easy to add/remove apps or build configurations
- **🔧 Maintainable**: Single source of truth for all build settings
- **📊 Comprehensive**: Tests all combinations automatically
- **🚀 Scalable**: Can handle dozens of apps and configurations

#### **6. CMakeLists.txt Requirements**

The CMakeLists.txt setup depends on your build approach. There are two main scenarios:

**Scenario A: CI-Only Builds (Minimal Setup)**

- Uses `build_app.sh` script which handles all the complexity
- CMakeLists.txt can be minimal since the script manages everything
- No direct `idf.py` support needed

**Scenario B: Full `idf.py` Compatibility (Complete Setup)**

- Supports both CI builds and direct `idf.py` usage
- Requires more complex CMakeLists.txt setup
- Enables development workflow with `idf.py build -DAPP_TYPE=app_name`

Let me show both approaches:

**Scenario A: Minimal CMakeLists.txt (CI-Only Builds)**

If you only use `build_app.sh` for building (CI workflows), your CMakeLists.txt can be minimal:

**Project-Level CMakeLists.txt** (minimal):

```cmake
cmake_minimum_required(VERSION 3.16)

# Define APP_TYPE with default value
if(NOT DEFINED APP_TYPE)
    set(APP_TYPE "main")
endif()

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32_iid_${APP_TYPE}_app)
```

**Component-Level CMakeLists.txt** (ultra-minimal):

```cmake
# Ultra-minimal setup - build_app.sh handles source file discovery
# Get source file from environment variable set by build_app.sh
if(NOT DEFINED APP_SOURCE_FILE)
    message(FATAL_ERROR "APP_SOURCE_FILE not defined. Use build_app.sh to build.")
endif()

# Register component with source file from build_app.sh
idf_component_register(
    SRCS "${APP_SOURCE_FILE}"  # Source file from build_app.sh
    INCLUDE_DIRS "."  # Add your own include directories as needed
    REQUIRES driver esp_timer freertos  # Add your own requirements as needed
)

# Add compile definitions for each example type
target_compile_definitions(${COMPONENT_LIB} PRIVATE 
    "EXAMPLE_TYPE_${APP_TYPE}=1"
)
```

**Note for Users:**

- **INCLUDE_DIRS**: Add your own include directories (e.g., `"../inc"`, `"../lib"`)
- **REQUIRES**: Add your own component requirements (e.g., `"your_component"`, `"esp_wifi"`)
- **SRCS**: Only `APP_SOURCE_FILE` is required - the script handles source file selection
- **APP_TYPE**: Only `APP_TYPE` is required - the script handles app type validation

**What Gets Removed in Ultra-Minimal Setup:**

- ❌ **App Type Validation**: No checking if `APP_TYPE` exists in `app_config.yml`
- ❌ **Build Type Validation**: No checking if `BUILD_TYPE` is valid
- ❌ **Advanced Variable Setting**: No `set(APP_TYPE ... CACHE ... FORCE)` or `set(BUILD_TYPE ...)`
- ❌ **Dynamic Project Naming**: No `project(esp32_iid_${APP_TYPE}_app)`
- ❌ **Python Dependencies**: No `execute_process` calls to `get_app_info.py`
- ❌ **Source File Discovery**: No dynamic source file selection in CMake

**What Stays in Ultra-Minimal Setup:**

- ✅ **Basic APP_TYPE Definition**: Simple `if(NOT DEFINED APP_TYPE)` with default
- ✅ **Dynamic Project Naming**: Still uses `project(esp32_iid_${APP_TYPE}_app)`
- ✅ **Environment Variable Usage**: Uses `APP_SOURCE_FILE` from `build_app.sh`
- ✅ **APP_TYPE Variable**: Still receives `APP_TYPE` from `build_app.sh`
- ✅ **Compile Definitions**: Still adds `EXAMPLE_TYPE_${APP_TYPE}=1`
- ✅ **Basic Component Registration**: Registers component with source from script

**Why This Works:**

- `build_app.sh` discovers source file from `app_config.yml` and sets `APP_SOURCE_FILE` environment variable
- `build_app.sh` calls `idf.py` with `-D APP_TYPE=app_name`, `-D APP_SOURCE_FILE=source_file`, and `-D BUILD_TYPE=build_type`
- CMakeLists.txt simply uses the `APP_SOURCE_FILE` variable provided by the script
- `build_app.sh` handles all validation and source file discovery before calling `idf.py`
- Perfect for CI-only workflows where script handles everything

**Alternative Minimal Approach (Conditional Sources):**

You can also use CMake's conditional source inclusion instead of dynamic source selection:

```cmake
# Alternative minimal approach using conditional sources
idf_component_register(
    SRCS
        "common_source.cpp"
        $<$<STREQUAL:${APP_TYPE},ascii_art>:"AsciiArtComprehensiveTest.cpp">
        $<$<STREQUAL:${APP_TYPE},gpio_test>:"GpioComprehensiveTest.cpp">
        $<$<STREQUAL:${APP_TYPE},adc_test>:"AdcComprehensiveTest.cpp">
        $<$<STREQUAL:${APP_TYPE},uart_test>:"UartComprehensiveTest.cpp">
    INCLUDE_DIRS "."
    REQUIRES driver esp_timer freertos
)

# Add compile definitions for each example type
target_compile_definitions(${COMPONENT_LIB} PRIVATE 
    "EXAMPLE_TYPE_${APP_TYPE}=1"
)
```

**Pros of Conditional Sources:**

- ✅ **No Python Dependencies**: Doesn't need `get_app_info.py`
- ✅ **Faster CMake**: No `execute_process` calls
- ✅ **Explicit**: All source files are visible in CMakeLists.txt

**Cons of Conditional Sources:**

- ❌ **Manual Maintenance**: Must update CMakeLists.txt when adding new apps
- ❌ **Not DRY**: Duplicates information from `app_config.yml`
- ❌ **Error Prone**: Easy to forget to add new apps

**Ultra-Minimal CMakeLists.txt** (no Python dependencies):

```cmake
cmake_minimum_required(VERSION 3.16)

# Define APP_TYPE with default value
if(NOT DEFINED APP_TYPE)
    set(APP_TYPE "main")
endif()

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32_app)
```

**Ultra-Minimal Component CMakeLists.txt** (no Python dependencies):

```cmake
# Get source file from environment variable set by build_app.sh
if(DEFINED ENV{APP_SOURCE_FILE})
    set(MAIN_SOURCE $ENV{APP_SOURCE_FILE})
else()
    message(FATAL_ERROR "APP_SOURCE_FILE environment variable not set. Run build_app.sh instead of idf.py directly.")
endif()

# Register component with source file from environment
idf_component_register(
    SRCS "${MAIN_SOURCE}"
    INCLUDE_DIRS "."
    REQUIRES driver esp_timer freertos
)

# Add compile definitions for each example type
target_compile_definitions(${COMPONENT_LIB} PRIVATE 
    "EXAMPLE_TYPE_${APP_TYPE}=1"
)
```

**Pros of Environment Variable Approach:**

- ✅ **No Python Dependencies in CMake**: CMakeLists.txt is completely Python-free
- ✅ **Faster CMake**: No `execute_process` calls during CMake configuration
- ✅ **Centralized Logic**: All app selection logic in `build_app.sh`
- ✅ **Clear Separation**: Script handles configuration, CMake handles building
- ✅ **Error Prevention**: Prevents direct `idf.py` usage without proper setup

**Cons of Environment Variable Approach:**

- ❌ **No Direct `idf.py` Support**: Must always use `build_app.sh`
- ❌ **Environment Dependency**: Relies on environment variables being set
- ❌ **Script Coupling**: CMakeLists.txt is tightly coupled to `build_app.sh`

**When to Use Each Approach:**

| Approach | Python Deps | Direct `idf.py` | Speed | Maintainability |
|----------|-------------|-----------------|-------|-----------------|
| **Dynamic Source Selection** | ✅ Required | ✅ Supported | Medium | ✅ High |
| **Conditional Sources** | ❌ None | ✅ Supported | ✅ Fast | ❌ Low |
| **Environment Variables** | ❌ None | ❌ Not Supported | ✅ Fast | ✅ High |

**Recommendation:**

- Use **Environment Variables** for CI-only workflows where you never need direct `idf.py`
- Use **Dynamic Source Selection** for development workflows with `idf.py` support
- Use **Conditional Sources** only if you want to avoid Python dependencies but need `idf.py` support

**Scenario B: Full `idf.py` Compatibility (Complete Setup)**

If you want to support both CI builds AND direct `idf.py` usage for development, you need the full setup:

**Project-Level CMakeLists.txt** (complete):

```cmake
cmake_minimum_required(VERSION 3.16)

# CRITICAL: Set variables BEFORE any other processing
# This ensures they are available during component configuration
if(DEFINED APP_TYPE)
    message(STATUS "APP_TYPE from command line: ${APP_TYPE}")
else()
    set(APP_TYPE "ascii_art")
    message(STATUS "APP_TYPE defaulting to: ${APP_TYPE}")
endif()

if(DEFINED BUILD_TYPE)
    message(STATUS "BUILD_TYPE from command line: ${BUILD_TYPE}")
else()
    set(BUILD_TYPE "Release")
    message(STATUS "BUILD_TYPE defaulting to: ${BUILD_TYPE}")
endif()

# Validate app type by reading from app_config.yml (single source of truth)
execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/scripts/get_app_info.py" list
    OUTPUT_VARIABLE VALID_APP_TYPES_STRING
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE APP_LIST_RESULT
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

if(NOT APP_LIST_RESULT EQUAL 0)
    message(FATAL_ERROR "Failed to read valid app types from app_config.yml")
endif()

# Convert space-separated string to CMake list
string(REPLACE " " ";" VALID_APP_TYPES "${VALID_APP_TYPES_STRING}")

if(NOT APP_TYPE IN_LIST VALID_APP_TYPES)
    message(FATAL_ERROR "Invalid APP_TYPE: ${APP_TYPE}. Valid types: ${VALID_APP_TYPES}")
endif()

# Validate build type
set(VALID_BUILD_TYPES "Debug;Release")
if(NOT BUILD_TYPE IN_LIST VALID_BUILD_TYPES)
    message(FATAL_ERROR "Invalid BUILD_TYPE: ${BUILD_TYPE}. Valid types: ${VALID_BUILD_TYPES}")
endif()

# CRITICAL: Set these as global variables for all components
set(APP_TYPE "${APP_TYPE}" CACHE STRING "App type to build" FORCE)
set(BUILD_TYPE "${BUILD_TYPE}" CACHE STRING "Build type (Debug/Release)" FORCE)

# Include ESP-IDF build system
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Set project name based on app type
project(esp32_iid_${APP_TYPE}_app)
```

**Component-Level CMakeLists.txt** (complete):

```cmake
# Flexible main component for different app types
# Determine source file based on APP_TYPE

# Get app type from parent (set by project-level CMakeLists.txt)
if(NOT DEFINED APP_TYPE)
    set(APP_TYPE "main")
endif()

# Get source file from centralized configuration
execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/../scripts/get_app_info.py" validate "${APP_TYPE}"
    RESULT_VARIABLE VALIDATE_RESULT
    OUTPUT_QUIET
    ERROR_QUIET
)

if(NOT VALIDATE_RESULT EQUAL 0)
    message(FATAL_ERROR "Unknown APP_TYPE: ${APP_TYPE}")
endif()

execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/../scripts/get_app_info.py" source_file "${APP_TYPE}"
    OUTPUT_VARIABLE MAIN_SOURCE
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE SOURCE_RESULT
)

if(NOT SOURCE_RESULT EQUAL 0)
    message(FATAL_ERROR "Failed to get source file for APP_TYPE: ${APP_TYPE}")
endif()

# Check if source file exists and handle path resolution
set(SOURCE_FILE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/${MAIN_SOURCE}")
if(NOT EXISTS "${SOURCE_FILE_PATH}")
    set(SOURCE_FILE_PATH "${CMAKE_CURRENT_LIST_DIR}/${MAIN_SOURCE}")
    if(NOT EXISTS "${SOURCE_FILE_PATH}")
        message(FATAL_ERROR "Source file not found: ${MAIN_SOURCE}")
    endif()
endif()

# Determine include paths based on environment
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../inc")
    set(INC_BASE_PATH "../inc")
elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../../../inc")
    set(INC_BASE_PATH "../../../inc")
else()
    message(FATAL_ERROR "Cannot find inc directory")
endif()

# Register component with dynamic source file
idf_component_register(
    SRCS "${MAIN_SOURCE}"
    INCLUDE_DIRS "." "${INC_BASE_PATH}" "${INC_BASE_PATH}/base" "${INC_BASE_PATH}/mcu/esp32"
    REQUIRES driver esp_timer freertos iid-espidf
)

# Set C++ standard
target_compile_features(${COMPONENT_LIB} PRIVATE cxx_std_17)

# Set compiler flags based on build type
if(BUILD_TYPE STREQUAL "Debug")
    target_compile_options(${COMPONENT_LIB} PRIVATE
        -Wall -Wextra -Wpedantic -O0 -g3 -DDEBUG
    )
else()
    target_compile_options(${COMPONENT_LIB} PRIVATE
        -Wall -Wextra -Wpedantic -O2 -g -DNDEBUG
    )
endif()

# Add compile definitions for each example type
target_compile_definitions(${COMPONENT_LIB} PRIVATE 
    "EXAMPLE_TYPE_${APP_TYPE}=1"
)
```

**Why This Full Setup is Needed for `idf.py` Compatibility:**

1. **Command Line Support**: `idf.py build -DAPP_TYPE=gpio_test -DBUILD_TYPE=Release`
2. **Validation**: Ensures app types exist in `app_config.yml` before building
3. **Dynamic Source Selection**: Gets the correct source file for each app type
4. **Project Naming**: Sets project name dynamically based on app type
5. **Development Workflow**: Enables developers to build directly with `idf.py`

**Usage Examples:**

**CI Builds (both scenarios work):**

```bash
# Uses build_app.sh which handles everything
./build_app.sh gpio_test Release
```

**Direct `idf.py` Usage (only Scenario B works):**

```bash
# Direct idf.py usage for development
idf.py build -DAPP_TYPE=gpio_test -DBUILD_TYPE=Release
idf.py flash -DAPP_TYPE=gpio_test -DBUILD_TYPE=Release
idf.py monitor
```

**Recommendation:**

- **Use Scenario A** if you only use CI workflows and never need direct `idf.py` usage
- **Use Scenario B** if you want full development workflow support with `idf.py`

#### **7. How build_app.sh Works with Both Scenarios**

The `build_app.sh` script is designed to work with both CMakeLists.txt scenarios:

**Key Script Features:**

- **Automatic ESP-IDF Setup**: Sources the correct ESP-IDF version
- **Source File Discovery**: Gets source file from `app_config.yml` and exports as `APP_SOURCE_FILE`
- **Parameter Passing**: Calls `idf.py` with `-DAPP_TYPE`, `-DAPP_SOURCE_FILE`, and `-DBUILD_TYPE`
- **Build Directory Management**: Creates organized build directories
- **Size Analysis**: Generates size reports and metadata
- **Error Handling**: Validates combinations before building

**Script Call Pattern:**

```bash
# build_app.sh discovers source file and calls idf.py like this:
# 1. Get source file from app_config.yml
SOURCE_FILE=$(python3 "${SCRIPT_DIR}/get_app_info.py" source_file "${APP_TYPE}")
export APP_SOURCE_FILE="${SOURCE_FILE}"

# 2. Call idf.py with all necessary variables
idf.py -B "$BUILD_DIR" -D CMAKE_BUILD_TYPE="$BUILD_TYPE" -D BUILD_TYPE="$BUILD_TYPE" -D APP_TYPE="$APP_TYPE" -D APP_SOURCE_FILE="$SOURCE_FILE" -D IDF_CCACHE_ENABLE="$USE_CCACHE" reconfigure
idf.py -B "$BUILD_DIR" build
```

**How It Works with Scenario A (Ultra-Minimal CMakeLists.txt):**

- Script discovers source file from `app_config.yml` and sets `APP_SOURCE_FILE` environment variable
- Script passes `-DAPP_TYPE=gpio_test` and `-DAPP_SOURCE_FILE=GpioComprehensiveTest.cpp` to `idf.py`
- CMakeLists.txt simply uses the `APP_SOURCE_FILE` variable provided by the script
- Script handles all app selection and source file discovery logic
- Perfect for CI-only workflows

**How It Works with Scenario B (Full CMakeLists.txt):**

- Script discovers source file from `app_config.yml` and sets `APP_SOURCE_FILE` environment variable
- Script passes `-DAPP_TYPE=gpio_test` and `-DAPP_SOURCE_FILE=GpioComprehensiveTest.cpp` to `idf.py`
- CMakeLists.txt can use either the script-provided `APP_SOURCE_FILE` or do its own discovery
- Both script and CMakeLists.txt work together
- Enables both CI and development workflows

**Script Parameters:**

```bash
# Basic usage
./build_app.sh gpio_test Release

# With ESP-IDF version
./build_app.sh gpio_test Release release/v5.5

# With project path (for CI)
./build_app.sh --project-path /path/to/project gpio_test Release

# Clean build
./build_app.sh gpio_test Release --clean

# List available apps
./build_app.sh list

# Show app information
./build_app.sh info gpio_test
```

#### **8. Submodule Integration**

The `hf-espidf-project-tools` submodule provides the essential scripts:

**Required Scripts:**

- **`generate_matrix.py`**: Reads `app_config.yml` and generates build matrix
- **`build_app.sh`**: Builds specific app with given parameters
- **`get_app_info.py`**: Extracts app information from configuration
- **`config_loader.sh`**: Loads and validates configuration

**Submodule Setup:**

```bash
# Add submodule
git submodule add https://github.com/hardfoc/hf-espidf-project-tools.git examples/esp32/scripts

# Initialize submodule
git submodule update --init --recursive
```

**Directory Structure:**

```
your-project/
├── examples/esp32/
│   ├── CMakeLists.txt              # Project-level CMakeLists.txt
│   ├── app_config.yml              # Build configuration
│   ├── main/
│   │   ├── AsciiArtComprehensiveTest.cpp
│   │   ├── GpioComprehensiveTest.cpp
│   │   ├── AdcComprehensiveTest.cpp
│   │   └── CMakeLists.txt          # Component-level CMakeLists.txt
│   └── scripts/  # Submodule
│       ├── generate_matrix.py
│       ├── build_app.sh
│       ├── get_app_info.py
│       └── config_loader.sh
```

#### **9. Build Process Flow**

1. **Configuration Reading**: `generate_matrix.py` reads `app_config.yml`
2. **Matrix Generation**: Creates all valid build combinations
3. **Parallel Execution**: Each combination runs as separate job
4. **Dynamic Building**: Each job calls `build_app.sh` with specific parameters
5. **CMake Integration**: CMakeLists.txt uses `APP_SOURCE_FILE` from build_app.sh
6. **Artifact Collection**: All builds are collected and organized

#### **10. How App Type Selection Works**

The app type selection system enables dynamic building of different applications from the same codebase:

**Step 1: Command Line Input**

```bash
# CI builds with specific app type
idf.py build -DAPP_TYPE=gpio_test -DBUILD_TYPE=Release

# Development builds with default app type
idf.py build  # Uses default from app_config.yml
```

**Step 2: Project-Level Validation**

- Project-level CMakeLists.txt receives `APP_TYPE` and `BUILD_TYPE`
- Validates `APP_TYPE` against `app_config.yml` using `get_app_info.py list`
- Sets global variables for all components
- Sets project name dynamically: `esp32_iid_${APP_TYPE}_app`

**Step 3: Component-Level Source Selection**

- Component-level CMakeLists.txt gets `APP_TYPE` from parent
- Calls `get_app_info.py source_file ${APP_TYPE}` to get source file name
- Validates source file exists in main/ directory
- Registers component with dynamic source file

**Step 4: Build Configuration**

- Sets include paths based on environment (CI vs development)
- Applies build type-specific compiler flags
- Adds app-specific compile definitions: `EXAMPLE_TYPE_${APP_TYPE}=1`

**Key Benefits:**

- **Single Codebase**: All apps share the same project structure
- **Dynamic Selection**: Build any app without code changes
- **Validation**: Ensures app types exist in configuration
- **Flexibility**: Easy to add new apps by updating `app_config.yml`
- **CI Integration**: Matrix builds automatically test all combinations

#### **11. app_config.yml Structure**

The `app_config.yml` file is the central configuration that enables parallel building:

**Global Metadata:**

```yaml
metadata:
  project: "ESP32 HardFOC Interface Wrapper"
  default_app: "ascii_art"
  target: "esp32c6"
  idf_versions: ["release/v5.5", "release/v5.4"]
  build_types: [["Debug", "Release"], ["Debug"]]
```

**App Definitions:**

```yaml
apps:
  ascii_art:
    description: "ASCII art generator example"
    source_file: "AsciiArtComprehensiveTest.cpp"
    category: "utility"
    idf_versions: ["release/v5.5"]
    build_types: ["Debug", "Release"]
    ci_enabled: true
    featured: true

  gpio_test:
    description: "GPIO peripheral comprehensive testing"
    source_file: "GpioComprehensiveTest.cpp"
    category: "peripheral"
    idf_versions: ["release/v5.5"]
    build_types: ["Debug", "Release"]
    ci_enabled: true
    featured: true
```

**Key Features:**

- **Hierarchical Configuration**: Global settings apply to all apps by default
- **App Overrides**: Individual apps can override global settings
- **Source File Mapping**: Each app maps to its specific source file
- **Build Type Control**: Apps can specify which build types to use
- **CI Integration**: `ci_enabled` flag controls which apps are built in CI

#### **12. Parallel Building Benefits**

This setup enables powerful parallel building capabilities:

**Multiple Apps × Multiple Build Types × Multiple IDF Versions:**

- **12 apps** × **2 build types** × **2 IDF versions** = **48 parallel builds**
- Each build runs independently and in parallel
- No dependency between different app builds
- Maximum utilization of GitHub Actions runners

**Example Build Matrix:**

```
ascii_art + Debug + v5.5     │ gpio_test + Debug + v5.5
ascii_art + Release + v5.5   │ gpio_test + Release + v5.5
ascii_art + Debug + v5.4     │ gpio_test + Debug + v5.4
adc_test + Debug + v5.5      │ uart_test + Debug + v5.5
adc_test + Release + v5.5    │ uart_test + Release + v5.5
... (all combinations)       │ ... (all combinations)
```

**Time Savings:**

- **Sequential**: 48 builds × 5 minutes = 4 hours
- **Parallel**: 48 builds ÷ 20 runners = ~12 minutes
- **Speedup**: 20x faster with parallel execution

#### **13. Key Scripts and Their Roles**

The `hf-espidf-project-tools` submodule provides essential scripts that enable the dynamic build system:

**`generate_matrix.py`**

- **Purpose**: Reads `app_config.yml` and generates build matrix
- **Input**: `app_config.yml` configuration file
- **Output**: JSON matrix with all valid build combinations
- **Usage**: Called by CI workflow to create parallel build jobs

**`get_app_info.py`**

- **Purpose**: Extracts app information from `app_config.yml`
- **Commands**:
  - `list`: Returns all valid app types
  - `validate <app_type>`: Validates app type exists
  - `source_file <app_type>`: Returns source file name for app
  - `info <app_type>`: Returns detailed app information
- **Usage**: Called by CMakeLists.txt to get app-specific data

**`build_app.sh`**

- **Purpose**: Builds specific app with given parameters
- **Parameters**: `--project-path`, app name, build type, IDF version
- **Usage**: Called by CI workflow for each matrix combination

**`config_loader.sh`**

- **Purpose**: Loads and validates configuration
- **Usage**: Provides configuration utilities for other scripts

**Script Integration Flow:**

```
CI Workflow → generate_matrix.py → Build Matrix
     ↓
Each Build Job → build_app.sh → idf.py build
     ↓
CMakeLists.txt → APP_SOURCE_FILE → Source File Selection
     ↓
ESP-IDF Build → Firmware Binary
```

### **Matrix Generation**

The workflow calls your project's `generate_matrix.py` script to create the build matrix:

```python
# Expected output format from generate_matrix.py
{
  "include": [
    {
      "idf_version": "release/v5.5",        # Git format for ESP-IDF cloning
      "idf_version_docker": "v5.5",         # Docker-safe format for artifacts
      "idf_version_file": "release_v5_5",   # File-safe format for build dirs
      "build_type": "Debug",                # Build configuration
      "app_name": "gpio_test",              # Application name
      "target": "esp32c6",                  # Target MCU
      "config_source": "app"                # Configuration source
    }
  ]
}
```

### **Required Scripts**

Your `hf-espidf-project-tools` directory must contain:

| Script | Purpose | Required |
|--------|---------|----------|
| `generate_matrix.py` | Matrix generator from `app_config.yml` | ✅ |
| `build_app.sh` | Application builder | ✅ |
| `config_loader.sh` | Configuration loader | ✅ |
| `requirements.txt` | Python dependencies | ❌ |

---

## 🏗️ Build Process

### **Phase 1: Matrix Generation**

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Checkout    │───▶│ Ensure Tools    │───▶│ Install Python  │───▶│ Run generate    │───▶│ Output JSON     │
│ Repo        │    │ Directory       │    │ Deps            │    │ matrix.py       │    │ Matrix          │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Phase 2: Parallel Build Execution**

```
┌─────────────┐
│ Matrix      │
│ Entry       │
└──────┬──────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐     
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Checkout    │───▶│ Cache Python    │───▶│ Install Python  │───▶│ ESP-IDF CI      │ │
│  │ Repo        │    │ Deps            │    │ Deps            │    │ Action          │ │
│  └─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                            │          │
│                                                                            ▼          │
│  ┌─────────────┐    ┌─────────────────┐                           ┌─────────────────┐ │
│  │ Upload      │◀───│ Build with      │◀───---------------------──│ Cache ccache    │ │
│  │ Artifacts   │    │ build_app.sh    │ *ESP-IDF CI HAS IDF RDY*  │                 │ │
│  └─────────────┘    └─────────────────┘                           └─────────────────┘ │
└──────┬────────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│ Matrix      │
│ Exit        │
└─────────────┘
```

### **Phase 3: Size Reporting**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Download        │───▶│ Parse Size      │───▶│ Generate        │───▶│ Comment on      │
│ Artifacts       │    │ Data            │    │ Markdown        │    │ PR              │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Detailed Build Steps**

1. **🔍 Matrix Generation**:
   - Validates project tools directory
   - Runs `generate_matrix.py` with project configuration
   - Outputs JSON matrix for parallel execution

2. **🏗️ Direct Project Building**:
   - ESP-IDF CI action works directly with project files
   - No file copying or workspace preparation needed
   - Builds directly from source directory structure

3. **🛡️ ESP-IDF Environment**:
   - Uses `espressif/esp-idf-ci-action@v1` for reliable environment
   - Sets up ESP-IDF tools and dependencies
   - Configures target and build parameters

4. **⚡ Build Execution**:
   - Runs `build_app.sh` with matrix parameters
   - Handles incremental builds with ccache
   - Generates size analysis and metadata

5. **📦 Artifact Management**:
   - Uploads firmware binaries and build outputs
   - Organizes artifacts by app, version, and build type
   - Sets appropriate retention policies

6. **📊 Size Reporting**:
   - Aggregates size data from all builds
   - Creates comprehensive PR comments
   - Enforces size budgets (optional)

---

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **Matrix Generation Fails**

**Symptoms**: "Matrix generation failed" or "No matrix entries found"
**Solutions**:

```bash
# Check script exists and is executable
ls -la hf-espidf-project-tools/generate_matrix.py
chmod +x hf-espidf-project-tools/generate_matrix.py

# Test matrix generation locally
cd examples/esp32
python3 hf-espidf-project-tools/generate_matrix.py --validate

# Check Python dependencies
pip install pyyaml jq
```

#### **Build Fails**

**Symptoms**: "Build failed" or "ESP-IDF not found"
**Solutions**:

```bash
# Verify project structure is ready for building
ls -la src/ inc/ examples/
ls -la CMakeLists.txt app_config.yml

# Check build_app.sh handles matrix parameters
./hf-espidf-project-tools/build_app.sh --help

# Validate ESP-IDF version compatibility
python3 hf-espidf-project-tools/generate_matrix.py --validate
```

#### **Cache Issues**

**Symptoms**: "Cache miss" or "Build too slow"
**Solutions**:

```yaml
# Use clean build to bypass caches
clean_build: true

# Check cache configuration
# Cache keys should include relevant file hashes
```

#### **Artifact Upload Fails**

**Symptoms**: "Artifact upload failed" or "No artifacts found"
**Solutions**:

```bash
# Check build outputs exist
ls -la build-app-*/

# Verify build_app.sh generates proper outputs
./hf-espidf-project-tools/build_app.sh gpio_test Release

# Check size files are created inside build directory
ls -la build-app-*/size.*

# Verify artifact structure
find build-app-*/ -name "*.bin" -o -name "*.elf" -o -name "size.*"
```

#### **Size Report Issues**

**Symptoms**: "No size artifacts found" or "Size data missing"
**Solutions**:

```bash
# Check size files are created in build directory
ls -la build-app-*/size.*

# Verify size.info contains metadata
cat build-app-*/size.info

# Check build_app.sh size generation
./hf-espidf-project-tools/build_app.sh gpio_test Release
ls -la build-app-*/size.*
```

#### **Size Budget Violations**

**Symptoms**: "Size budget exceeded" or build fails due to size limits
**Solutions**:

```yaml
# Disable size budget enforcement temporarily
max_dec_total: "0"

# Increase size limit (in bytes)
max_dec_total: "2000000"  # 2MB limit

# Use dynamic size limits based on build type
max_dec_total: ${{ matrix.build_type == 'Debug' && '2000000' || '1600000' }}
```

```bash
# Check current firmware sizes
grep -E '^\s*text\s+data\s+bss\s+dec' build-app-*/size.txt

# Analyze size breakdown
python3 -c "
import re
with open('build-app-*/size.txt', 'r') as f:
    for line in f:
        if 'dec' in line:
            print(line.strip())
"
```

#### **"build_app.sh: No such file or directory"**

**Cause**: Path resolution or submodule checkout issues

**Solutions**:

1. **Check Submodule Status**: Verify submodule is properly initialized

   ```bash
   git submodule status
   git submodule update --init --recursive
   ```

2. **Verify Paths**: Check that `project_tools_dir` points to the correct location
3. **Check Repository Structure**: Ensure the tools directory contains required scripts
4. **For Explicit Paths**: When `project_tools_dir` is specified, the workflow uses that path directly (no auto-cloning)

#### **"Project tools directory not found"**

**Cause**: Incorrect path configuration or missing tools directory

**Solutions**:

1. **Verify Paths**: Ensure paths are relative to repository root
2. **Check Auto-clone**: Set `auto_clone_tools: true` if not using submodules
3. **Manual Setup**: Clone tools repository manually if needed

#### **Submodule Detection Issues**

**Symptoms**: Workflow runs but can't find scripts in submodule

**Solutions**:

1. **Specify `project_tools_dir`** - When using submodules, explicitly set the path to the submodule
2. **Verify Submodule URL**: Ensure submodule points to correct repository
3. **Check Submodule Commit**: Ensure submodule is at a valid commit
4. **Auto-clone Logic**: Auto-clone only happens when `project_tools_dir` is not specified

### **Debug Information**

The workflow provides detailed logging to help diagnose issues:

- Path resolution details
- Submodule detection and validation
- Available directory listings
- Script validation results

### **Debug Mode**

Enable verbose output for debugging:

```yaml
jobs:
  build:
    uses: hardfoc/hf-espidf-ci-tools/.github/workflows/ru-build.yml@v1
    with:
      project_dir: examples/esp32
      clean_build: true  # Bypass caches for debugging
```

Enable debug output by setting:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### **Local Testing**

Test the build process locally:

```bash
# 1. Setup environment
cd examples/esp32
source hf-espidf-project-tools/setup_common.sh

# 2. Test matrix generation
python3 hf-espidf-project-tools/generate_matrix.py --validate

# 3. Test direct building (no setup needed)

# 4. Test build
./hf-espidf-project-tools/build_app.sh gpio_test Release
```


---

## 📚 Related Documentation

- 📖 [**Main Documentation**](../README.md) - Complete CI tools overview
- 🛡️ [**Security Workflow**](security-workflow.md) - Security auditing and analysis

### **Project Tools Documentation**

- 🏗️ [**Build System**](https://github.com/hardfoc/hf-espidf-project-tools) - Complete build system guide
- Check cache key generation in workflow
- Verify cache paths are accessible

## 📚 Related Workflows

- **[Security](security-workflow.md)** - Security auditing

## 🔗 Related Resources

- [ESP-IDF CI Action](https://github.com/espressif/esp-idf-ci-action)
- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)

---

[← Previous: Documentation Index](index.md) | [Next: Security Workflow →](security-workflow.md)

**📚 [All Documentation](index.md)** | **🏠 [Main README](../README.md)**
