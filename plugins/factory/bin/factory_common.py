"""Where the project's factory lives. Shared by factory-job, factory-gate and factory-route.

The project is the git repository that contains the current directory, or the
one $FACTORY_REPO names. Its factory state and configuration live under
<repo>/.factory/, written by /factory:setup; the scripts come from the plugin.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parent


def _repo():
    env = os.environ.get("FACTORY_REPO")
    if env:
        return Path(env).resolve()
    res = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit("factory: run this inside the project's git repository (or set FACTORY_REPO)")
    return Path(res.stdout.strip())


REPO = _repo()
FACTORY = REPO / ".factory"
CONFIG_PATH = FACTORY / "config.json"
CHECKS = FACTORY / "checks.sh"

if not CONFIG_PATH.exists():
    sys.exit(f"factory: {CONFIG_PATH} doesn't exist; run /factory:setup in this project first")

DEFAULTS = {
    "concurrency": 2,
    "max_rounds": 5,
    "base_branch": "main",
    "merge_method": "squash",
    "language": "es",
    "labels": {"queue": "factory", "needs_info": "factory:needs-info", "needs_human": "factory:needs-human"},
    "routing": {
        "low": {"builder": "sonnet", "standards": "haiku", "spec": "haiku"},
        "medium": {"builder": "sonnet", "standards": "sonnet", "spec": "sonnet"},
        "high": {"builder": "opus", "standards": "sonnet", "spec": "sonnet"},
    },
    "surface_reviewers": {
        "ui": {"ux": "sonnet", "ui": "sonnet"},
        "security": {"security": "opus"},
    },
    "protected_paths": [".factory/*"],
    "test_globs": ["tests/*", "*/tests/*", "test_*.py", "*_test.py", "*.test.*", "*.spec.*"],
    "human_paths": [],
    "human_notes": [],
    "ports": {"base": 5200, "step": 10},
    "prices_usd_per_mtok": {},
}


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


CONFIG = _merge(DEFAULTS, json.loads(CONFIG_PATH.read_text()))
