# Dancie

Welcome to the game where you're supposed to dance. Now get up and move!

## Getting started

-   Clone the `dancie` repo
-   `cd` into the root directory

### My development process

-   Create a virtual environment in the root directory of `dancie`.

```
deactivate
python3 -m venv .venv && source .venv/bin/activate && pip install numpy adafruit-circuitpython-framebuf pillow watchfiles
```

-   Create emulator for rapid development

```bash
mkdir -p src/emulator
mkdir -p assets
touch src/emulator/**init**.py
touch src/emulator/ssd1306.py
touch src/simulate.py

brew install python-tk@3.11
curl -L https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_framebuf/main/examples/font5x8.bin -o assets/font5x8.bin
```

Make sure whenever you're using assets, you point to the `assets` folder.

-   Start developing

```
watchfiles "python src/simulate.py"
```
