from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from gi.repository import Gio, GLib, Gtk

DMS_CSS = Path.home() / ".config" / "gtk-4.0" / "dank-colors.css"
DMS_JSON = Path.home() / ".cache" / "DankMaterialShell" / "dms-colors.json"

HEX = re.compile(r"^#([0-9a-fA-F]{6})$")
DEFINE = re.compile(r"@define-color\s+([\w-]+)\s+([^;]+);")

PRESETS = {
    "dark": {
        "background": "#111318",
        "surface": "#181b21",
        "surface_high": "#23272f",
        "outline": "#747984",
        "text": "#f1f3f6",
        "accent": "#d8dee9",
        "on_accent": "#111318",
    },
    "rose": {
        "background": "#181215",
        "surface": "#241e22",
        "surface_high": "#2f282c",
        "outline": "#9b8d94",
        "text": "#ecdfe5",
        "accent": "#f6b2e0",
        "on_accent": "#4e1e44",
    },
    "mono": {
        "background": "#101010",
        "surface": "#1b1b1b",
        "surface_high": "#282828",
        "outline": "#8f8f8f",
        "text": "#eeeeee",
        "accent": "#ffffff",
        "on_accent": "#151515",
    },
}


def _hex_to_rgba(value: str, alpha: float) -> str:
    m = HEX.match(value.strip())
    if not m:
        return f"rgba(20,20,20,{alpha:.3f})"
    h = m.group(1)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.3f})"


def _parse_dms_css() -> dict[str, str] | None:
    if not DMS_CSS.exists():
        return None
    try:
        raw = DMS_CSS.read_text(encoding="utf-8")
    except OSError:
        return None

    values = {name: val.strip() for name, val in DEFINE.findall(raw)}
    def resolve(name: str, depth: int = 0) -> str | None:
        if depth > 8:
            return None
        val = values.get(name)
        if not val:
            return None
        if val.startswith("@"):
            return resolve(val[1:], depth + 1)
        return val if HEX.match(val) else None

    accent = resolve("accent_bg_color")
    on_accent = resolve("accent_fg_color")
    background = resolve("window_bg_color")
    text = resolve("window_fg_color")
    surface = resolve("card_bg_color") or resolve("view_bg_color")
    outline = resolve("theme_unfocused_fg_color") or text

    if not all([accent, on_accent, background, text, surface]):
        return None

    return {
        "background": background,
        "surface": surface,
        "surface_high": surface,
        "outline": outline or text,
        "text": text,
        "accent": accent,
        "on_accent": on_accent,
    }


def _parse_dms_json() -> dict[str, str] | None:
    if not DMS_JSON.exists():
        return None
    try:
        data = json.loads(DMS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    colors = data.get("colors", {})
    palette = colors.get("dark") or colors.get("light")
    if not isinstance(palette, dict):
        return None
    try:
        return {
            "background": palette["background"],
            "surface": palette["surface_container_high"],
            "surface_high": palette["surface_container_highest"],
            "outline": palette["outline"],
            "text": palette["on_surface"],
            "accent": palette["primary"],
            "on_accent": palette["on_primary"],
        }
    except KeyError:
        return None


def palette_for(theme: str) -> dict[str, str]:
    theme = theme.lower()
    if theme == "dms":
        return _parse_dms_css() or _parse_dms_json() or PRESETS["dark"]
    return PRESETS.get(theme, PRESETS["dark"])


def build_css(theme: str, opacity: float) -> str:
    p = palette_for(theme)
    bg = _hex_to_rgba(p["background"], opacity)
    surface = _hex_to_rgba(p["surface"], min(0.96, opacity + 0.08))
    outline = _hex_to_rgba(p["outline"], 0.58)
    accent_glow = _hex_to_rgba(p["accent"], 0.46)

    return f"""
window.gamekeys-window {{ background-color: transparent; }}
.hud {{
  background-color: {bg};
  border: 1px solid {outline};
  border-radius: 15px;
  padding: 10px;
  box-shadow: 0 4px 18px rgba(0,0,0,0.35);
}}
.keycap {{
  color: {p['text']};
  background-color: {surface};
  border: 1.5px solid {outline};
  border-radius: 8px;
  font-family: monospace;
  font-weight: 700;
  font-size: 15px;
  min-width: 42px;
  min-height: 38px;
  padding: 0 6px;
}}
.key-wide {{ min-width: 72px; }}
.key-space {{ min-width: 190px; }}
.keycap.pressed {{
  color: {p['on_accent']};
  background-color: {p['accent']};
  border-color: {p['accent']};
  box-shadow: 0 0 10px {accent_glow};
}}
.mouse-btn {{
  color: {p['text']};
  background-color: {surface};
  border: 1.5px solid {outline};
  font-family: monospace;
  font-weight: 700;
  font-size: 13px;
  min-width: 54px;
  min-height: 52px;
  padding: 0 4px;
}}
.mouse-left {{ border-radius: 22px 4px 4px 4px; }}
.mouse-right {{ border-radius: 4px 22px 4px 4px; }}
.mouse-btn.pressed {{
  color: {p['on_accent']};
  background-color: {p['accent']};
  border-color: {p['accent']};
  box-shadow: 0 0 10px {accent_glow};
}}
.mouse-body {{
  color: {p['text']};
  background-color: {surface};
  border: 1.5px solid {outline};
  border-radius: 4px 4px 26px 26px;
  font-family: monospace;
  font-weight: 700;
  font-size: 11px;
  min-height: 62px;
}}
.mouse-body.pressed {{
  color: {p['on_accent']};
  background-color: {p['accent']};
  border-color: {p['accent']};
  box-shadow: 0 0 10px {accent_glow};
}}
"""


class ThemeManager:
    def __init__(self, provider: Gtk.CssProvider, theme: str, opacity: float):
        self.provider = provider
        self.theme = theme
        self.opacity = opacity
        self._monitor: Gio.FileMonitor | None = None
        self._reload_source = 0

    def apply(self) -> None:
        self.provider.load_from_data(build_css(self.theme, self.opacity).encode("utf-8"))

    def start_monitor(self) -> None:
        if self.theme != "dms":
            return
        directory = DMS_CSS.parent
        directory.mkdir(parents=True, exist_ok=True)
        try:
            self._monitor = Gio.File.new_for_path(str(directory)).monitor_directory(
                Gio.FileMonitorFlags.NONE, None
            )
            self._monitor.connect("changed", self._on_changed)
        except GLib.Error:
            self._monitor = None

    def _on_changed(self, _monitor, file, _other, _event) -> None:
        if Path(file.get_path() or "").name != DMS_CSS.name:
            return
        if self._reload_source:
            GLib.source_remove(self._reload_source)
        self._reload_source = GLib.timeout_add(180, self._reload)

    def _reload(self) -> bool:
        self._reload_source = 0
        self.apply()
        return False
