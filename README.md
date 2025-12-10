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

Here are all the pieces of hardware I'm using:

Xiao ESP323C Microcontroller
SSD1306 128x64 OLED screen
ADXL345 Accelerometer
Rotary Encoder
3.7 V LiPo Battery
6 NeoPixel LEDs
CD74HC4067 16 Channel Analog Multiplexer
8 limit switches (interfacing with the multiplexer)
On/Off Switch

You can look at my whole project to see what I have so far, but let me first explain the game.

## Game setup

I've made a custom bitmap shape that is duplicated 8 times, each one rotating farther around an offset centerpoint. This results in a circular shape on the screen. Each shape has it's own hitbox in the center of its main design.

## Consol layout

There are two cylidrical handles, each with 4 of the limit switches. The 8 total limit switches that are used for the user's fingers to press.

1 of the 6 NeoPixel LEDs is simply an indicator light that turns green when the game console (the ESP32-C3) is turned on. The other 5 NeoPixel LEDs are "health" indicators for the game.

## User input & gameplay

User presses the 8 limit switches, depending on the shape that move onto the screen. For example, the user must press limit switch #1 (mux channel 0) when moving-shape-type-1 is over lapping some part of map-shape-type-1's hitbox. You get point based on how close the two shapes are perfectly aligned when you press the button. Pressing the wrong button for the moving shape that's overlapping it's map shape counterpart substract 1 point. You get 5 points for a perfectly overlapping shape. Points MUST only be whole numbers.

Intermitently, a left, right, up, or down arrow will appear in the center of the screen. When that happens, the user will have 2 seconds to tilt the accelerometer in the left or right direction, depending on which arrow appeared. An arrow appears after every seventh shape, but the direction of the arrow that appears should be random every time. Users get 5 points for doing the correct movement, but if the user doesn't do the correct movement within 2 seconds, they lose 1 health, which is then indecated on the "Health" LEDs.

The 5 Health NeoPixel LEDs start out purple. When you miss an overlapping shape, the last (5th) LED turns off completely. When you miss a second overlapping shape, the 4th LED turns off. Missing an overlapping shape simply means the shape overlapped completely, but the user did not press the corresponding swith in time. When the user misses 5 overlaps, meaning all 5 Health LEDs have turned off, the game is over.

The screen displays "Game Over" on the top of the screen and "Press Start to Reply" on the bottom of the screen. The "Start" button is the the button that's built in to the rotary encoder.

The user should be able to restart the game without needing to power cycle the device.

There are 10 levels, and as you increase in levels, the shapes move faster, and you have less time to do the accelerometer gestures. Each level has (14 shapes + 2 accelerometer gestures) * the level, so if you're on level 7, for example, there would be (14*7) + (2\*7) = 112 total shapes and gestures (98 moving shapes and 14 gestures)

When the user either gets "Game Over" or beats a level, the system check to see if their score was high enough to get on the High Score Board, the user uses the rotary encoder to select alphanumaric characters, and pressing the built-in button on the rotary encoder to select each character. High Score Board names can only be a max of 20 characters. The new high score is then written to a file called `high_score_board.txt` on the ESP32.
