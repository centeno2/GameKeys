from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

APP_NAME = "gamekeys"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "position": "bottom-left",
    "margin_x": 20,
    "margin_y": 20,
    "theme": "dms",
    "opacity": 0.72,
    "mouse": True,
    "keys": [
        ["Tab", "Q", "W", "E", "R"],
        ["Shift", "A", "S", "D", "F"],
        ["Ctrl", "Space"],
    ],
}


@dataclass
class Config:
    position: str = "bottom-left"
    margin_x: int = 20
    margin_y: int = 20
    theme: str = "dms"
    opacity: float = 0.72
    mouse: bool = True
    keys: list[list[str]] = field(default_factory=lambda: [
        ["Tab", "Q", "W", "E", "R"],
        ["Shift", "A", "S", "D", "F"],
        ["Ctrl", "Space"],
    ])


def _merge(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(DEFAULT_CONFIG)
    data.update(raw)
    return data


def load_config(path: Path | None = None) -> Config:
    path = path or CONFIG_FILE
    if not path.exists():
        save_default_config(path)
        raw: dict[str, Any] = {}
    else:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raw = {}

    data = _merge(raw)
    return Config(
        position=str(data["position"]),
        margin_x=int(data["margin_x"]),
        margin_y=int(data["margin_y"]),
        theme=str(data["theme"]),
        opacity=max(0.15, min(1.0, float(data["opacity"]))),
        mouse=bool(data["mouse"]),
        keys=data["keys"],
    )


def save_default_config(path: Path | None = None) -> None:
    path = path or CONFIG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
