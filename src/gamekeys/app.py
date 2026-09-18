from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cairo
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import GLib, Gtk
from gi.repository import Gtk4LayerShell as LayerShell

from .config import CONFIG_FILE, Config, load_config
from .input import InputReader
from .theme import ThemeManager


class GameKeysApp(Gtk.Application):
    def __init__(self, config: Config):
        super().__init__(application_id="dev.gamekeys.Overlay")
        self.config = config
        self.widgets: dict[str, Gtk.Widget] = {}
        self.mouse_widgets: dict[str, Gtk.Widget] = {}
        self.reader: InputReader | None = None
        self.theme_manager: ThemeManager | None = None

    def do_activate(self) -> None:
        win = Gtk.ApplicationWindow(application=self)
        win.add_css_class("gamekeys-window")
        win.set_decorated(False)
        win.set_resizable(False)
        win.set_focusable(False)

        LayerShell.init_for_window(win)
        LayerShell.set_namespace(win, "gamekeys")
        LayerShell.set_layer(win, LayerShell.Layer.OVERLAY)
        LayerShell.set_keyboard_mode(win, LayerShell.KeyboardMode.NONE)
        LayerShell.set_exclusive_zone(win, 0)
        self._apply_position(win)

        provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(
            win.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.theme_manager = ThemeManager(provider, self.config.theme, self.config.opacity)
        self.theme_manager.apply()
        self.theme_manager.start_monitor()

        hud = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hud.add_css_class("hud")

        keyboard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        for row_def in self.config.keys:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            for key in row_def:
                label = "SPACE" if key == "Space" else key.upper() if len(key) == 1 else key
                widget = Gtk.Label(label=label)
                widget.add_css_class("keycap")
                if key in {"Tab", "Shift", "Ctrl"}:
                    widget.add_css_class("key-wide")
                if key == "Space":
                    widget.add_css_class("key-space")
                row.append(widget)
                self.widgets[key] = widget
            keyboard.append(row)
        hud.append(keyboard)

        if self.config.mouse:
            mouse = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            lmb = Gtk.Label(label="LMB")
            lmb.add_css_class("mouse-btn")
            lmb.add_css_class("mouse-left")
            rmb = Gtk.Label(label="RMB")
            rmb.add_css_class("mouse-btn")
            rmb.add_css_class("mouse-right")
            top.append(lmb)
            top.append(rmb)
            body = Gtk.Label(label="MMB\n●")
            body.add_css_class("mouse-body")
            mouse.append(top)
            mouse.append(body)
            self.mouse_widgets = {"LMB": lmb, "RMB": rmb, "MMB": body}
            hud.append(mouse)

        win.set_child(hud)
        win.connect("realize", self._make_click_through)
        win.connect("map", self._make_click_through)
        win.present()

        self.reader = InputReader(self._dispatch_input)
        self.reader.start()

    def _apply_position(self, win: Gtk.Window) -> None:
        pos = self.config.position.lower()
        top = pos.startswith("top")
        bottom = pos.startswith("bottom")
        left = pos.endswith("left")
        right = pos.endswith("right")
        LayerShell.set_anchor(win, LayerShell.Edge.TOP, top)
        LayerShell.set_anchor(win, LayerShell.Edge.BOTTOM, bottom)
        LayerShell.set_anchor(win, LayerShell.Edge.LEFT, left)
        LayerShell.set_anchor(win, LayerShell.Edge.RIGHT, right)
        if top:
            LayerShell.set_margin(win, LayerShell.Edge.TOP, self.config.margin_y)
        if bottom:
            LayerShell.set_margin(win, LayerShell.Edge.BOTTOM, self.config.margin_y)
        if left:
            LayerShell.set_margin(win, LayerShell.Edge.LEFT, self.config.margin_x)
        if right:
            LayerShell.set_margin(win, LayerShell.Edge.RIGHT, self.config.margin_x)

    @staticmethod
    def _make_click_through(win: Gtk.Window, *_args) -> None:
        surface = win.get_surface()
        if surface is not None:
            surface.set_input_region(cairo.Region())

    def _dispatch_input(self, name: str, pressed: bool) -> None:
        GLib.idle_add(self._set_pressed, name, pressed)

    def _set_pressed(self, name: str, pressed: bool) -> bool:
        widget = self.widgets.get(name) or self.mouse_widgets.get(name)
        if widget is None:
            return False
        if pressed:
            widget.add_css_class("pressed")
        else:
            widget.remove_css_class("pressed")
        return False

    def do_shutdown(self) -> None:
        if self.reader:
            self.reader.stop()
        Gtk.Application.do_shutdown(self)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GameKeys Wayland input overlay")
    parser.add_argument("--config", type=Path, default=CONFIG_FILE)
    parser.add_argument(
        "--position",
        choices=["top-left", "top-right", "bottom-left", "bottom-right"],
        help="Override configured position",
    )
    parser.add_argument("--theme", choices=["dms", "dark", "rose", "mono"], help="Override theme")
    parser.add_argument("--opacity", type=float, help="Override panel opacity (0.15-1.0)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = load_config(args.config)
    if args.position:
        config.position = args.position
    if args.theme:
        config.theme = args.theme
    if args.opacity is not None:
        config.opacity = max(0.15, min(1.0, args.opacity))
    app = GameKeysApp(config)
    return app.run([sys.argv[0]])


if __name__ == "__main__":
    raise SystemExit(main())
