#!/usr/bin/env bash
set -u

pass() { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m✗\033[0m %s\n' "$*"; }

printf 'GameKeys environment check\n\n'

if [[ "${XDG_SESSION_TYPE:-}" == "wayland" || -n "${WAYLAND_DISPLAY:-}" ]]; then
  pass "Wayland detected (${XDG_CURRENT_DESKTOP:-unknown desktop})"
else
  fail "Wayland not detected"
fi

if python3 - <<'PY' >/dev/null 2>&1
import cairo, evdev, gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, Gtk4LayerShell
PY
then
  pass "Python, GTK4, gtk4-layer-shell, PyCairo and evdev imports"
else
  fail "One or more runtime dependencies are missing"
fi

if find /dev/input -maxdepth 1 -type c -name 'event*' -readable -print -quit 2>/dev/null | grep -q .; then
  pass "Readable /dev/input/event* device found"
else
  warn "No readable /dev/input/event* device found"
fi

if [[ -f "$HOME/.cache/DankMaterialShell/dms-colors.json" || -f "$HOME/.config/gtk-4.0/dank-colors.css" ]]; then
  pass "DMS/Matugen palette detected"
else
  warn "DMS/Matugen not detected (optional; built-in themes still work)"
fi
