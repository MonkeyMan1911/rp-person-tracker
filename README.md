# Raspberry Pi Person Tracking System

A simple person-tracking project that uses two analog distance sensors and a continuous-rotation servo to turn an attached mount toward a detected person.

**Project status:** Assembly and software testing in progress
**Microcontroller:** Raspberry Pi Pico 2 W
**Programming language:** MicroPython

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Materials](#2-materials)
3. [Assembly and Wiring](#3-assembly-and-wiring)
4. [Software Setup](#4-software-setup)
5. [Sensor Calibration](#5-sensor-calibration)
6. [Servo Calibration](#6-servo-calibration)
7. [How the Tracking Algorithm Works](#7-how-the-tracking-algorithm-works)
8. [Running the Program](#8-running-the-program)
9. [Troubleshooting](#9-troubleshooting)
10. [Known Limitations](#10-known-limitations)
11. [Project Files](#11-project-files)

---

## 1. Project Overview

The purpose of this project is to create a simple tracking mechanism that turns a mounted attachment toward a person based on readings from two distance sensors.

The system uses two Hummingbird 3.3 V analog distance sensors connected to a Raspberry Pi Pico 2 W. Each sensor measures the distance to an object by producing an analog voltage. The Pico converts this voltage into an estimated distance using previously collected calibration measurements.

The program compares the readings from both sensors and uses a continuous-rotation servo to turn the mount toward the sensor detecting the closer object.

### Main Features

- Two analog distance sensors for detecting nearby objects.
- Sensor calibration using measurements collected at 5 cm intervals.
- Averaging of multiple analog readings to reduce measurement noise.
- A consistency check requiring four readings within a 3 cm tolerance.
- Automatic servo direction control based on sensor readings.
- A timed servo movement system that estimates its current position.

**Important:** The intended behavior is described here, but the complete system has not yet been tested. Successful person tracking, mechanical performance, and actual accuracy remain to be verified.

## 2. Materials

### Hardware

- Raspberry Pi Pico 2 W
- Breadboard
- Two Hummingbird 3.3 V analog distance sensors
- One 360° continuous-rotation servo
- MicroUSB data cable
- Computer

### Assembly Materials

- 3D printer, or cardboard and craft materials for a mount
- Measuring tape or ruler
- A piece of paper for measuring and marking distances

### Software

- Visual Studio Code
- MicroPico VS Code extension
- MicroPython firmware on the Pico

**Note:** Alternative components may work, but their wiring, voltage requirements, and code may differ.

## 3. Assembly and Wiring

### 3.1 Connecting the Distance Sensors

Both sensors connect to the Pico's analog-capable GPIO pins.

| Component wire | Raspberry Pi Pico 2 W connection |
|---|---|
| Sensor 0 power (VCC) | 3V3(OUT), pin 36 |
| Sensor 0 ground (GND) | GND |
| Sensor 0 analog output | GP26, physical pin 31 |
| Sensor 1 power (VCC) | 3V3(OUT), pin 36 |
| Sensor 1 ground (GND) | GND |
| Sensor 1 analog output | GP27, physical pin 32 |

The code identifies these connections as follows:

```python
sensors = [ADC(Pin(26)), ADC(Pin(27))]
```

The first sensor is referred to as Sensor 0, and the second is Sensor 1.

**Wiring verification:** These connections assume that the sensors accept a 3.3 V supply and output an analog voltage that stays within the Pico's ADC input range of 0–3.3 V. Confirm the sensor's pinout and electrical specifications before connecting it.

### 3.2 Connecting the Servo

| Servo connection | Connection |
|---|---|
| Signal wire | GP6, physical pin 9 |
| Power wire | A suitable supply for the servo's voltage and current requirements |
| Ground wire | Supply ground, connected to Pico GND |

The code initializes the servo using:

```python
servo = PWM(Pin(6))
servo.freq(50)
```

The servo receives a 50 Hz PWM signal from GPIO 6.

**Power safety:** Do not assume the servo can be powered from the Pico's 3.3 V output. Use a suitable external regulated supply if required by the servo's specifications. Connect the external supply's ground to the Pico's ground so that the control signal has a common reference. Do not connect an external supply's positive output to the Pico's 3V3 pin.

### 3.3 Physical Assembly

1. Place the Raspberry Pi Pico at the edge of the breadboard, leaving access to its USB port.
2. Connect both distance sensors according to the wiring tables.
3. Mount the sensors side by side, facing forward in their intended sensing directions.
4. Connect the servo's signal and power wiring.
5. Attach the servo to the tracking mount.
6. Secure the sensors to the mount so that their positions and orientations remain consistent.
7. Check that the mount can rotate without hitting the breadboard, wires, or other objects.

**Mechanical note:** The sensors' exact orientation and spacing will affect which objects they detect. The physical arrangement should be tested before relying on the tracking algorithm.

## 4. Software Setup

### 4.1 Prerequisites

Install Visual Studio Code and the MicroPico extension. The Pico must be running compatible MicroPython firmware.

### 4.2 Connecting to the Pico

1. Open Visual Studio Code.
2. Open the project directory containing the Python files.
3. Connect the Pico to the computer using a MicroUSB data cable.
4. Confirm that the MicroPico extension recognizes the board.
5. Open the integrated terminal or MicroPython REPL.

If the board is connected correctly, you should be able to execute commands on the Pico.

### 4.3 Running a Python File

1. Open the Python file you want to run.
2. Open the Command Palette using `Ctrl+Shift+P` on Windows/Linux or `Cmd+Shift+P` on macOS.
3. Search for `MicroPico: Run Current File on Board`.
4. Select the command.
5. Observe the output in the terminal.

Repeat these steps for the calibration scripts and the main tracking program as needed.

## 5. Sensor Calibration

### 5.1 Purpose

The distance sensors produce analog voltages rather than direct distance measurements. Calibration establishes the relationship between the voltage reported by a sensor and the distance to an object.

The calibration process uses measurements collected at 5 cm intervals, from 5 cm through 90 cm. A piece of paper was used as the target, and its distance from the sensor was measured manually.

The recorded measurements were saved in a file named `measurements.txt`.

### 5.2 Collecting Measurements

The script used for collecting distance calibration measurements is `distance_calibration.py`.

The process is:

1. Place the paper at a known distance from the sensor, starting at 5 cm.
2. Run `distance_calibration.py`.
3. Enter the known distance when prompted.
4. Allow the script to collect multiple voltage readings.
5. Record the reported average voltage in `measurements.txt`.
6. Repeat the process at 10 cm, 15 cm, and every subsequent 5 cm interval.
7. Continue through 90 cm.
8. At 95 cm, readings did not produce consistent averages, so this distance was excluded from the active calibration table.

The sensor should remain in the same orientation throughout calibration. The paper should be positioned consistently, and the distance should be measured from a consistent reference point.

### 5.3 Calibration Measurements

The following table contains the recorded calibration data. Voltage values are in volts.

| Distance | Average voltage |
|---:|---:|
| 5 cm | 0.084950 |
| 10 cm | 0.167850 |
| 15 cm | 0.224200 |
| 20 cm | 0.270250 |
| 25 cm | 0.376300 |
| 30 cm | 0.413400 |
| 35 cm | 0.521550 |
| 40 cm | 0.573750 |
| 45 cm | 0.624000 |
| 50 cm | 0.689800 |
| 55 cm | 0.756250 |
| 60 cm | 0.844000 |
| 65 cm | 0.917450 |
| 70 cm | 0.966650 |
| 75 cm | 1.041450 |
| 80 cm | 1.107600 |
| 85 cm | 1.178600 |
| 90 cm | 1.241150 |
| 95 cm | Approximately 2 V; inconsistent readings |

The 95 cm measurement is included for documentation only. It is not used by the current program.

### 5.4 The `measurements.txt` File

The measurements were recorded in the following format:

```text
05cm - 0.08494999
10cm - 0.16785
15cm - 0.224200016
20cm - 0.27024996
25cm - 0.37630004
30cm - 0.413400032
35cm - 0.52155
40cm - 0.57375
45cm - 0.624
50cm - 0.689799936
55cm - 0.75625
60cm - 0.844
65cm - 0.91744995
70cm - 0.9666501
75cm - 1.04145
80cm - 1.1076
85cm - 1.1786
90cm - 1.2411499
95cm - ~2 but no consistent averages
```

This file serves as a record of the measurements. The current tracking program does not read `measurements.txt` automatically; the values are copied into the `calibration` list in `main.py`.

### 5.5 How `distance_calibration.py` Works

The script reads the analog voltage using the Pico's ADC.

```python
raw = sensor.read_u16()
voltage = raw * 3.3 / 65535
```

The Pico's `read_u16()` method returns a value from 0 to 65535. This value is converted into an estimated voltage using the 3.3 V ADC reference.

The script collects multiple readings and calculates an average to reduce the effect of measurement fluctuations.

**Implementation note:** The supplied script performs 21 readings because it loops over `range(21)`, but divides the accumulated voltage by 20. For an accurate average, change the loop to `range(20)` or divide by the actual number of readings. The script also rounds individual voltages to three decimal places before accumulating them, which reduces precision.

### 5.6 Applying the Calibration Data

In `main.py`, calibration data is stored as pairs of voltage and distance:

```python
calibration = [
    (0.08495, 5),
    (0.16785, 10),
    (0.22420, 15),
    (0.27025, 20),
    # Additional measurements...
    (1.24115, 90)
]
```

Each pair follows this order:

```python
(voltage, distance_in_cm)
```

This is the reverse of the order in which the measurements are presented in `measurements.txt`.

### 5.7 Converting Voltage into Distance

The `get_distance(voltage)` function finds the two calibration points surrounding a measured voltage and estimates the distance using linear interpolation.

The formula is:

\[
d=d_1+\frac{V-V_1}{V_2-V_1}(d_2-d_1)
\]

Where:

- \(d\) is the estimated distance.
- \(V\) is the measured voltage.
- \(V_1,V_2\) are the surrounding calibration voltages.
- \(d_1,d_2\) are their corresponding distances.

For example, if a voltage falls between the measurements collected at 20 cm and 25 cm, the program estimates a distance between those two values.

If the voltage falls outside the calibration range, the function returns `None`. This prevents the program from treating an out-of-range voltage as a valid distance.

**Limitation:** Linear interpolation assumes that voltage changes approximately linearly between adjacent calibration points. It does not guarantee accurate measurements, particularly near the ends of the calibrated range.

## 6. Servo Calibration

### 6.1 Purpose

The project uses a 360° continuous-rotation servo. Unlike a standard positional servo, it is controlled by the direction and speed associated with its control pulses rather than by requesting a specific absolute angle.

The program uses timed rotation to estimate the amount of movement. Calibration helps determine how long the servo must run to rotate approximately one degree.

### 6.2 Pulse Configuration

The servo settings are defined in `servo_calibration.py` and `main.py`.

```python
STOP_PULSE = 1.46
SLOW_CW_PULSE = 1.44
SLOW_CCW_PULSE = 1.48

SECONDS_PER_DEGREE = 0.06666666667
```

The pulse values are expressed in milliseconds.

| Constant | Purpose |
|---|---|
| `STOP_PULSE` | Pulse duration intended to stop the servo |
| `SLOW_CW_PULSE` | Pulse duration intended to rotate clockwise |
| `SLOW_CCW_PULSE` | Pulse duration intended to rotate counterclockwise |
| `SECONDS_PER_DEGREE` | Estimated rotation time per degree |

These are initial calibration values, not guaranteed settings for every servo. The actual stop point, direction, and rotation speed depend on the hardware.

### 6.3 Calibrating the Rotation Rate

The `servo_calibration.py` script includes a `calibrate()` function that runs the servo counterclockwise for a specified duration.

The procedure is:

1. Secure the servo and ensure that the mount can rotate safely.
2. Start with a short test duration.
3. Run the servo and measure the approximate number of degrees it rotates.
4. Stop the servo and record the elapsed time and measured rotation.
5. Calculate the rotation time per degree.
6. Update `SECONDS_PER_DEGREE`.
7. Repeat the test to check consistency.

The calculation is:

\[
\text{SECONDS\_PER\_DEGREE}
=\frac{\text{elapsed time in seconds}}
{\text{degrees rotated}}
\]

For example, if the servo rotates approximately 30° in 2 seconds:

\[
\frac{2}{30}\approx0.0667
\text{ seconds per degree}
\]

This is the value currently used by the program.

**Important:** The supplied `servo_calibration.py` defines `calibrate()` but does not call it. To perform the test, the function must be invoked explicitly, for example:

```python
calibrate(seconds=2)
```

Make sure the mount has enough clearance before running the test.

### 6.4 Adjusting the Pulse Values

The stop, clockwise, and counterclockwise pulse values may also need to be adjusted through trial and error.

1. Run the servo using the proposed stop pulse.
2. Check whether the servo stops rotating.
3. Adjust the pulse slightly if the servo continues to creep.
4. Test each direction at a low speed.
5. Verify which pulse corresponds to clockwise and counterclockwise movement.
6. Update the constants in `main.py`.

The exact pulse duration at which a continuous-rotation servo stops varies between units. The value `1.46` milliseconds is an initial setting, not a universal stop value.

### 6.5 How `main.py` Estimates Position

The tracking program stores its estimated angle in:

```python
current_angle = 0
```

When it receives a target angle, the `move_to()` function calculates the difference between the target and the current estimate. It then runs the servo for the corresponding amount of time.

```python
delta = target - current_angle
```

The program estimates the required rotation duration as:

```python
time.sleep(abs(delta) * SECONDS_PER_DEGREE)
```

After the delay, it sends the stop pulse and updates `current_angle`.

This method assumes that the servo rotates at a consistent speed. It does not measure the actual physical angle, and errors can accumulate over repeated movements.

## 7. How the Tracking Algorithm Works

The main program is stored in `main.py`.

### 7.1 Sensor Initialization

Both sensors are initialized using the ADC pins GP26 and GP27. The servo is initialized on GP6 with a 50 Hz PWM frequency.

At startup, the program sends the stop pulse and waits briefly before beginning the tracking loop.

### 7.2 Reading and Averaging Voltages

For each sensor, the program collects 20 ADC readings and averages them.

```python
for _ in range(20):
    total += sensor.read_u16()
    time.sleep_ms(2)
```

The average is converted to voltage, and the calibration table is used to estimate distance.

Averaging reduces short-term fluctuations, although it cannot eliminate all measurement errors.

### 7.3 Requiring Four Consistent Readings

The program uses these settings:

```python
REQUIRED_READINGS = 4
ERROR_MARGIN = 3
```

Each sensor maintains a history of its most recent four valid distance readings.

A sensor becomes ready when:

1. Four valid readings have been collected.
2. Their average has been calculated.
3. Every reading is within 3 cm of that average.

If a reading is outside the calibrated voltage range, that sensor's history is cleared.

This helps prevent the servo from reacting immediately to a single unstable measurement.

**Clarification:** The 3 cm tolerance is measured against the average of the four readings, not against the previous reading or a known true distance.

### 7.4 Choosing a Target

The program selects a target based on which sensors have consistent readings.

| Sensor state | Program behavior |
|---|---|
| Neither sensor is ready | Keep the current estimated angle |
| Only Sensor 0 is ready | Target `ANGLE_SENSOR_0` (-45°) |
| Only Sensor 1 is ready | Target `ANGLE_SENSOR_1` (45°) |
| Both are ready and Sensor 0 reports a shorter distance | Target -45° |
| Both are ready and Sensor 1 reports a shorter distance | Target 45° |
| Both are ready and report equal distances | Target 45° |

The last case follows from the comparison in the supplied code: if Sensor 0 is not closer than Sensor 1, the program selects Sensor 1.

### 7.5 Moving the Servo

The servo turns toward the selected target only when the target differs from the current estimated angle.

The program uses timed movement to approximate the requested rotation and then sends the stop pulse.

It repeats the sensor-reading process approximately every 0.05 seconds, in addition to the time spent collecting sensor samples and moving the servo.

### 7.6 Stopping the Program

Press `Ctrl+C` in the REPL or terminal to interrupt the program.

The `KeyboardInterrupt` handler attempts to return the servo to the estimated rest position of 0°, sends the stop pulse, and deinitializes the PWM output.

Because the servo is continuous rotation and has no angle feedback, the return-to-rest movement is only an estimate. It is not a guarantee that the mount will physically return to exactly 0°.

## 8. Running the Program

### 8.1 Recommended Order

1. **Check the wiring.** Confirm the sensor supply voltage, ADC connections, servo signal, and common ground.
2. **Run `distance_calibration.py`.** Verify that the sensor produces plausible voltage readings.
3. **Review `measurements.txt`.** Confirm that the recorded measurements correspond to the intended distances.
4. **Run `servo_calibration.py`.** Test the servo's stop pulse, directions, and approximate rotation speed.
5. **Update the constants.** Apply the verified pulse values and rotation estimate to `main.py`.
6. **Position the sensors.** Secure both sensors side by side and check their sensing directions.
7. **Run `main.py`.** Watch the REPL output for sensor distances and readiness indicators.
8. **Test with a stationary target.** Place an object at a known distance in front of each sensor and observe the response.
9. **Test the complete mount.** Verify that the servo moves in the intended direction and stops safely.

### 8.2 Understanding the Terminal Output

The main program prints output similar to:

```text
Tracking started. Press Ctrl+C to stop.
S0: 25.1cm (waiting) | S1: 40.2cm (waiting)
S0: 24.9cm (waiting) | S1: 40.1cm (waiting)
S0: 25.0cm (READY) | S1: 40.0cm (READY)
-> Moving to -45 degrees, then stopping
```

The values above are illustrative examples, not verified test results.

- `S0` and `S1` identify the two sensors.
- The distance is the estimate calculated from the calibration table.
- `waiting` means the sensor has not met the consistency requirement.
- `READY` means the four-reading consistency check has passed.
- The movement message identifies the target angle requested by the program.

## 9. Troubleshooting

### 9.1 Sensor Readings Are `None` or Out of Range

**Possible causes:**

- The measured voltage is below the lowest calibration voltage or above the highest one.
- The sensor is wired incorrectly.
- The sensor supply voltage is incorrect.
- The target is outside the sensor's reliable operating range.

**What to do:**

1. Run `distance_calibration.py`.
2. Check the raw ADC values and voltage readings.
3. Verify the sensor's power, ground, and output connections.
4. Compare the measured voltage with the calibration table.
5. Repeat calibration if the sensor's output differs substantially from the recorded values.

### 9.2 The Sensor Never Becomes Ready

**Possible causes:**

- The measurements fluctuate by more than the allowed 3 cm.
- The sensor is pointed at an inconsistent target.
- The target is moving.
- The voltage-to-distance calibration is inaccurate.

**What to do:**

1. Keep a stationary object at a fixed distance.
2. Check whether the printed distances fluctuate significantly.
3. Confirm that the calibration data matches the sensor being used.
4. Verify that the program receives four valid readings.

The tolerance should only be changed after observing the actual measurement noise.

### 9.3 The Servo Does Not Stop

**Possible causes:**

- The stop pulse is not calibrated for the particular servo.
- The pulse value is being interpreted differently than expected.
- The servo is receiving unstable power.

**What to do:**

1. Verify the servo's voltage and current requirements.
2. Confirm that the Pico and servo supply share a common ground.
3. Adjust `STOP_PULSE` in small increments.
4. Test the stop pulse without the tracking mount attached if necessary.

### 9.4 The Servo Turns in the Wrong Direction

**Possible causes:**

- The clockwise and counterclockwise pulse values are reversed for the servo.
- The physical sensor arrangement does not match the intended angle mapping.

**What to do:**

1. Test each direction independently.
2. Confirm which sensor is connected to GP26 and which is connected to GP27.
3. Check the sensor mounting orientation.
4. Adjust the pulse assignments or angle mapping in `main.py` if required.

### 9.5 The Servo Does Not Point Accurately

**Possible causes:**

- The estimated rotation rate is inaccurate.
- The servo speed changes with load or supply voltage.
- The servo drifts while stopped.
- Timing errors accumulate across repeated movements.

**What to do:**

1. Repeat the rotation-rate calibration.
2. Check the stop pulse and direction settings.
3. Observe whether the mount drifts after multiple movements.
4. Recalibrate after making mechanical changes.

Without a physical angle sensor, the program cannot correct its estimated position using the servo's actual position.

### 9.6 The Servo or Pico Resets Unexpectedly

**Possible causes:**

- The servo draws more current than the supply can provide.
- The wiring is loose.
- The supply voltage drops when the servo starts moving.

**What to do:**

1. Disconnect power before changing wiring.
2. Verify that the servo has an appropriate power supply.
3. Check ground connections.
4. Inspect the wiring for shorts and loose connections.
5. Avoid powering a servo from the Pico's 3.3 V output unless the hardware specifications explicitly support the load.

## 10. Known Limitations

The following limitations are known from the supplied code or remain to be verified during testing.

### 10.1 Calibration Range

The active calibration table covers 5–90 cm. The program does not extrapolate outside that range, so out-of-range voltages produce no distance estimate.

### 10.2 Sensor Accuracy

The recorded calibration values were obtained using a piece of paper at manually measured distances. Measurement uncertainty, target positioning, and sensor characteristics may affect the results.

### 10.3 Servo Position Estimation

The current angle is tracked in software using elapsed time. There is no physical angle sensor or encoder to confirm the actual position.

### 10.4 Target Selection

The program selects between two fixed target angles, -45° and 45°. It does not calculate a continuous angle from the person's location.

### 10.5 Detection Versus Person Recognition

The system responds to distance measurements. It does not identify whether an object is a person. Any object that produces suitable sensor readings may trigger the same behavior.

### 10.6 Testing Status

The complete project has not yet been tested. The tracking logic and wiring described here are based on the supplied code and setup information. Actual tracking accuracy, mechanical reliability, and long-term behavior remain unverified.

## 11. Project Files

| File | Purpose |
|---|---|
| `servo_calibration.py` | Contains the servo pulse settings and a function for estimating rotation time per degree. |
| `distance_calibration.py` | Collects analog voltage measurements at known distances. |
| `measurements.txt` | Stores the recorded distance and average voltage measurements. |
| `main.py` | Reads both sensors, estimates distances, checks consistency, and controls the servo. |

### File Relationships

The calibration workflow is:

1. Run `distance_calibration.py` to collect voltage measurements.
2. Record the measurements in `measurements.txt`.
3. Copy the verified voltage-distance pairs into the calibration list in `main.py`.
4. Run `servo_calibration.py` to tune the servo's pulse settings and rotation-time estimate.
5. Transfer the verified servo constants to `main.py`.
6. Run `main.py` to operate the tracking system.

The calibration scripts and data file are used during setup. The main tracking program uses the calibration values embedded directly in its source code rather than reading the text file automatically.

---
