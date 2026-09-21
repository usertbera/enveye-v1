from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from deepdiff import DeepDiff

SEVERITY_BY_KIND = {
    "missing": "high",
    "type_changed": "medium",
    "changed": "medium",
    "added": "low",
}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

_PATH_KEY_RE = re.compile(r"\['?([^'\]]+)'?\]")


@dataclass
class Change:
    kind: str  # "missing" | "added" | "changed" | "type_changed"
    path: str
    key: str
    old: Any = None
    new: Any = None
    severity: str = "medium"


def _humanize_path(deepdiff_path: str) -> str:
    return deepdiff_path[len("root"):] if deepdiff_path.startswith("root") else deepdiff_path


def _last_key(path: str) -> str:
    matches = _PATH_KEY_RE.findall(path)
    return matches[-1] if matches else path


def compute_changes(baseline: dict, target: dict) -> list[Change]:
    """baseline = the environment that works (e.g. DEV); target = the one that's broken (e.g. QA)."""
    diff = DeepDiff(baseline, target, ignore_order=True, view="tree")

    changes: list[Change] = []

    for level in diff.get("dictionary_item_removed", []):
        path = _humanize_path(level.path(output_format="str"))
        changes.append(Change("missing", path, _last_key(path), old=level.t1, new=None,
                               severity=SEVERITY_BY_KIND["missing"]))

    for level in diff.get("dictionary_item_added", []):
        path = _humanize_path(level.path(output_format="str"))
        changes.append(Change("added", path, _last_key(path), old=None, new=level.t2,
                               severity=SEVERITY_BY_KIND["added"]))

    for level in diff.get("values_changed", []):
        path = _humanize_path(level.path(output_format="str"))
        changes.append(Change("changed", path, _last_key(path), old=level.t1, new=level.t2,
                               severity=SEVERITY_BY_KIND["changed"]))

    for level in diff.get("type_changes", []):
        path = _humanize_path(level.path(output_format="str"))
        changes.append(Change("type_changed", path, _last_key(path), old=level.t1, new=level.t2,
                               severity=SEVERITY_BY_KIND["type_changed"]))

    changes.sort(key=lambda c: SEVERITY_ORDER[c.severity])
    return changes
