#!/usr/bin/env bash
set -euo pipefail

PURGE=false
[[ "${1:-}" == "--purge" ]] && PURGE=true

BIN="$HOME/.local/bin/gamekeys"
RULE='/etc/udev/rules.d/70-gamekeys-uaccess.rules'

if [[ -x "$BIN" ]]; then
  "$BIN" stop >/dev/null 2>&1 || true
fi
pkill -f "$HOME/.local/lib/gamekeys/gamekeys.py" 2>/dev/null || true
rm -f "${XDG_RUNTIME_DIR:-/tmp}/gamekeys-${UID}.pid"

rm -rf "$HOME/.local/share/gamekeys"
rm -rf "$HOME/.local/lib/gamekeys"
rm -f "$BIN"
rm -f "$HOME/.local/share/applications/gamekeys.desktop"

if $PURGE; then
  rm -rf "$HOME/.config/gamekeys"
  if [[ -e "$RULE" ]]; then
    sudo rm -f "$RULE"
    sudo udevadm control --reload-rules
    sudo udevadm trigger --subsystem-match=input || true
  fi
  echo "GameKeys fully removed, including config and its optional udev rule."
else
  echo "GameKeys removed."
  echo "Your config was kept at: $HOME/.config/gamekeys/config.json"
  echo "For a completely clean removal:"
  echo "  ./scripts/uninstall.sh --purge"
fi
