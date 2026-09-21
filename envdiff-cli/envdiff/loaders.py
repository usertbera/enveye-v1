from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_snapshot(path: str | Path) -> dict:
    """Load an env/config snapshot from .env, .yaml/.yml, or .json (default)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".env" or path.name.startswith(".env"):
        return _load_dotenv(path)
    if suffix in (".yaml", ".yml"):
        return yaml.safe_load(path.read_text()) or {}
    return json.loads(path.read_text())


def _load_dotenv(path: Path) -> dict:
    result: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result
