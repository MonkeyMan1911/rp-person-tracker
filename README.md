# Raspberry Pi Person Tracking System

## Table of Contents
1. Overview
2. Materials
3. Assembly and Wiring
4. Software Setup
5. Distance Sensor Calibration
6. How the Tracking Algorithm Works
7. Servo Position Control
8. Running the Program
9. Troubleshooting
10. Limitations
11. Project Files

## 1. Overview

This project uses a Raspberry Pi Pico 2 W, two analog distance sensors, and a positional servo to detect the approximate location of a person or object and turn toward the sensor detecting the closer target.

The two sensors are mounted side by side and monitor the distance in front of them. When a target is consistently detected by one sensor, the servo moves to the corresponding angle. If neither sensor detects a target for several consecutive loops, the servo returns to its resting position.

The project uses a **positional servo instead of a continuous-rotation servo**. This allows the program to command specific angles rather than estimating the servo's position from how long it has been rotating, reducing the position drift associated with timed movement.

## 2. Materials

- Raspberry Pi Pico 2 W
- Two Hummingbird analog distance sensors
- One Hummingbird positional servo
- Jumper wires
- USB cable and computer for programming
- Suitable power source for the Pico and servo
- Mounting materials to hold the sensors side by side and attach them to the servo

Check the specifications of the exact sensors and servo before connecting their power supplies.

## 3. Assembly and Wiring

Mount the two distance sensors next to each other, facing the area where the target is expected to appear. Attach the sensor assembly to the servo so that the servo can change the direction in which the sensors point.

### Pin connections

| Component | Pico connection |
|---|---|
| Distance sensor 0 analog output | GP27 (ADC) |
| Distance sensor 1 analog output | GP26 (ADC) |
| Servo control signal | GP6 (PWM) |
| Sensor power and ground | According to the sensor specifications |
| Servo power and ground | According to the servo specifications |

The code initializes the sensors using GP27 and GP26, in that order, and generates the servo control signal on GP6.

**Power safety:** Do not assume that the Pico's 3.3 V output can supply the servo's current requirements. Use an appropriate regulated supply if necessary, and connect the grounds together when the components use separate power supplies. Verify voltage compatibility before wiring the components.

## 4. Software Setup

The program is written in MicroPython and uses the Pico's built-in hardware interfaces.

The following modules are imported:

- `ADC` reads the analog distance sensors.
- `Pin` specifies the Pico GPIO pins.
- `PWM` generates the servo control signal.
- `time` provides delays and timing functions.

### Project file

The main program is `main.py`. The previous `servo_calibration.py` file is no longer required by the current program.

Connect the Pico to a computer, open the MicroPython-compatible development environment, and upload `main.py` to the Pico. Run the program and monitor its output through the serial console.

## 5. Distance Sensor Calibration

The program converts the analog voltage from each distance sensor into an estimated distance in centimeters.

### Calibration procedure

1. Place a flat piece of paper at a known distance from the sensor.
2. Take measurements at intervals of 5 cm.
3. Collect repeated readings at each distance and calculate their average.
4. Record the average voltage alongside the known distance.
5. Use the resulting calibration data in `main.py`.

The current calibration table covers distances from 5 cm to 90 cm.

| Distance (cm) | Calibrated voltage (V) |
|---:|---:|
| 5 | 0.08495 |
| 10 | 0.16785 |
| 15 | 0.22420 |
| 20 | 0.27025 |
| 25 | 0.37630 |
| 30 | 0.41340 |
| 35 | 0.52155 |
| 40 | 0.57375 |
| 45 | 0.62400 |
| 50 | 0.68980 |
| 55 | 0.75625 |
| 60 | 0.84400 |
| 65 | 0.91745 |
| 70 | 0.96665 |
| 75 | 1.04145 |
| 80 | 1.10760 |
| 85 | 1.17860 |
| 90 | 1.24115 |

Measurements at 95 cm were excluded because they did not produce consistent averages.

### Voltage-to-distance conversion

The program takes 20 ADC readings per measurement and averages them to reduce short-term fluctuations.

It then uses linear interpolation between adjacent calibration points to estimate the distance:

$$
d=d_1+\frac{V-V_1}{V_2-V_1}(d_2-d_1)
$$

Where:
- $V$ is the measured voltage.
- $V_1$ and $V_2$ are neighboring calibration voltages.
- $d_1$ and $d_2$ are their corresponding distances.
- $d$ is the estimated distance.

If the measured voltage falls outside the calibration range, the function returns `None`, which the program treats as an out-of-range reading.

## 6. How the Tracking Algorithm Works

The program repeatedly reads both sensors, checks whether their readings are consistent, and selects a target angle.

### Step 1: Read both sensors

Each sensor is sampled 20 times, with a short delay between samples. The average ADC value is converted into voltage and then into distance.

### Step 2: Check reading consistency

The program stores recent valid distance readings for each sensor.

A sensor becomes ready when it has two readings and both readings are within 3 cm of their average. If a reading falls outside the calibration range, that sensor's history is cleared.

These settings are defined by:

- `REQUIRED_READINGS = 2`
- `ERROR_MARGIN = 3`

### Step 3: Select a target angle

The program uses the most recent distance from each sensor once that sensor is ready.

| Condition | Target angle |
|---|---:|
| Sensor 0 is ready and detects the closer target | -45° |
| Sensor 1 is ready and detects the closer target | +45° |
| Only sensor 0 is ready | -45° |
| Only sensor 1 is ready | +45° |
| Neither sensor detects a target for 10 consecutive loops | 0° |
| Readings are not yet consistent | Hold the current position |

When both sensors are ready, the program selects the sensor reporting the shorter distance. If both report exactly the same distance, the code selects sensor 1's angle.

The program waits briefly between loops and only commands a new position when the target angle differs from the current commanded angle.

## 7. Servo Position Control

The project now uses a positional servo instead of the previous continuous-rotation servo.

### Position settings

The program defines three target positions:

- **-45°:** Sensor 0's direction
- **0°:** Center or resting position
- **+45°:** Sensor 1's direction

These angles are relative to the program's assumed center position.

### PWM control

The servo is initialized on GP6 at a frequency of 50 Hz. The `set_angle()` function converts a requested angle into a pulse width.

The current configuration is:

- `MIN_PULSE_MS = 0.5`
- `MAX_PULSE_MS = 2.5`

The code maps the requested angle from -90° to +90° onto that pulse-width range:

$$
t=t_{min}+\frac{\theta + 90}{180}(t_{max}-t_{min})
$$

Where:
- $t$ is the pulse width in milliseconds.
- $t_{min}$ is the minimum configured pulse width.
- $t_{max}$ is the maximum configured pulse width.
- $\theta$ is the requested angle.

The program then converts the pulse width into the duty cycle needed for the PWM signal.

After a movement command, the program waits 0.4 seconds to allow the servo to reach its requested position before continuing.

**Important:** The code assumes that the configured pulse range corresponds appropriately to the servo's movement range. The actual angle-to-pulse relationship depends on the servo. If the physical positions do not match the intended angles, adjust the pulse limits carefully according to the servo's specifications and test the endpoints without forcing the servo against its mechanical stops.

### Returning to rest

If neither sensor detects an in-range target for 10 consecutive loops, the program commands the servo to return to 0°. When the program is interrupted with Ctrl+C, it also commands the servo to return to rest before shutting down the PWM peripheral.

## 8. Running the Program

1. Check all wiring and confirm that the sensors and servo have suitable power.
2. Connect the Pico to the computer.
3. Open `main.py` in your MicroPython development environment.
4. Run the program.
5. Watch the serial console for the sensor readings and tracking status.

Example console output:

```text
Tracking started. Press Ctrl+C to stop.
S0: 24.8cm (waiting) | S1: 30.2cm (waiting)
S0: 25.1cm (READY) | S1: 29.7cm (READY)
-> Moving to -45 degrees
```

The numbers in this example are illustrative. Actual readings depend on the sensors and environment.

Press Ctrl+C to stop the program. It will attempt to return the servo to its resting position before deinitializing PWM.

## 9. Troubleshooting

**The sensor reports `Out of range`.**
- Check that the target is within the calibrated distance range.
- Check the sensor's power, ground, analog output, and wiring.
- Remember that voltages outside the calibration table are not converted into distances.

**The sensor remains in the `waiting` state.**
- Check whether readings are fluctuating by more than the 3 cm error margin.
- Verify that the sensor is stable and the target surface is suitable for measurement.
- Confirm that the sensor's output voltage changes as expected with distance.

**The servo moves to the wrong angle.**
- Verify that the sensors are assigned to the intended left and right directions.
- Check the physical orientation of the servo and sensor assembly.
- Verify the servo's pulse-width requirements and adjust the configured limits if necessary.

**The servo buzzes or reaches a mechanical stop.**
- Stop the program and check the servo's permitted movement range.
- Narrow the pulse range if the commanded positions exceed the servo's physical limits.
- Do not leave a servo continuously pressing against a mechanical stop.

**The Pico resets or the servo behaves erratically.**
- Check the servo power supply and current capacity.
- Ensure the grounds are connected where required.
- Check for loose wires and unstable power connections.

## 10. Limitations

- The system estimates distance from calibrated analog voltage; accuracy depends on the sensors, calibration, and environment.
- The current calibration covers 5–90 cm. Readings outside this range are treated as out of range.
- The system uses two discrete target angles rather than continuously calculating a target's direction.
- The servo's commanded angle is based on the configured PWM pulse mapping. The program does not independently measure the physical angle of the servo assembly.
- The program assumes the sensors are mounted in a consistent orientation and that their readings can be compared to choose the closer target.
- A target must produce consistent readings before the program responds, which can introduce a small delay.
- If neither sensor detects a valid target for long enough, the system returns to center even if the target is present but temporarily outside the calibration range.

## 11. Project Files

| File | Purpose |
|---|---|
| `main.py` | Initializes the sensors and positional servo, converts sensor readings into distances, checks consistency, selects target angles, and runs the tracking loop. |
| `rotate.py` | Tests servo rotation. |
| `distance_calibration.py` | Aids in distance sensor calibration by printing voltage values at a known distance.
| `distance_read.py` | Tests if distance readings post-calibration are accurate. You must put your own measured points into the calibration list. |

The previous `servo_calibration.py` file has been removed because the current program directly commands the positional servo using PWM pulse widths defined in `main.py`.
