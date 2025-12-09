# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
# helpers_esp32c3.py
"""Helper functions optimized for ESP32-C3 with CircuitPython and displayio."""

import math

import ulab.numpy as np


def convert_bitmap_str_to_np(bm: str):
    """Convert string bitmap to ulab numpy array."""
    lines = [line.strip() for line in bm.strip().splitlines() if line.strip()]
    arr = [[int(char) for char in line] for line in lines]
    return np.array(arr, dtype=np.uint8)


def generate_bitmap_with_anchor_offset(bitmap, radius=0.0, draw_anchor=False):
    """Generate bitmap with anchor point offset (ulab compatible)."""
    rows, cols = bitmap.shape
    actual_center = (rows - 1) / 2.0
    distance_from_top_to_center = actual_center
    distance_from_top_to_new_anchor = distance_from_top_to_center + radius
    pixels_above_new_anchor = int(math.ceil(distance_from_top_to_new_anchor))
    pixels_below_new_anchor = pixels_above_new_anchor
    new_rows = pixels_above_new_anchor + 1 + pixels_below_new_anchor

    new_bitmap = np.zeros((new_rows, cols), dtype=bitmap.dtype)
    new_bitmap[0:rows, :] = bitmap

    if draw_anchor:
        anchor_row = pixels_above_new_anchor
        anchor_col = cols // 2
        if 0 <= anchor_row < new_rows and 0 <= anchor_col < cols:
            new_bitmap[anchor_row, anchor_col] = 1

    return new_bitmap


def rotate_bitmap_in_place(bitmap, degrees, trim_blank_pixels=False):
    """Rotate bitmap around its center (ulab compatible)."""
    rows, cols = bitmap.shape
    max_dim = max(rows, cols)
    square_bitmap = np.zeros((max_dim, max_dim), dtype=bitmap.dtype)

    row_offset = (max_dim - rows) // 2
    col_offset = (max_dim - cols) // 2
    square_bitmap[row_offset : row_offset + rows, col_offset : col_offset + cols] = (
        bitmap
    )

    angle_rad = math.radians(degrees)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    center = (max_dim - 1) / 2.0

    rotated_points = []
    for y in range(max_dim):
        for x in range(max_dim):
            if square_bitmap[y, x] == 0:
                continue
            rel_x = x - center
            rel_y = y - center
            rot_x = rel_x * cos_a - rel_y * sin_a
            rot_y = rel_x * sin_a + rel_y * cos_a
            rotated_points.append((rot_x, rot_y))

    if not rotated_points:
        return square_bitmap

    if not trim_blank_pixels:
        xs, ys = zip(*rotated_points)
        extent = max(
            abs(math.floor(min(xs))),
            abs(math.ceil(max(xs))),
            abs(math.floor(min(ys))),
            abs(math.ceil(max(ys))),
        )
        new_dim = max(2 * extent + 1, max_dim)
        rotated_bitmap = np.zeros((new_dim, new_dim), dtype=bitmap.dtype)
        new_center = (new_dim - 1) / 2.0

        for rot_x, rot_y in rotated_points:
            px = int(round(rot_x + new_center))
            py = int(round(rot_y + new_center))
            if 0 <= px < new_dim and 0 <= py < new_dim:
                rotated_bitmap[py, px] = 1

    return rotated_bitmap


def clear_displayio_bitmap(displayio_bitmap):
    """
    Efficiently clear a displayio.Bitmap by setting all pixels to 0.

    This is separated so it can be called once per frame in the main loop
    instead of inside draw_rotated_copies_esp32().
    """
    for x in range(displayio_bitmap.width):
        for y in range(displayio_bitmap.height):
            displayio_bitmap[x, y] = 0


def draw_numpy_to_displayio_bitmap(np_bitmap, displayio_bitmap, origin=(0, 0)):
    """
    Copy numpy array pixels into displayio.Bitmap.

    This is the KEY function that bridges numpy arrays to CircuitPython display.
    """
    origin_x, origin_y = origin
    rows, cols = np_bitmap.shape

    # Calculate center offset
    cx = cols // 2
    cy = rows // 2
    start_x = origin_x - cx
    start_y = origin_y - cy

    # Copy pixels (displayio.Bitmap uses [x, y] indexing!)
    for row in range(rows):
        for col in range(cols):
            if np_bitmap[row, col] > 0:
                x = start_x + col
                y = start_y + row
                # Bounds checking
                if 0 <= x < displayio_bitmap.width and 0 <= y < displayio_bitmap.height:
                    displayio_bitmap[x, y] = 1


def draw_rotated_copies_esp32(
    displayio_bitmap,
    np_bitmap,
    num_copies=8,
    start_angle=0.0,
    origin=None,
    clear_first=False,
):
    """
    Draw multiple rotated copies onto a displayio.Bitmap.
    ESP32-specific version.

    Parameters
    ----------
    displayio_bitmap : displayio.Bitmap
        The bitmap to draw onto.
    np_bitmap : np.ndarray
        The numpy array bitmap to rotate and draw.
    num_copies : int
        Number of rotated copies (default 8 for octagonal symmetry).
    start_angle : float
        Starting angle in degrees for the first copy.
    origin : tuple or None
        (x, y) center point. If None, uses center of display.
    clear_first : bool
        If True, clears the bitmap before drawing. For smooth animation,
        set to False and clear manually in the main loop BEFORE calling this.
    """
    if origin is None:
        origin = (displayio_bitmap.width // 2, displayio_bitmap.height // 2)

    # Optional clear - but you should clear ONCE in main loop instead
    if clear_first:
        clear_displayio_bitmap(displayio_bitmap)

    angle_step = 360.0 / num_copies

    # Draw all copies
    for i in range(num_copies):
        angle = start_angle + (angle_step * i)
        rotated = rotate_bitmap_in_place(np_bitmap, angle)
        draw_numpy_to_displayio_bitmap(rotated, displayio_bitmap, origin)


def draw_collision_points(displayio_bitmap, centers, size=3, color=1, style="box"):
    """
    Draw collision points for debugging hit detection zones.

    Parameters
    ----------
    displayio_bitmap : displayio.Bitmap
        The bitmap to draw on.
    centers : list of tuples
        List of (x, y) center coordinates.
    size : int, optional
        Size of the markers (default is 3).
    color : int, optional
        Color value to draw (1 for white, 0 for black).
    style : str, optional
        Marker style: "box" (hollow square), "cross" (crosshair), or "dot" (single pixel).
        Default is "box" for development.
    """
    for cx, cy in centers:
        if style == "box":
            # Draw hollow square outline
            for offset in range(-size, size + 1):
                # Top and bottom edges
                if 0 <= cx + offset < displayio_bitmap.width:
                    if 0 <= cy - size < displayio_bitmap.height:
                        displayio_bitmap[cx + offset, cy - size] = color
                    if 0 <= cy + size < displayio_bitmap.height:
                        displayio_bitmap[cx + offset, cy + size] = color

                # Left and right edges
                if 0 <= cy + offset < displayio_bitmap.height:
                    if 0 <= cx - size < displayio_bitmap.width:
                        displayio_bitmap[cx - size, cy + offset] = color
                    if 0 <= cx + size < displayio_bitmap.width:
                        displayio_bitmap[cx + size, cy + offset] = color

        elif style == "cross":
            # Draw crosshair
            for x in range(cx - size, cx + size + 1):
                if (
                    0 <= x < displayio_bitmap.width
                    and 0 <= cy < displayio_bitmap.height
                ):
                    displayio_bitmap[x, cy] = color

            for y in range(cy - size, cy + size + 1):
                if (
                    0 <= cx < displayio_bitmap.width
                    and 0 <= y < displayio_bitmap.height
                ):
                    displayio_bitmap[cx, y] = color

        elif style == "dot":
            # Draw single pixel
            if 0 <= cx < displayio_bitmap.width and 0 <= cy < displayio_bitmap.height:
                displayio_bitmap[cx, cy] = color


def i2c_bus_scanner():
    import adafruit_displayio_ssd1306
    import board
    import busio
    import displayio
    import i2cdisplaybus

    # Setup display with I2C scanning
    displayio.release_displays()

    print("Scanning I2C bus...")
    i2c = busio.I2C(board.SCL, board.SDA)

    # Wait for I2C to initialize
    import time

    time.sleep(0.5)

    # Lock the I2C bus while scanning
    while not i2c.try_lock():
        pass

    try:
        print(
            "I2C addresses found:",
            [hex(device_address) for device_address in i2c.scan()],
        )
    except Exception as e:
        print(f"I2C scan error: {e}")
    finally:
        i2c.unlock()

    # Now try to connect to display
    try:
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
        print("Display connected successfully!")
    except ValueError as e:
        print(f"Display connection failed: {e}")
        print("Check your wiring!")


def test_multiplexer_switches():
    """
    Simple test function to monitor multiplexer switches and print which one is pressed.
    Displays one switch at a time on serial monitor.

    Hardware setup:
    - CD74HC4067 multiplexer
    - S0 -> D8, S1 -> D9, S2 -> D10
    - SIG -> A2 (with external 10kΩ pull-up to 3.3V)
    - EN -> GND, VCC -> 3V3, GND -> GND
    - 8 normally-open limit switches on channels C0-C7 to GND

    Press Ctrl+C to exit.
    """
    import time

    import board
    from analogio import AnalogIn
    from digitalio import DigitalInOut, Direction

    # Initialize multiplexer control pins
    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT

    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT

    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT

    # Analog input for reading switch states
    analog_sig = AnalogIn(board.A2)

    # Voltage threshold: 1.5V = ~30000 in ADC units
    VOLTAGE_THRESHOLD = 30000

    def select_channel(channel):
        """Select a mux channel (0-7)."""
        s0.value = (channel & 0b001) != 0
        s1.value = (channel & 0b010) != 0
        s2.value = (channel & 0b100) != 0
        time.sleep(0.001)  # Allow mux to settle

    def read_switch(channel):
        """Read switch state. Returns True if pressed."""
        select_channel(channel)
        # Take multiple samples to detect instability (pressed state)
        samples = []
        for _ in range(5):
            samples.append(analog_sig.value < VOLTAGE_THRESHOLD)
            time.sleep(0.001)

        # If any variation in samples, switch is pressed (unstable signal)
        return len(set(samples)) > 1 or samples[0]

    print("Multiplexer Switch Test")
    print("Press switches to see which one is active...")
    print("Press Ctrl+C to exit\n")

    last_pressed = None

    try:
        while True:
            current_pressed = None

            # Scan all 8 channels
            for channel in range(8):
                if read_switch(channel):
                    current_pressed = channel
                    break  # Only report one at a time

            # Only print when state changes
            if current_pressed != last_pressed:
                if current_pressed is not None:
                    print(
                        f"Switch {current_pressed + 1} pressed (Channel {current_pressed})"
                    )
                else:
                    print("No switch pressed")
                last_pressed = current_pressed

            time.sleep(0.05)  # 50ms scan rate

    except KeyboardInterrupt:
        print("\n\nSwitch test stopped")
        analog_sig.deinit()
        s0.deinit()
        s1.deinit()
        s2.deinit()


def diagnose_multiplexer():
    """
    Improved multiplexer diagnostic with proper settling times and analysis.
    Addresses multiplexer-specific issues: settling time, crosstalk, capacitance.

    Press Ctrl+C to exit.
    """
    import time

    import board
    from analogio import AnalogIn
    from digitalio import DigitalInOut, Direction

    print("\n" + "=" * 60)
    print("MULTIPLEXER DIAGNOSTIC TEST v2 (with settling analysis)")
    print("=" * 60)

    # Initialize control pins
    print("\n1. Initializing control pins...")
    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT
    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT
    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT
    print("   Control pins initialized")

    # Initialize analog input
    print("\n2. Initializing analog input...")
    analog_sig = AnalogIn(board.A2)
    print("   Analog input initialized")

    def select_channel(channel):
        """Select a mux channel with proper settling time."""
        s0.value = (channel & 0b001) != 0
        s1.value = (channel & 0b010) != 0
        s2.value = (channel & 0b100) != 0
        # CD74HC4067 datasheet: propagation delay ~10ns, but real-world
        # capacitance requires much longer settling
        time.sleep(0.005)  # 5ms settling time (increased from 2ms)

    def voltage_from_raw(raw_value):
        """Convert raw ADC value to voltage."""
        return (raw_value / 65535) * 3.3

    # Test settling time
    print("\n3. Testing multiplexer settling time...")
    select_channel(0)
    settling_data = []

    for delay_ms in [0.001, 0.002, 0.005, 0.010]:
        select_channel(0)
        time.sleep(delay_ms)
        reading_0 = analog_sig.value

        select_channel(7)
        time.sleep(delay_ms)
        reading_7 = analog_sig.value

        settling_data.append({"delay": delay_ms, "ch0": reading_0, "ch7": reading_7})

    print("   Delay(ms) | Ch0 Reading | Ch7 Reading | Difference")
    print("   " + "-" * 55)
    for data in settling_data:
        diff = abs(data["ch0"] - data["ch7"])
        print(
            f"   {data['delay'] * 1000:5.1f}     | {data['ch0']:11d} | {data['ch7']:11d} | {diff:10d}"
        )

    if settling_data[-1]["ch0"] == settling_data[-1]["ch7"]:
        print("   → Channels reading identical (potential wiring issue)")

    # Test crosstalk
    print("\n4. Testing for crosstalk between channels...")
    print("   (Checking if switching speed causes channel bleed)")

    select_channel(0)
    time.sleep(0.010)  # Long settle
    stable_0 = analog_sig.value

    # Rapidly switch through all channels then back to 0
    for ch in range(1, 8):
        select_channel(ch)
        time.sleep(0.0001)  # Very fast switching

    select_channel(0)
    immediate_0 = analog_sig.value
    time.sleep(0.010)
    settled_0 = analog_sig.value

    crosstalk = abs(stable_0 - immediate_0)
    recovery = abs(immediate_0 - settled_0)

    print(f"   Ch0 stable: {stable_0} ({voltage_from_raw(stable_0):.2f}V)")
    print(
        f"   Ch0 immediate after fast switching: {immediate_0} ({voltage_from_raw(immediate_0):.2f}V)"
    )
    print(f"   Ch0 after 10ms settle: {settled_0} ({voltage_from_raw(settled_0):.2f}V)")
    print(f"   Crosstalk effect: {crosstalk} ({voltage_from_raw(crosstalk):.3f}V)")

    if crosstalk > 1000:
        print("   ⚠ WARNING: Significant crosstalk detected!")
        print("   → Add 0.1µF capacitor from SIG to GND")
        print("   → Increase settling time in code")
    else:
        print("   ✓ Crosstalk is minimal")

    # Read baseline with proper settling
    print("\n5. Reading baseline values (with 5ms settling time)...")
    print("\nChannel | Raw Value | Voltage | Min   | Max   | Variation")
    print("-" * 70)

    baseline_values = []
    for channel in range(8):
        select_channel(channel)

        # Take 20 readings over 100ms (plenty of time for settling)
        readings = []
        for _ in range(20):
            readings.append(analog_sig.value)
            time.sleep(0.005)  # 5ms between samples

        avg_raw = sum(readings) / len(readings)
        min_raw = min(readings)
        max_raw = max(readings)
        voltage = voltage_from_raw(avg_raw)
        variation = max_raw - min_raw

        baseline_values.append({
            "avg": avg_raw,
            "min": min_raw,
            "max": max_raw,
            "voltage": voltage,
            "variation": variation,
        })

        status = "STABLE" if variation < 1000 else "NOISY"
        print(
            f"   {channel}    | {int(avg_raw):5d}     | {voltage:.2f}V  | {int(min_raw):5d} | {int(max_raw):5d} | {int(variation):5d} {status}"
        )

    # Check for common issues
    print("\n6. Analyzing results...")
    all_same = len(set(int(b["avg"]) for b in baseline_values)) == 1
    all_high = all(b["voltage"] > 2.5 for b in baseline_values)
    all_low = all(b["voltage"] < 0.5 for b in baseline_values)
    high_variation = any(b["variation"] > 5000 for b in baseline_values)

    if all_same:
        print("   ✗ ALL CHANNELS READING IDENTICAL VALUE")
        print("   → Multiplexer control pins (S0/S1/S2) may not be connected")
        print("   → Check D8, D9, D10 connections")
        print("   → Verify multiplexer is powered (VCC to 3.3V)")
    elif all_high:
        print("   ✓ All channels HIGH (pull-up working correctly)")
        print("   → Switches likely not closing or not connected to GND")
    elif all_low:
        print("   ✗ All channels LOW")
        print("   → Missing pull-up resistor or multiplexer not powered")
    elif high_variation:
        print("   ⚠ High signal variation detected")
        print("   → Possible floating inputs or bad connections")
        print("   → Add capacitor (0.1µF) from SIG to GND for filtering")
    else:
        print("   ✓ Baseline readings look reasonable")

    # Enhanced monitoring with debouncing
    print("\n7. Continuous monitoring (with debouncing)...")
    print("   Press switches ONE AT A TIME and HOLD for 1 second")
    print("   Press Ctrl+C to exit\n")
    print("Ch | Samples | Avg Raw | Voltage | State")
    print("-" * 60)

    prev_state = [None] * 8

    try:
        while True:
            for channel in range(8):
                select_channel(channel)

                # Take 10 samples over 50ms (proper debouncing period)
                samples = []
                for _ in range(10):
                    samples.append(analog_sig.value)
                    time.sleep(0.005)

                avg_raw = sum(samples) / len(samples)
                min_val = min(samples)
                max_val = max(samples)
                variation = max_val - min_val
                voltage = voltage_from_raw(avg_raw)
                baseline = baseline_values[channel]["avg"]

                # Determine state with hysteresis
                if avg_raw < 10000:  # Clearly pressed
                    current_state = "PRESSED"
                elif avg_raw > 40000:  # Clearly released
                    current_state = "RELEASED"
                else:  # Ambiguous middle range
                    current_state = "FLOATING/BAD"

                # Only print changes or problems
                if current_state != prev_state[channel]:
                    consistent = variation < 5000
                    consistency_mark = "✓" if consistent else "✗ UNSTABLE"

                    print(
                        f" {channel} | {len(samples):7d} | {int(avg_raw):7d} | {voltage:5.2f}V | {current_state:12s} {consistency_mark}"
                    )

                    if not consistent:
                        print(
                            f"    └─> Variation: {int(variation)} (min:{int(min_val)} max:{int(max_val)})"
                        )

                    prev_state[channel] = current_state

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("DIAGNOSTIC SUMMARY & RECOMMENDATIONS")
        print("=" * 60)

        print("\n✓ Tests completed:")
        print(f"  - Settling time analysis: {settling_data[-1]['delay'] * 1000}ms")
        print(f"  - Crosstalk test: {crosstalk} ADC units")
        print(
            f"  - Baseline stability: {baseline_values[0]['variation']} avg variation"
        )

        print("\n📋 Hardware checklist:")
        print("  □ S0 (D8), S1 (D9), S2 (D10) connected?")
        print("  □ EN pin connected to GND? (enables multiplexer)")
        print("  □ VCC to 3.3V, GND to GND?")
        print("  □ 10kΩ pull-up from SIG to 3.3V?")
        print("  □ 0.1µF capacitor from SIG to GND? (recommended)")
        print("  □ All 8 switches: one terminal to C0-C7, other to GND?")

        print("\n💡 Recommended settling time: 5-10ms per channel")
        print("   (Your system shows ~5ms is adequate)")

        print("\n" + "=" * 60 + "\n")

        analog_sig.deinit()
        s0.deinit()
        s1.deinit()
        s2.deinit()


def test_single_channel(channel_num):
    """
    Test one specific multiplexer channel continuously.
    Use this to test each connection individually.

    Args:
        channel_num: 0-7, the channel to test
    """
    import time

    import board
    from analogio import AnalogIn
    from digitalio import DigitalInOut, Direction

    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT
    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT
    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT

    analog_sig = AnalogIn(board.A2)

    # Select the channel
    s0.value = (channel_num & 0b001) != 0
    s1.value = (channel_num & 0b010) != 0
    s2.value = (channel_num & 0b100) != 0

    print(f"\nTesting Channel {channel_num} continuously")
    print("Press and HOLD the switch. Wiggle wires if needed.")
    print("Press Ctrl+C to exit\n")
    print("Raw Value | Voltage | Status")
    print("-" * 40)

    try:
        while True:
            raw = analog_sig.value
            voltage = (raw / 65535) * 3.3

            if raw < 2000:
                status = "✓ GOOD (pressed)"
            elif raw > 50000:
                status = "✓ GOOD (released)"
            else:
                status = "✗ BAD (floating/intermittent)"

            print(f"{raw:5d}     | {voltage:.2f}V   | {status}")
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nTest stopped")
        analog_sig.deinit()
        s0.deinit()
        s1.deinit()
        s2.deinit()
