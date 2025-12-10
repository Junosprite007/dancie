# Dancie

Welcome to the game where you're supposed to dance. Now get up and move!

## Table of Contents

-   [Hardware](#hardware)
-   [Game Overview](#game-overview)
-   [Console Layout](#console-layout)
-   [How to Play](#how-to-play)
-   [Gameplay Mechanics](#gameplay-mechanics)
-   [Scoring System](#scoring-system)
-   [Level Progression](#level-progression)
-   [Development Setup](#development-setup)

## Hardware

Here are all the pieces of hardware I'm using:

-   **Xiao ESP32-C3 Microcontroller**
-   **SSD1306 128x64 OLED screen**
-   **ADXL345 Accelerometer**
-   **Rotary Encoder** (with built-in button)
-   **3.7V LiPo Battery**
-   **6 NeoPixel LEDs** (connected to pin D3)
    -   1 LED: Power indicator (green)
    -   5 LEDs: Health indicators (purple)
-   **CD74HC4067 16-Channel Analog Multiplexer** (pins D8, D9, D10, A2)
-   **8 Limit Switches** (interfacing with the multiplexer channels 0-7)
-   **On/Off Switch**

## Game Overview

I've made a custom bitmap shape that is duplicated 8 times, each one rotating farther around an offset centerpoint. This results in a circular kaleidoscope shape on the screen. Each shape has its own hitbox in the center of its main design.

The game is a rhythm-based challenge where you press the correct buttons as shapes slide across the screen toward their targets, and tilt the accelerometer in response to arrow prompts. React quickly and accurately to score points and keep your health up!

## Console Layout

There are two cylindrical handles, each with 4 of the limit switches. The 8 total limit switches are used for the user's fingers to press.

1 of the 6 NeoPixel LEDs is simply an indicator light that turns green when the game console (the ESP32-C3) is turned on. The other 5 NeoPixel LEDs are "health" indicators for the game.

## How to Play

### Starting the Game

1. Power on the device using the on/off switch
2. The power indicator LED turns green
3. Watch the animated splash screen
4. Press the rotary encoder button to start

### During Gameplay

**Button Presses:**

-   Watch for shapes sliding in from the left or right side of the screen
-   Each shape targets one of the 8 map pieces in the kaleidoscope
-   Press the corresponding button (1-8) when the moving shape overlaps its target
-   The closer the alignment when you press, the more points you earn!

**Accelerometer Gestures:**

-   After every 7th shape, an arrow appears in the center (up, down, left, or right)
-   Tilt the accelerometer in the indicated direction
-   You have 2 seconds to respond (less time at higher levels)
-   Complete the gesture correctly to earn bonus points!

### Winning and Losing

**Health System:**

-   You start with 5 health (shown as 5 purple LEDs)
-   Missing a shape (it passes without you pressing the button) = lose 1 health
-   Missing or doing the wrong accelerometer gesture = lose 1 health
-   When all 5 health LEDs are gone, it's game over!

**Level Complete:**

-   Beat each level by completing all required shapes and gestures
-   Watch the victory LED animation!
-   Progress through all 10 levels to win the game

**Game Over:**

-   The screen displays "GAME OVER" and "Press Start to Restart"
-   Press the rotary encoder button to restart from level 1
-   No need to power cycle the device!

## Gameplay Mechanics

### Shape Movement

-   Shapes targeting the left side of the screen spawn from the left
-   Shapes targeting the right side of the screen spawn from the right
-   Each shape moves horizontally only, matching the Y position of its target
-   Shape speed increases with each level

### Button Mapping

-   Each of the 8 map pieces corresponds to one button (1-8)
-   Button 1 = Multiplexer channel 0
-   Button 2 = Multiplexer channel 1
-   ... and so on through button 8

### Gesture Prompts

-   Arrows appear after every 7th shape
-   Direction is random: up, down, left, or right
-   Time to respond decreases with each level
-   Gestures still appear while shapes continue moving in the background

## Scoring System

### Button Press Scoring

| Alignment Distance     | Points Awarded |
| ---------------------- | -------------- |
| Perfect (0 pixels off) | +5 points      |
| Great (1-2 pixels off) | +4 points      |
| Good (3-4 pixels off)  | +3 points      |
| OK (5-19 pixels off)   | +2 points      |
| Poor (20+ pixels off)  | -2 points      |
| Wrong button pressed   | -1 point       |

**Note:** Points are always whole numbers and score cannot go below 0.

### Gesture Scoring

-   **Correct gesture:** +5 points
-   **Wrong gesture or timeout:** -1 health (no points)

## Level Progression

There are **10 levels** total, with increasing difficulty:

### Events Per Level

Each level has **(14 shapes + 2 gestures) × level number**

Examples:

-   Level 1: 14 shapes + 2 gestures = 16 total events
-   Level 7: 98 shapes + 14 gestures = 112 total events
-   Level 10: 140 shapes + 20 gestures = 160 total events

### Difficulty Scaling

As you progress through levels:

-   **Shape speed increases** (linearly from 1.5 to 4.0 pixels/frame)
-   **Gesture time decreases** (linearly from 2.0 to 0.8 seconds)
-   More shapes and gestures to complete per level

## Development Setup

### Getting Started

Clone the `dancie` repo and `cd` into the root directory:

```bash
git clone <repo-url>
cd dancie
```
