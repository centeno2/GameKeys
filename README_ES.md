# GameKeys

GameKeys es un overlay ligero de teclado y mouse para **Linux Wayland**, pensado para jugar y ver en pantalla qué teclas y botones del mouse estás presionando sin depender de OBS.

## Funciones

- Teclado visual configurable.
- Indicadores `LMB`, `RMB` y `MMB`.
- Teclas y clics iluminados mientras se mantienen presionados.
- Overlay GTK4 + `gtk4-layer-shell`.
- Click-through: no roba clics ni foco.
- Posición configurable en las cuatro esquinas.
- Integración dinámica con DankMaterialShell/Matugen.
- Recarga de colores en vivo cuando cambia el wallpaper/tema.
- Temas de respaldo `dark`, `rose` y `mono`.
- No inicia automáticamente con el sistema.
- Diagnóstico con `gamekeys doctor`.

## Compatibilidad

### Probado

- Niri

### Se espera compatibilidad

- Hyprland
- Sway
- River
- Wayfire
- KDE Plasma Wayland
- COSMIC y otros compositores Wayland compatibles con layer-shell

### No soportado actualmente

- GNOME Wayland sin una solución compatible de layer-shell
- X11
- Windows
- macOS

Por ahora Niri es el único entorno marcado oficialmente como probado por el proyecto.

## Requisitos

Obligatorios:

- Linux
- sesión Wayland
- Python 3
- GTK 4
- `gtk4-layer-shell` + typelib de GObject Introspection
- PyGObject
- PyCairo
- `python-evdev`
- permiso para leer `/dev/input/event*`

Opcional:

- DankMaterialShell/Matugen para los colores dinámicos

Sin DMS/Matugen, GameKeys usa automáticamente un tema integrado.

## Instalación

```bash
git clone https://github.com/TU-USUARIO/GameKeys.git
cd GameKeys
./scripts/install.sh
```

El instalador hace automáticamente lo siguiente:

1. comprueba Wayland;
2. detecta la distribución;
3. instala dependencias;
4. verifica GTK4, Layer Shell, PyGObject, PyCairo y evdev;
5. detecta y respalda instalaciones antiguas de desarrollo;
6. instala GameKeys para el usuario actual;
7. crea el lanzador de aplicaciones;
8. configura acceso a `/dev/input/event*` si hace falta;
9. detecta DMS/Matugen y activa el tema dinámico.

### Arch / Garuda / CachyOS y derivados

Usa `pacman` para instalar:

```text
python
python-gobject
python-cairo
gtk4
gtk4-layer-shell
python-evdev
```

### Debian / Ubuntu recientes

Usa `apt` para instalar:

```text
python3
python3-gi
python3-cairo
python3-evdev
gir1.2-gtk-4.0
gir1.2-gtk4layershell-1.0
libgtk4-layer-shell0
```

En Ubuntu puede ser necesario tener habilitado el repositorio Universe. Las versiones antiguas que no empaqueten `gir1.2-gtk4layershell-1.0` no son compatibles con el instalador automático.

## Uso

```bash
gamekeys
```

El mismo comando funciona como ON/OFF.

También:

```bash
gamekeys start
gamekeys stop
gamekeys restart
gamekeys status
gamekeys logs
gamekeys doctor
```

Ejemplos:

```bash
gamekeys restart --position bottom-right
gamekeys restart --theme rose
gamekeys restart --theme dms --opacity 0.78
```

## Configuración

```text
~/.config/gamekeys/config.json
```

Configuración predeterminada:

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

## Tema dinámico DMS / Matugen

GameKeys detecta:

```text
~/.config/gtk-4.0/dank-colors.css
~/.cache/DankMaterialShell/dms-colors.json
```

Cuando DMS/Matugen cambia la paleta, GameKeys recarga los colores sin reiniciarse. Si esos archivos no existen, usa un tema integrado.

## Permisos de entrada

GameKeys usa evdev para leer el estado global del teclado y mouse. **No se ejecuta con sudo**.

Si el usuario no puede leer `/dev/input/event*`, el instalador crea una regla `uaccess` en:

```text
/etc/udev/rules.d/70-gamekeys-uaccess.rules
```

En algunos equipos puede ser necesario reconectar el teclado/mouse o cerrar e iniciar sesión una vez.

## Diagnóstico

```bash
gamekeys doctor
```

Comprueba Wayland, dependencias, permisos de input y disponibilidad de DMS/Matugen.

También puedes ejecutar desde el repositorio:

```bash
./scripts/check.sh
```

## Desinstalar

Manteniendo la configuración:

```bash
./scripts/uninstall.sh
```

Borrado completo, incluyendo configuración y regla udev:

```bash
./scripts/uninstall.sh --purge
```

## Prueba de instalación limpia

Desde un clon del repositorio:

```bash
./scripts/uninstall.sh --purge
./scripts/install.sh
gamekeys doctor
gamekeys
```

Esto permite comprobar que una instalación nueva funciona sin depender de los archivos que usamos durante el desarrollo.

## Seguridad

Para mostrar pulsaciones globales, GameKeys necesita acceso de lectura a dispositivos de entrada de Linux. No necesita privilegios root durante la ejecución y no está diseñado para guardar ni registrar permanentemente las pulsaciones.

## Licencia

MIT.
