# emulator/display.py
# import time
# import tkinter as tk

# from adafruit_framebuf import MONO_HLSB, FrameBuffer
# from PIL import Image, ImageTk
from splash_frames import SPLASH_FRAMES

SCALE = 4
WIDTH = 128
HEIGHT = 64

frames = []
for i in range(len(SPLASH_FRAMES)):
    lines = [line for line in SPLASH_FRAMES[i].strip().split("\n") if line]
    height = len(lines)
    width = len(lines[0])
    frames.append(
        dict({
            "lines": lines,
            "height": height,
            "width": width,
        })
    )

print(len(frames))


# class SSD1306Emulator(FrameBuffer):
#     def __init__(self):
#         self.buf = bytearray(WIDTH * HEIGHT // 8)
#         super().__init__(self.buf, WIDTH, HEIGHT, MONO_HLSB)
#         self._root = tk.Tk()
#         self._root.title("SSD1306 Emulator")
#         self._canvas = tk.Label(self._root)
#         self._canvas.pack()

#     def show(self):
#         img = Image.new("1", (WIDTH, HEIGHT))
#         img.frombytes(bytes(self.buf))
#         img = img.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.NEAREST)
#         self._tk_img = ImageTk.PhotoImage(img)
#         self._canvas.configure(image=self._tk_img)
#         self._root.update_idletasks()
#         self._root.update()


# if __name__ == "__main__":
#     disp = SSD1306Emulator()
#     disp.fill(0)
#     disp.line(0, 0, 127, 63, 1)
#     disp.rect(10, 10, 30, 20, 1, fill=True)
#     disp.text("Hello", 40, 28, 1)
#     while True:
#         disp.show()
#         time.sleep(0.05)
