"""SSD1306 desktop emulator that mimics CircuitPython's framebuf surface."""

import time
import tkinter as tk
from dataclasses import dataclass

from adafruit_framebuf import MVLSB, FrameBuffer
from PIL import Image, ImageTk


@dataclass
class EmulatorConfig:
    width: int = 128
    height: int = 64
    scale: int = 4  # how many desktop pixels per OLED pixel
    fps: int = 10  # throttle redraws to avoid pegging the CPU
    title: str = "SSD1306 Emulator"


class SSD1306Emulator(FrameBuffer):
    def __init__(self, config: EmulatorConfig | None = None):
        cfg = config or EmulatorConfig()
        self.width = cfg.width
        self.height = cfg.height
        self.scale = cfg.scale
        self._frame_interval = 1 / cfg.fps
        self._next_frame_time = 0.0

        self.buf = bytearray(self.width * self.height // 8)
        super().__init__(self.buf, self.width, self.height, MVLSB)

        self._root = tk.Tk()
        self._root.title(cfg.title)
        self._label = tk.Label(self._root, bd=0)
        self._label.pack()
        self._tk_image = None  # keep reference so Tk doesn’t GC it

    def show(self):
        now = time.perf_counter()
        if now < self._next_frame_time:
            self._root.update()
            return
        self._next_frame_time = now + self._frame_interval

        image = Image.frombytes(
            "L",  # <-- 8-bit grayscale to match our one-byte-per-pixel buffer
            (self.width, self.height),
            self._buffer_as_row_major(),
        ).convert("1")

        image = image.resize(
            (self.width * self.scale, self.height * self.scale),
            Image.NEAREST,
        )

        self._tk_image = ImageTk.PhotoImage(image)
        self._label.configure(image=self._tk_image)
        self._root.update_idletasks()
        self._root.update()

    def _buffer_as_row_major(self) -> bytes:
        out = bytearray(self.width * self.height)
        for x in range(self.width):
            column_offset = x
            for page in range(self.height // 8):
                byte = self.buf[column_offset + page * self.width]
                base_y = page * 8
                for bit in range(8):
                    if byte & (1 << bit):
                        out[(base_y + bit) * self.width + x] = 0xFF
        return bytes(out)

    def close(self):
        self._root.destroy()
