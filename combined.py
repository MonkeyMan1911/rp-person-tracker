from machine import ADC, Pin, PWM
import time

# --- Configuration & Tuning ---
ANGLE_SENSOR_0 = -45
ANGLE_SENSOR_1 = 45
ANGLE_REST = 0

STOP_PULSE = 1.46
SLOW_CW_PULSE = 1.44
SLOW_CCW_PULSE = 1.48

SECONDS_PER_DEGREE = 0.06666666667

# Consistency settings
REQUIRED_READINGS = 4
ERROR_MARGIN = 3  # cm

# --- Hardware Initialization ---
sensors = [ADC(Pin(26)), ADC(Pin(27))]

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
current_angle = 0

def set_servo_pulse(ms):
    duty = int((ms / 20.0) * 65535)
    servo.duty_u16(duty)

def move_to(target):
    global current_angle
    delta = target - current_angle
    if delta == 0:
        return

    set_servo_pulse(SLOW_CCW_PULSE if delta > 0 else SLOW_CW_PULSE)
    time.sleep(abs(delta) * SECONDS_PER_DEGREE)
    set_servo_pulse(STOP_PULSE)

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
set_servo_pulse(STOP_PULSE)
time.sleep(0.5)

# Store recent readings
history_0 = []
history_1 = []

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

        # Check whether readings are consistent
        s0_consistent = readings_consistent(history_0)
        s1_consistent = readings_consistent(history_1)

        print(
            f"S0: {f'{d0:.1f}cm' if d0 is not None else 'Out of range'} "
            f"({'READY' if s0_consistent else 'waiting'}) | "
            f"S1: {f'{d1:.1f}cm' if d1 is not None else 'Out of range'} "
            f"({'READY' if s1_consistent else 'waiting'})"
        )

        # Only use a sensor if it has 4 consistent readings
        valid_d0 = history_0[-1] if s0_consistent else None
        valid_d1 = history_1[-1] if s1_consistent else None

        # Determine target
        if valid_d0 is not None and valid_d1 is not None:
            target = ANGLE_SENSOR_0 if valid_d0 < valid_d1 else ANGLE_SENSOR_1

        elif valid_d1 is not None:
            target = ANGLE_SENSOR_1

        elif valid_d0 is not None:
            target = ANGLE_SENSOR_0

        else:
            # No sensor has 4 consistent readings
            target = current_angle

        # Move only after consistency requirement is met
        if target != current_angle:
            print(f"-> Moving to {target} degrees, then stopping")
            move_to(target)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nProgram stopped. Returning to rest.")
    move_to(ANGLE_REST)
    set_servo_pulse(STOP_PULSE)
    servo.deinit()
