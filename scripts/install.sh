#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HOME/.local/share/gamekeys"
LEGACY="$HOME/.local/lib/gamekeys"
BIN="$HOME/.local/bin"
APPS="$HOME/.local/share/applications"
CONFIG="$HOME/.config/gamekeys"
RULE='/etc/udev/rules.d/70-gamekeys-uaccess.rules'

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

check_session() {
  if [[ "${XDG_SESSION_TYPE:-}" == "x11" ]]; then
    die "GameKeys currently requires Wayland. This session reports X11."
  fi

  if [[ "${XDG_CURRENT_DESKTOP:-}" =~ [Gg][Nn][Oo][Mm][Ee] ]]; then
    warn "GNOME Wayland does not natively expose the layer-shell protocol GameKeys uses."
  fi

  if [[ "${XDG_SESSION_TYPE:-}" != "wayland" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    warn "A Wayland session was not detected. Installation can continue, but GameKeys will only run under Wayland."
  else
    ok "Wayland session detected"
  fi
}

read_os_release() {
  [[ -r /etc/os-release ]] || die "Cannot read /etc/os-release to detect the distribution."
  # shellcheck disable=SC1091
  . /etc/os-release
  DISTRO_ID="${ID:-unknown}"
  DISTRO_LIKE="${ID_LIKE:-}"
}

install_dependencies() {
  read_os_release
  info "Detected distribution: ${PRETTY_NAME:-$DISTRO_ID}"

  if command -v pacman >/dev/null 2>&1 || [[ "$DISTRO_ID $DISTRO_LIKE" =~ (arch|manjaro) ]]; then
    info "Installing Arch/Arch-based dependencies"
    sudo pacman -S --needed python python-gobject python-cairo gtk4 gtk4-layer-shell python-evdev
    return
  fi

  if command -v apt-get >/dev/null 2>&1 || [[ "$DISTRO_ID $DISTRO_LIKE" =~ (debian|ubuntu) ]]; then
    info "Installing Debian/Ubuntu dependencies"
    sudo apt-get update
    if ! sudo apt-get install -y \
      python3 python3-gi python3-cairo python3-evdev \
      gir1.2-gtk-4.0 gir1.2-gtk4layershell-1.0 libgtk4-layer-shell0; then
      cat >&2 <<'MSG'

Could not install gtk4-layer-shell packages.
On Ubuntu, make sure the Universe repository is enabled and try again.
GameKeys currently supports recent Debian/Ubuntu releases that provide
`gir1.2-gtk4layershell-1.0`.
MSG
      exit 1
    fi
    return
  fi

  cat >&2 <<MSG
Unsupported distribution for automatic dependency installation: ${PRETTY_NAME:-$DISTRO_ID}

Install these equivalents manually, then rerun the installer:
  Python 3
  PyGObject / GObject introspection
  PyCairo
  GTK 4
  gtk4-layer-shell + its GObject introspection typelib
  python-evdev
MSG
  exit 1
}

verify_dependencies() {
  info "Verifying Python/GTK dependencies"
  python3 - <<'PY'
from ctypes import CDLL
CDLL("libgtk4-layer-shell.so")

import cairo
import evdev
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, Gtk4LayerShell  # noqa: F401

print("Python imports OK")
PY
  ok "GTK4, gtk4-layer-shell, PyGObject, PyCairo and evdev are available"
}

stop_existing() {
  if [[ -x "$BIN/gamekeys" ]]; then
    "$BIN/gamekeys" stop >/dev/null 2>&1 || true
  fi
  pkill -f "$HOME/.local/lib/gamekeys/gamekeys.py" 2>/dev/null || true
  rm -f "${XDG_RUNTIME_DIR:-/tmp}/gamekeys-${UID}.pid"
}

migrate_legacy() {
  if [[ -d "$LEGACY" ]]; then
    local backup="$HOME/.local/share/gamekeys-legacy-backup-$(date +%Y%m%d-%H%M%S)"
    info "Legacy GameKeys install detected"
    mv "$LEGACY" "$backup"
    ok "Legacy files backed up to $backup"
  fi
}

install_files() {
  info "Installing GameKeys"
  mkdir -p "$DEST" "$BIN" "$APPS" "$CONFIG"
  rm -rf "$DEST/src"
  cp -r "$ROOT/src" "$DEST/src"
  install -Dm755 "$ROOT/bin/gamekeys" "$BIN/gamekeys"

  if [[ ! -f "$CONFIG/config.json" ]]; then
    cp "$ROOT/config.example.json" "$CONFIG/config.json"
    ok "Created default configuration"
  else
    ok "Existing configuration preserved"
  fi

  sed "s|@GAMEKEYS_BIN@|$BIN/gamekeys|g" "$ROOT/assets/gamekeys.desktop" > "$APPS/gamekeys.desktop"
  chmod 644 "$APPS/gamekeys.desktop"

  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS" >/dev/null 2>&1 || true
  fi
}

configure_input_access() {
  if find /dev/input -maxdepth 1 -type c -name 'event*' -readable -print -quit 2>/dev/null | grep -q .; then
    ok "Input event devices are readable by the current user"
    return
  fi

  info "Enabling active-session access to /dev/input/event*"
  printf '%s\n' 'SUBSYSTEM=="input", KERNEL=="event*", TAG+="uaccess"' | sudo tee "$RULE" >/dev/null
  sudo udevadm control --reload-rules
  sudo udevadm trigger --subsystem-match=input || true

  if find /dev/input -maxdepth 1 -type c -name 'event*' -readable -print -quit 2>/dev/null | grep -q .; then
    ok "Input access enabled"
  else
    warn "The udev rule was installed, but existing devices may need to be unplugged/replugged or the session restarted once."
  fi
}

report_optional_integrations() {
  if [[ -f "$HOME/.cache/DankMaterialShell/dms-colors.json" || -f "$HOME/.config/gtk-4.0/dank-colors.css" ]]; then
    ok "DankMaterialShell/Matugen palette detected: dynamic theme integration enabled"
  else
    info "DMS/Matugen not detected; built-in themes will be used automatically"
  fi
}

main() {
  check_session
  install_dependencies
  verify_dependencies
  stop_existing
  migrate_legacy
  install_files
  configure_input_access
  report_optional_integrations

  cat <<MSG

GameKeys installed successfully.

Commands:
  gamekeys                 Toggle ON/OFF
  gamekeys start           Start
  gamekeys stop            Stop
  gamekeys status          Status
  gamekeys logs            Show log
  gamekeys doctor          Check environment

Config:
  $CONFIG/config.json

Start it with:
  gamekeys
MSG
}

main "$@"
