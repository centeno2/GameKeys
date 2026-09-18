# GameKeys

Lightweight keyboard and mouse input overlay for Linux Wayland, designed for gaming without OBS.

## Features

- Keyboard + `LMB`, `RMB`, `MMB`.
- Keys light up while pressed.
- Click-through GTK4 layer-shell overlay.
- Works over fullscreen on compatible compositors.
- Four-corner positioning.
- Dynamic DankMaterialShell / Matugen colors.
- Built-in `dark`, `rose` and `mono` themes.
- True layer-shell overlay visible across workspaces.

## Compatibility

**Tested:** Niri.

**Expected:** Hyprland, Sway, River, Wayfire, KDE Plasma Wayland, COSMIC and other layer-shell compositors.

X11, Windows and macOS are not currently supported.

## Install

Clone the repository anywhere. GameKeys installs its runtime to `~/.local/share/gamekeys`.

```bash
git clone https://github.com/centeno2/GameKeys.git ~/Projects/GameKeys
cd ~/Projects/GameKeys
./scripts/install.sh
```

## Usage

```bash
gamekeys
gamekeys start
gamekeys stop
gamekeys status
gamekeys doctor
gamekeys logs
```
##view


<img width="536" height="190" alt="imagen" src="https://github.com/user-attachments/assets/349bbd67-2f35-4f14-844d-3a793eb55527" /> 
<img width="536" height="190" alt="imagen" src="https://github.com/user-attachments/assets/8a278e37-bc22-42ee-ac3e-ab36d78427e0" />



Examples:

```bash
gamekeys restart --position bottom-right
gamekeys restart --theme rose
gamekeys restart --theme dms --opacity 0.78
```

Config:

```text
~/.config/gamekeys/config.json
```

## Uninstall

```bash
gamekeys uninstall
gamekeys uninstall --purge
```

The cloned repository is not required after installation.

## License

MIT.
