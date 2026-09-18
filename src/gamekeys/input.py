from __future__ import annotations

import select
import threading
import time
from collections import defaultdict
from typing import Callable

from evdev import InputDevice, ecodes, list_devices

KEY_MAP = {
    ecodes.KEY_TAB: "Tab",
    ecodes.KEY_Q: "Q",
    ecodes.KEY_W: "W",
    ecodes.KEY_E: "E",
    ecodes.KEY_R: "R",
    ecodes.KEY_LEFTSHIFT: "Shift",
    ecodes.KEY_RIGHTSHIFT: "Shift",
    ecodes.KEY_A: "A",
    ecodes.KEY_S: "S",
    ecodes.KEY_D: "D",
    ecodes.KEY_F: "F",
    ecodes.KEY_LEFTCTRL: "Ctrl",
    ecodes.KEY_RIGHTCTRL: "Ctrl",
    ecodes.KEY_SPACE: "Space",
}

MOUSE_MAP = {
    ecodes.BTN_LEFT: "LMB",
    ecodes.BTN_RIGHT: "RMB",
    ecodes.BTN_MIDDLE: "MMB",
}

ALL_CODES = set(KEY_MAP) | set(MOUSE_MAP)


class InputReader:
    def __init__(self, callback: Callable[[str, bool], None]):
        self.callback = callback
        self.running = False
        self.thread: threading.Thread | None = None
        self._pressed_codes: set[int] = set()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True, name="gamekeys-input")
        self.thread.start()

    def stop(self) -> None:
        self.running = False

    @staticmethod
    def _open_devices() -> list[InputDevice]:
        devices: list[InputDevice] = []
        for path in list_devices():
            try:
                dev = InputDevice(path)
                keys = dev.capabilities().get(ecodes.EV_KEY, [])
                if any(code in ALL_CODES for code in keys):
                    devices.append(dev)
                else:
                    dev.close()
            except (PermissionError, OSError):
                continue
        return devices

    def _emit_for_code(self, code: int) -> None:
        name = KEY_MAP.get(code) or MOUSE_MAP.get(code)
        if not name:
            return
        mapping = KEY_MAP if code in KEY_MAP else MOUSE_MAP
        pressed = any(c in self._pressed_codes for c, n in mapping.items() if n == name)
        self.callback(name, pressed)

    def _loop(self) -> None:
        while self.running:
            devices = self._open_devices()
            if not devices:
                time.sleep(2.0)
                continue
            try:
                while self.running:
                    readable, _, _ = select.select(devices, [], [], 1.5)
                    for dev in readable:
                        try:
                            for event in dev.read():
                                if event.type != ecodes.EV_KEY or event.code not in ALL_CODES:
                                    continue
                                if event.value == 0:
                                    self._pressed_codes.discard(event.code)
                                else:
                                    self._pressed_codes.add(event.code)
                                self._emit_for_code(event.code)
                        except OSError:
                            raise
            except (OSError, ValueError):
                pass
            finally:
                for dev in devices:
                    try:
                        dev.close()
                    except OSError:
                        pass
                self._pressed_codes.clear()
            time.sleep(0.5)
