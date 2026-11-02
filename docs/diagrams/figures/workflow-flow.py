"""From a caller's push to a GitHub Release: the two reusable workflows and what passes between them.

Reads: From top to bottom. A HardFOC repository calls ru-build from its ESP32 build workflow. ru-build's first job
finds hf-espidf-project-tools (a submodule, the project_tools_dir input, or a clone) and turns app_config.yml into a
build matrix. The build job runs once per matrix entry inside the espressif/idf Docker image and uploads the build
folder as a fw-* artifact. On pull requests the size-report job comments a size table. When the caller pushes a
version tag, ru-release-with-artifacts downloads the fw-* artifacts built for that commit and attaches them to a
GitHub Release. Job names are read from the workflow files.
"""

import yaml

from hardfoc_mkdocs_theme.figkit import Fig
from hardfoc_mkdocs_theme.paths import repo_root

ROOT = repo_root()
BUILD = ".github/workflows/ru-build.yml"
RELEASE = ".github/workflows/ru-release-with-artifacts.yml"


def _jobs(path):
    doc = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    return [(jid, " ".join(str(j.get("name", jid)).split())) for jid, j in doc["jobs"].items()]


def data():
    return {
        "build_jobs": [j for j, _ in _jobs(BUILD)],
        "release_jobs": [j for j, _ in _jobs(RELEASE)],
        "sources": [f"{BUILD}:jobs", f"{RELEASE}:jobs"],
    }


def build(d):
    f = Fig(
        "workflow-flow",
        "From push to release",
        alt="Flow diagram: a calling repository runs ru-build, whose generate-matrix, build and size-report jobs read "
        "app_config.yml through hf-espidf-project-tools, build every app in the espressif/idf image and upload fw-* "
        "artifacts; on a version tag ru-release-with-artifacts attaches those artifacts to a GitHub Release.",
        width=1200,
        kicker="Workflows",
        subtitle="Two reusable workflows. The build workflow produces the firmware; the release workflow ships it.",
        profile="overview",
        legend=[("brand", "this repository"), ("teal", "your repository"), ("slate", "external")],
    )
    W = f.body_w
    caller = f.card(0, 0, W, "Your repository",
                    ["esp32-examples-build-ci.yml calls ru-build  /  release.yml (on v* tags) calls the release"],
                    tone="teal", accent=True)

    top = caller.b + 40
    inner = f.region_inner_top(top)
    gap = 24
    cw = (W - 32 - 2 * gap) / 3
    texts = {
        "generate-matrix": ["find the project tools", "app_config.yml to a matrix"],
        "build": ["one job per app, IDF, build type", "espressif/idf image, build_app.sh"],
        "size-report": ["pull requests only", "size table comment, optional budget"],
    }
    cards = []
    for i, job in enumerate(d["build_jobs"]):
        cards.append(f.card(16 + i * (cw + gap), inner, cw, job, texts.get(job, []), tone="brand", mono=False))
    hb = max(c.b for c in cards)
    reg = f.region(0, top, W, hb - top + 18, "ru-build.yml", tone="brand")
    for a, b in zip(cards, cards[1:]):
        f.connect(a, b, "right", "left", tone="rail")

    tools = f.card(0, reg.b + 40, (W - gap) / 2, "hf-espidf-project-tools",
                   ["generate_matrix.py, build_app.sh, config_loader.sh"], tone="slate")
    art = f.card(tools.r + gap, reg.b + 40, (W - gap) / 2, "fw-<app>-<idf>-<build type>",
                 ["artifacts, kept 7 days"], tone="slate", mono=True)
    f.connect(cards[0], tools, "bottom", "top", tone="rail")
    f.connect(cards[1], art, "bottom", "top", tone="rail")

    rel = f.card(0, art.b + 40, W, d["release_jobs"][0] + " (ru-release-with-artifacts.yml)",
                 ["downloads the fw-* artifacts built for the tagged commit, creates the release, attaches them"],
                 tone="brand", accent=True)
    f.connect(art, rel, "bottom", "top", tone="rail")
    gh = f.card(0, rel.b + 40, W, "GitHub Release", ["generated notes and the firmware of every matrix entry"],
                tone="slate")
    f.connect(rel, gh, "bottom", "top", tone="rail")
    f.connect(caller, reg, "bottom", "top", tone="rail")
    return f
