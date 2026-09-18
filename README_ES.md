# GameKeys

Overlay ligero de teclado y mouse para Linux Wayland, pensado para jugar sin depender de OBS.

## Funciones

- Teclado + `LMB`, `RMB` y `MMB`.
- Las teclas se iluminan al presionarlas.
- Overlay GTK4 layer-shell, click-through.
- Visible sobre fullscreen en compositores compatibles.
- Posición en las cuatro esquinas.
- Colores dinámicos con DankMaterialShell / Matugen.
- Temas `dark`, `rose` y `mono`.
- Overlay layer-shell real, visible al cambiar entre workspaces.

## Compatibilidad

**Probado:** Niri.

**Esperado:** Hyprland, Sway, River, Wayfire, KDE Plasma Wayland, COSMIC y otros compositores con layer-shell.

Actualmente no soporta X11, Windows ni macOS.

## Instalación

Puedes clonar el repositorio en cualquier carpeta. La aplicación se instala en `~/.local/share/gamekeys`.

```bash
git clone https://github.com/centeno2/GameKeys.git ~/Projects/GameKeys
cd ~/Projects/GameKeys
./scripts/install.sh
```

## Uso

```bash
gamekeys
gamekeys start
gamekeys stop
gamekeys status
gamekeys doctor
gamekeys logs
```

Ejemplos:

```bash
gamekeys restart --position bottom-right
gamekeys restart --theme rose
gamekeys restart --theme dms --opacity 0.78
```

Configuración:

```text
~/.config/gamekeys/config.json
```

## Desinstalar

```bash
gamekeys uninstall
gamekeys uninstall --purge
```

No necesitas conservar el repositorio clonado después de instalar.

## Licencia

MIT.
