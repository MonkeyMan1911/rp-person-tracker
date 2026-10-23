from machine import ADC, Pin, PWM
import time

# --- Configuration & Tuning ---
ANGLE_SENSOR_0 = -45   # degrees from center (0 = servo's middle position)
ANGLE_SENSOR_1 = 45
ANGLE_REST = 0

# Servo pulse range. 0.5-2.5 ms covers most hobby servos.
# If the horn buzzes or hits its stops at the extremes, narrow these (try 0.6/2.4 or 1.0/2.0).
MIN_PULSE_MS = 0.5     # pulse for -90 degrees
MAX_PULSE_MS = 2.5     # pulse for +90 degrees

SERVO_SETTLE_S = 0.4   # pause after a move so the servo can arrive before reading sensors

# Consistency settings
REQUIRED_READINGS = 2
ERROR_MARGIN = 3  # cm

# Loops in a row with nothing detected before going back to ANGLE_REST
NO_DETECT_LOOPS = 10

# --- Hardware Initialization ---
sensors = [ADC(Pin(27)), ADC(Pin(26))]

servo = PWM(Pin(6))
servo.freq(50)

calibration = [
    (0.08495, 5), (0.16785, 10), (0.22420, 15), (0.27025, 20),
    (0.37630, 25), (0.41340, 30), (0.52155, 35), (0.57375, 40),
    (0.62400, 45), (0.68980, 50), (0.75625, 55), (0.84400, 60),
    (0.91745, 65), (0.96665, 70), (1.04145, 75), (1.10760, 80),
    (1.17860, 85), (1.24115, 90)
]

# --- Helper Functions ---
current_angle = ANGLE_REST

def set_angle(rel_deg):
    """Command the servo to rel_deg (-90 to +90, 0 = center) and hold it there."""
    rel_deg = max(-90, min(90, rel_deg))
    pulse_ms = MIN_PULSE_MS + (rel_deg + 90) / 180.0 * (MAX_PULSE_MS - MIN_PULSE_MS)
    servo.duty_u16(int(pulse_ms / 20.0 * 65535))

def move_to(target):
    global current_angle
    if target == current_angle:
        return
    set_angle(target)
    time.sleep(SERVO_SETTLE_S)
    current_angle = target

def get_voltage(sensor):
    total = 0
    for _ in range(20):
        total += sensor.read_u16()
        time.sleep_ms(2)
    raw = total / 20
    return raw * 3.3 / 65535

def get_distance(voltage):
    for i in range(len(calibration) - 1):
        v1, d1 = calibration[i]
        v2, d2 = calibration[i + 1]

        if v1 <= voltage <= v2:
            return d1 + (voltage - v1) * (d2 - d1) / (v2 - v1)

    return None

def readings_consistent(readings):
    if len(readings) < REQUIRED_READINGS:
        return False

    average = sum(readings) / len(readings)

    for reading in readings:
        if abs(reading - average) > ERROR_MARGIN:
            return False

    return True

# --- Startup ---
set_angle(ANGLE_REST)
time.sleep(1.0)

# Store recent readings
history_0 = []
history_1 = []
no_detect_count = 0

# --- Main Loop ---
print("Tracking started. Press Ctrl+C to stop.")

try:
    while True:
        d0 = get_distance(get_voltage(sensors[0]))
        d1 = get_distance(get_voltage(sensors[1]))

        # Add new readings to history
        if d0 is not None:
            history_0.append(d0)
            if len(history_0) > REQUIRED_READINGS:
                history_0.pop(0)
        else:
            history_0.clear()

        if d1 is not None:
            history_1.append(d1)
            if len(history_1) > REQUIRED_READINGS:
                history_1.pop(0)
        else:
            history_1.clear()

        # Count consecutive loops where neither sensor detects anything
        if d0 is None and d1 is None:
            no_detect_count += 1
        else:
            no_detect_count = 0

        # Check whether readings are consistent
        s0_consistent = readings_consistent(history_0)
        s1_consistent = readings_consistent(history_1)

        print(
            f"S0: {f'{d0:.1f}cm' if d0 is not None else 'Out of range'} "
            f"({'READY' if s0_consistent else 'waiting'}) | "
            f"S1: {f'{d1:.1f}cm' if d1 is not None else 'Out of range'} "
            f"({'READY' if s1_consistent else 'waiting'})"
        )

        # Only use a sensor if it has consistent readings
        valid_d0 = history_0[-1] if s0_consistent else None
        valid_d1 = history_1[-1] if s1_consistent else None

        # Determine target
        if valid_d0 is not None and valid_d1 is not None:
            target = ANGLE_SENSOR_0 if valid_d0 < valid_d1 else ANGLE_SENSOR_1

        elif valid_d1 is not None:
            target = ANGLE_SENSOR_1

        elif valid_d0 is not None:
            target = ANGLE_SENSOR_0

        elif no_detect_count >= NO_DETECT_LOOPS:
            # Nothing detected by either sensor for a while: return to rest
            target = ANGLE_REST

        else:
            # Readings still settling: hold position
            target = current_angle

        # Move only when the target changes
        if target != current_angle:
            print(f"-> Moving to {target} degrees")
            move_to(target)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nProgram stopped. Returning to rest.")
    set_angle(ANGLE_REST)
    time.sleep(0.5)
    servo.deinit()
