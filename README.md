# GameKeys

GameKeys is a lightweight keyboard and mouse input overlay for Linux Wayland. It is designed for gaming: keep a compact visual HUD on screen without OBS, while your keys and mouse buttons light up as you press them.

## Features

- Configurable keyboard overlay.
- `LMB`, `RMB` and `MMB` indicators.
- Keys and mouse buttons light up while pressed.
- GTK4 + `gtk4-layer-shell` overlay.
- Click-through and non-focusable.
- Four-corner positioning.
- Works above normal/fullscreen windows on compatible compositors.
- Dynamic DankMaterialShell / Matugen colors with live reload.
- Built-in fallback themes: `dark`, `rose`, `mono`.
- No autostart by default.
- `gamekeys doctor` diagnostics.

## Compatibility

GameKeys currently targets **Linux + Wayland** compositors that expose the layer-shell protocol used by `gtk4-layer-shell`.

### Tested

- Niri

### Expected to work

- Hyprland
- Sway
- River
- Wayfire
- KDE Plasma Wayland
- COSMIC and other compatible Wayland compositors

### Not currently supported

- GNOME Wayland without a compatible layer-shell solution
- X11 sessions
- Windows
- macOS

Only Niri is currently listed as tested by the project. Other compositors should be treated as community-test targets until confirmed.

## Requirements

Required runtime components:

- Linux
- Wayland session
- Python 3
- GTK 4
- `gtk4-layer-shell` plus its GObject introspection typelib
- PyGObject
- PyCairo
- `python-evdev`
- permission to read Linux input event devices (`/dev/input/event*`)

Optional:

- DankMaterialShell / Matugen for dynamic wallpaper/theme colors

If DMS/Matugen is not present, GameKeys automatically uses a built-in theme.

## Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/YOUR-USER/GameKeys.git
cd GameKeys
./scripts/install.sh
```

The installer:

1. checks whether the current session is Wayland;
2. detects the Linux distribution;
3. installs supported dependencies;
4. verifies GTK4, gtk4-layer-shell, PyGObject, PyCairo and evdev imports;
5. stops/migrates an older local GameKeys install if present;
6. installs GameKeys under the current user;
7. creates the desktop launcher;
8. configures active-session input access if `/dev/input/event*` is not readable;
9. detects DMS/Matugen and enables dynamic colors automatically.

### Supported automatic installers

#### Arch Linux and Arch-based distributions

Installed through `pacman`:

```text
python
python-gobject
python-cairo
gtk4
gtk4-layer-shell
python-evdev
```

This includes distributions such as Arch Linux, Garuda, CachyOS and other compatible Arch-based systems.

#### Recent Debian / Ubuntu releases

Installed through `apt`:

```text
python3
python3-gi
python3-cairo
python3-evdev
gir1.2-gtk-4.0
gir1.2-gtk4layershell-1.0
libgtk4-layer-shell0
```

On Ubuntu, the package may require the Universe repository to be enabled. Older Debian/Ubuntu releases that do not provide `gir1.2-gtk4layershell-1.0` are not supported by the automatic installer.

Other distributions can still run GameKeys after installing equivalent packages manually; automatic dependency installation is not implemented for them yet.

## Installed locations

```text
~/.local/share/gamekeys/
~/.local/bin/gamekeys
~/.config/gamekeys/config.json
~/.local/share/applications/gamekeys.desktop
```

A legacy development install at `~/.local/lib/gamekeys` is automatically moved to a timestamped backup under `~/.local/share/` during installation.

## Input permissions

GameKeys reads keyboard and mouse events using Linux evdev. It never needs to be run with `sudo`.

If the current user cannot read any `/dev/input/event*` device, the installer creates:

```text
/etc/udev/rules.d/70-gamekeys-uaccess.rules
```

This adds active-session `uaccess` permission. Existing devices may occasionally need to be unplugged/replugged or the user session restarted once after first installation.

## Usage

Toggle GameKeys on/off:

```bash
gamekeys
```

Other commands:

```bash
gamekeys start
gamekeys stop
gamekeys restart
gamekeys status
gamekeys logs
gamekeys doctor
```

Temporary overrides:

```bash
gamekeys restart --position bottom-right
gamekeys restart --theme rose
gamekeys restart --theme dms --opacity 0.78
```

## Diagnostics

Run:

```bash
gamekeys doctor
```

It checks:

- Wayland session detection;
- Python/GTK runtime dependencies;
- readable Linux input devices;
- DMS/Matugen dynamic palette availability.

The repository also includes a pre-install check:

```bash
./scripts/check.sh
```

## Configuration

User configuration lives at:

```text
~/.config/gamekeys/config.json
```

Default configuration:

```json
{
  "position": "bottom-left",
  "margin_x": 20,
  "margin_y": 20,
  "theme": "dms",
  "opacity": 0.72,
  "mouse": true,
  "keys": [
    ["Tab", "Q", "W", "E", "R"],
    ["Shift", "A", "S", "D", "F"],
    ["Ctrl", "Space"]
  ]
}
```

Supported positions:

```text
top-left
top-right
bottom-left
bottom-right
```

Built-in themes:

```text
dms
dark
rose
mono
```

## DMS / Matugen dynamic theme

When `theme` is `dms`, GameKeys looks for:

```text
~/.config/gtk-4.0/dank-colors.css
~/.cache/DankMaterialShell/dms-colors.json
```

The GTK color file is preferred because it reflects the palette currently applied to GTK. GameKeys monitors DMS color changes and reloads its CSS without restarting the overlay. If the integration is unavailable, it falls back safely to the built-in dark theme.

## Clean uninstall

Remove the application but keep your config:

```bash
./scripts/uninstall.sh
```

Completely remove GameKeys, its config and the optional udev rule:

```bash
./scripts/uninstall.sh --purge
```

## Clean-install test

For a release smoke test, clone the repository, remove the current local installation, reinstall from the clone and run diagnostics:

```bash
./scripts/uninstall.sh --purge
./scripts/install.sh
gamekeys doctor
gamekeys
```

Do this only from a local clone you can keep open, so the installer remains available after the installed copy is removed.

## Project structure

```text
GameKeys/
├── .github/workflows/compile.yml
├── assets/gamekeys.desktop
├── bin/gamekeys
├── scripts/
│   ├── check.sh
│   ├── install.sh
│   └── uninstall.sh
├── src/gamekeys/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── input.py
│   └── theme.py
├── config.example.json
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── README_ES.md
```

## Security note

GameKeys requires read access to input event devices to display global key/button state. Review the source and the udev rule before installation if using it on a shared or sensitive workstation. GameKeys does not need root privileges at runtime and does not intentionally record or persist input events.

## Roadmap

- GUI settings panel.
- More configurable key layouts.
- Per-game presets.
- More compositor testing.
- Additional distribution installers.
- Optional packaged releases / AUR package.

## License

MIT.
