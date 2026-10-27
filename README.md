# Raspberry Pi Person Tracker

A Raspberry Pi Pico 2 W project that uses two analog distance sensors and a positional servo to turn a fixed attachment (a pointer, a camera mount, a lamp, etc.) toward the nearest person or object.

The two sensors sit side by side. Whichever one sees something closer "wins," and the servo swings to that side. If nothing is detected for a while, the servo returns to center.

This guide walks you through building it yourself, start to finish. Extra reference material (how the algorithm works, tuning, troubleshooting, limitations, and ideas) is at the end.

---

## Table of Contents

**Build it step by step**

1. [What you will build](#1-what-you-will-build)
2. [Gather your parts](#2-gather-your-parts)
   - [3D-print the housing and topper](#3d-print-the-housing-and-topper)
3. [Set up the Pico with MicroPython](#3-set-up-the-pico-with-micropython)
4. [Get the code](#4-get-the-code)
5. [Wire everything up](#5-wire-everything-up)
6. [Test the servo](#6-test-the-servo)
7. [Calibrate the distance sensors](#7-calibrate-the-distance-sensors)
8. [Check your calibration](#8-check-your-calibration)
9. [Mount the sensors on the servo](#9-mount-the-sensors-on-the-servo)
10. [Run the tracker](#10-run-the-tracker)

**Extra info**

- [A. How the tracking algorithm works](#a-how-the-tracking-algorithm-works)
- [B. How the servo is controlled](#b-how-the-servo-is-controlled)
- [C. Settings you can tune](#c-settings-you-can-tune)
- [D. Troubleshooting](#d-troubleshooting)
- [E. Limitations](#e-limitations)
- [F. Ideas for improving it](#f-ideas-for-improving-it)
- [G. Project files](#g-project-files)
- [H. License](#h-license)

---

# Build it step by step

## 1. What you will build

When finished, you will have:

- Two distance sensors mounted side by side, facing forward.
- A positional servo that rotates the sensor assembly (and anything else attached to it).
- A MicroPython program on the Pico that reads both sensors, decides which side a target is on, and moves the servo to **-45°**, **0°** (center), or **+45°**.

**Why a positional servo?** A continuous-rotation servo can only be told how fast to spin, so you have to guess where it is by timing its movement, and that guess drifts. A positional servo takes an actual angle, so the program always knows where it is pointing.

## 2. Gather your parts

| Part | Notes |
|------|-------|
| Raspberry Pi Pico 2 W | Any Pico running MicroPython should work with minor changes |
| 2x Hummingbird analog distance sensors | Any analog distance sensor works, but you must calibrate it yourself |
| 1x Hummingbird positional servo | Must accept a standard 50 Hz PWM signal |
| Jumper wires | |
| USB cable | For programming the Pico |
| Power source suitable for the servo | See the power warning in Step 5 |
| 3D-printed housing and topper | The project’s printable model files are in [`models/`](https://github.com/MonkeyMan1911/rp-person-tracker/tree/main/models) |
| Mounting materials | Needed only for any additional attachment or fastening not built into the printed parts |
| A flat piece of paper | Used as a calibration target |
| Ruler or tape measure | Used for calibration |

> Check the datasheets for your exact sensors and servo before connecting power. Voltage and current requirements vary.

### 3D-print the housing and topper

The repository includes a `models/` folder for the project's physical parts. Print the **housing** and **topper** before final assembly so you can check the fit around the electronics and moving servo assembly.

1. Open the [repository's `models/` folder](https://github.com/MonkeyMan1911/rp-person-tracker/tree/main/models) and identify the housing and topper files. Use the provided model files rather than recreating the parts from scratch.
2. Download the printable mesh files (usually `.stl`) and open them in your slicer, such as Cura, PrusaSlicer, or Bambu Studio.
3. Confirm the model units and scale before slicing. Do not resize the parts unless you are intentionally modifying the design; scaling can change the fit of the servo, sensors, and any openings.
4. Inspect the slicer's preview for missing walls, unexpected gaps, or unsupported overhangs. Use the orientation suggested by the model or the orientation that gives the housing a stable base and keeps the topper's visible surface clean.
5. If the repository does not specify settings for your printer and filament, use your printer's normal profile as a **starting point**, not as a verified project setting. A typical first test is 0.2 mm layer height, 2–3 walls, and 15–20% infill. Use supports only where the slicer preview shows they are needed.
6. Print the housing and topper, then remove any brim or support material carefully. Avoid cutting into the mating surfaces or thin features.
7. Test-fit the topper to the housing without forcing it. Check that the pieces sit together as intended and that the housing leaves room for the components and wires. If the fit is too tight, check for leftover support material and first-layer bulging before changing the model or scaling it.
8. Before installing electronics, check that no printed edge can snag the wires and that the complete assembly can rotate through the intended range without hitting the housing or topper.

**Fit and safety notes**

- The exact print time, filament use, tolerances, and best orientation depend on the model files and your printer. The repository does not establish universal slicer settings, so treat the settings above as test-print guidance.
- Keep the servo's moving parts clear of the housing and topper. Do not run the servo if the printed parts bind, flex into the mechanism, or force it against a stop.
- If a part does not fit, verify the model, scale, orientation, and print quality before editing dimensions. A small test print may be quicker than reprinting the entire part.
- Keep the Pico, sensor wiring, and servo connections accessible while you test the fit. Do not trap wires between the housing and topper.

## 3. Set up the Pico with MicroPython

1. Download the latest MicroPython firmware for the **Pico 2 W** from [micropython.org/download](https://micropython.org/download/).
2. Hold the **BOOTSEL** button on the Pico while plugging it into your computer by USB. It will appear as a USB drive.
3. Drag the `.uf2` firmware file onto that drive. The Pico will reboot by itself.
4. Install an editor that can talk to MicroPython. Good options:
   - [Thonny](https://thonny.org/) (easiest for beginners)
   - VS Code with the MicroPico extension (this repo includes a `.micropico` config file for that setup)
5. In your editor, select the **MicroPython (Raspberry Pi Pico)** interpreter and confirm you can see a `>>>` prompt in the shell.

## 4. Get the code

Clone the repository (or download it as a ZIP from GitHub):

```bash
git clone https://github.com/MonkeyMan1911/rp-person-tracker.git
cd rp-person-tracker
```

The scripts live in the `scripts/` folder. You will upload these to the Pico as you need them:

| Script | When you use it |
|--------|-----------------|
| `rotate.py` | Step 6: test the servo |
| `distance_calibration.py` | Step 7: collect voltage readings |
| `distance_read.py` | Step 8: verify your calibration |
| `main.py` | Step 10: the full tracker |

## 5. Wire everything up

### Pin connections

| Component | Pico pin |
|-----------|----------|
| Distance sensor 0, analog output | **GP27** (ADC) |
| Distance sensor 1, analog output | **GP26** (ADC) |
| Servo control signal | **GP6** (PWM) |
| Sensor power and ground | Per the sensor specifications |
| Servo power and ground | Per the servo specifications |

The code initializes the sensors on GP27 then GP26 (in that order) and generates the servo signal on GP6.

### Power safety

- **Do not assume the Pico's 3.3 V output can power the servo.** Servos can draw far more current than a Pico pin or regulator can supply. Use a separate regulated supply if your servo needs one.
- **Connect all grounds together** (Pico, sensors, and servo supply) so the signals share a common reference.
- Make sure each sensor's analog output never exceeds **3.3 V**, which is the limit for the Pico's ADC pins.
- Double-check every connection before applying power.

## 6. Test the servo

Before dealing with sensors, make sure the servo moves correctly.

1. Upload and run `scripts/rotate.py`.
2. Watch the servo. It should move to its test positions smoothly.
3. If it does not move, hums, or pushes against a stop, stop the program immediately and see [Troubleshooting](#d-troubleshooting).

Taking the servo horn off while testing (or making sure nothing is attached) avoids damage if the angles are wrong. Once the endpoints behave, attach the horn so that **0° points straight ahead**.

## 7. Calibrate the distance sensors

Analog distance sensors output a voltage that changes with distance, but the relationship is not a straight line and differs between individual sensors. Calibration builds a table that maps voltage to centimeters for *your* sensors.

1. Upload `scripts/distance_calibration.py` to the Pico and run it. It prints voltage readings.
2. Hold a **flat piece of paper** at exactly **5 cm** from the sensor, facing it straight on.
3. Let the readings settle, then write down several values and **average them**.
4. Move the paper back to **10 cm** and repeat. Continue in **5 cm steps** as far as the sensor gives consistent results.
5. **Drop any distance where the averages are not consistent.** In the original build, 95 cm was excluded for this reason, so the usable range ended up as 5 to 90 cm.
6. Repeat the whole process for the second sensor if you want separate tables (the sensors may not match exactly).
7. Put your results into the calibration list in `main.py` (and in `distance_read.py` for testing).

### Example calibration table (from the original build)

Your numbers will differ. Use these only as a rough sanity check.

| Distance (cm) | Voltage (V) |
|--------------:|------------:|
| 5  | 0.08495 |
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

### How voltage becomes distance

The program takes **20 ADC readings** per measurement and averages them to smooth out noise. It then finds the two calibration points surrounding the measured voltage and uses **linear interpolation**:

$$
d = d1 + (V - V1) / (V2 - V1) * (d2 - d1)
$$

- `V` is the measured voltage
- `V1`, `V2` are the neighboring calibration voltages
- `d1`, `d2` are their matching distances
- `d` is the estimated distance

If `V` falls outside the table, the function returns `None`, which the program treats as "out of range."

## 8. Check your calibration

1. Paste your measured table into the calibration list in `scripts/distance_read.py`.
2. Run it and hold the paper at distances you did **not** use for calibration (for example 12 cm or 47 cm).
3. Compare what the program prints with a ruler. If readings are off by more than a few centimeters, redo the calibration, taking more readings at each point and keeping the paper flat and square to the sensor.

## 9. Mount the sensors on the servo

1. Fix the two sensors **side by side**, facing the same direction, so each one covers one half of the area in front of the assembly.
2. Attach the sensor assembly to the servo horn so that rotating the servo changes where the sensors point.
3. Set the servo to its center (0°) position, then attach the horn so the sensors face straight ahead.
4. Make sure no wires will snag or tug as the assembly swings through ±45°.

The `models/` folder holds the files for the physical design of the project. If you printed the housing and topper in Step 2, test-fit them around the sensor/servo assembly now. Confirm the sensors face forward at the 0° rest position, the topper is secure, and neither printed part blocks the sensors or catches the wires. Remove the topper again if you need access while wiring or testing.

## 10. Run the tracker

1. Re-check wiring and power.
2. Upload `scripts/main.py` to the Pico and run it.
3. Open the serial console. You should see output like this:

```
Tracking started. Press Ctrl+C to stop.
S0: 24.8cm (waiting) | S1: 30.2cm (waiting)
S0: 25.1cm (READY) | S1: 29.7cm (READY)
-> Moving to -45 degrees
```

(The numbers above are only an example.)

4. Stand in front of the sensors. The servo should turn toward whichever sensor sees you as closer.
5. Step away or leave the sensors' range. After 10 loops with no detection, the servo returns to center.
6. Press **Ctrl+C** to stop. The program returns the servo to rest and shuts down the PWM output.

Congratulations, you have built it. The sections below explain how it works and how to adjust it.

---

# Extra info

## A. How the tracking algorithm works

Each loop of `main.py` does three things.

### 1. Read both sensors

Each sensor is sampled 20 times with a short delay between samples. The average ADC value is converted to a voltage, then to a distance using the calibration table.

### 2. Check that readings are consistent

Single readings can be noisy, so the program only trusts a sensor once it is **ready**.

- It stores recent valid distance readings for each sensor.
- A sensor becomes ready when it has **2 readings** and both are within **3 cm** of their average.
- If a reading is out of the calibrated range, that sensor's history is cleared.

These are controlled by:

```python
REQUIRED_READINGS = 2
ERROR_MARGIN = 3
```

### 3. Pick a target angle

The program uses the most recent distance from each ready sensor.

| Condition | Target angle |
|-----------|-------------:|
| Both ready, sensor 0 reports the closer distance | -45° |
| Both ready, sensor 1 reports the closer distance | +45° |
| Only sensor 0 is ready | -45° |
| Only sensor 1 is ready | +45° |
| Neither sensor detects a target for 10 loops in a row | 0° |
| Readings are not yet consistent | Hold current position |

If both sensors report exactly the same distance, the code picks sensor 1's angle.

The program waits briefly between loops and only sends a new command when the target angle differs from the current one, which avoids needless servo jitter.

## B. How the servo is controlled

The servo is driven by a **50 Hz PWM signal** on GP6. The width of each pulse tells the servo what angle to move to.

The code maps a requested angle from -90° to +90° onto a pulse range:

$$
t = t_min + (angle + 90) / 180 * (t_max - t_min)
$$

with these defaults:

```python
MIN_PULSE_MS = 0.5
MAX_PULSE_MS = 2.5
```

The `set_angle()` function then converts that pulse width in milliseconds into the duty cycle the Pico's PWM hardware needs. At 50 Hz one period is 20 ms, so the duty fraction is `t / 20`.

After each move the program waits **0.4 seconds** so the servo has time to arrive.

**Important:** Servos vary. The 0.5 to 2.5 ms range is a common starting point, but your servo may use a narrower range (such as 1.0 to 2.0 ms). If the physical positions do not match the intended angles, adjust the pulse limits slowly and test the endpoints carefully without forcing the servo against its mechanical stops.

The three positions used by the program are:

- **-45°**: sensor 0's direction
- **0°**: center / resting position
- **+45°**: sensor 1's direction

These are relative to the program's assumed center, so mount the horn with that in mind (Step 6).

## C. Settings you can tune

| Setting | What it does | Effect of increasing it |
|---------|--------------|-------------------------|
| `REQUIRED_READINGS` | Consistent readings needed before a sensor is trusted | Fewer false triggers, slower response |
| `ERROR_MARGIN` | Allowed spread (cm) between readings | More tolerant of noise, less precise |
| Samples per measurement (20) | ADC readings averaged each loop | Smoother values, slower loops |
| Rest timeout (10 loops) | Loops with no target before returning to center | Servo stays pointed longer after you leave |
| `MIN_PULSE_MS` / `MAX_PULSE_MS` | Pulse range mapped to -90° to +90° | Changes the physical angles; tune to your servo |
| Servo settle delay (0.4 s) | Wait after each move | Safer for slow servos, slower overall |
| Target angles (-45°, +45°) | Where the servo points for each sensor | Wider or narrower sweep |

## D. Troubleshooting

**The sensor reports `Out of range`.**
- Make sure the target is inside the calibrated range (5 to 90 cm in the original build).
- Check the sensor's power, ground, and analog output wiring.
- Remember that voltages outside your calibration table are not converted into distances.

**A sensor stays in the `waiting` state.**
- Readings may be fluctuating by more than the 3 cm error margin.
- Make sure the sensor is stable and the target surface is suitable (flat, not too dark or shiny).
- Confirm the sensor's output voltage actually changes as you move the target.

**The servo moves to the wrong angle.**
- Verify which sensor is physically on the left and right.
- Check the orientation of the servo and the sensor assembly.
- Check the servo's pulse-width requirements and adjust the limits if needed.

**The servo buzzes or hits a mechanical stop.**
- Stop the program and check the servo's allowed range of movement.
- Narrow the pulse range if the commanded positions go past the servo's limits.
- Never leave a servo continuously pushing against a stop.

**The Pico resets or the servo acts erratically.**
- The servo supply may not provide enough current.
- Make sure all grounds are connected.
- Check for loose wires or unstable connections.

## E. Limitations

- Distance is estimated from a calibrated analog voltage, so accuracy depends on your sensors, calibration, and surroundings.
- The calibrated range is 5 to 90 cm. Anything outside it is treated as out of range.
- The system picks between two fixed angles rather than computing a continuous direction to the target.
- The commanded angle comes from the PWM mapping. The program does not measure the servo's real angle.
- It assumes both sensors are mounted consistently so their readings can be compared fairly.
- Readings must be consistent before the program reacts, which adds a small delay.
- If a target is momentarily out of range for long enough, the servo returns to center even though the target is still there.

## F. Ideas for improving it

- Add more sensors or more angle positions for finer direction tracking.
- Interpolate between the two sensor readings to point at an angle in between instead of snapping to two positions.
- Use separate calibration tables for each sensor.
- Add feedback, such as a potentiometer on the servo shaft, so the program can confirm the real angle.
- Use a sensor with a longer or more reliable range.
- Add an LED or buzzer that shows when a target is locked.
- Log readings to a file to analyze noise and tune the settings.

## G. Project files

| File | Purpose |
|------|---------|
| `scripts/main.py` | Initializes the sensors and servo, converts readings to distances, checks consistency, selects target angles, and runs the tracking loop |
| `scripts/rotate.py` | Tests servo rotation |
| `scripts/distance_calibration.py` | Prints voltage values at a known distance to help with calibration |
| `scripts/distance_read.py` | Tests whether post-calibration distance readings are accurate; you must enter your own calibration points |
| [`models/`](https://github.com/MonkeyMan1911/rp-person-tracker/tree/main/models) | 3D model files for the printed housing and topper; check the folder for the available source and printable files |
| `.micropico` | Configuration for the MicroPico VS Code extension |
| `LICENSE` | MIT license |

The earlier `servo_calibration.py` was removed because `main.py` now commands the positional servo directly with PWM pulse widths.

## H. License

This project is released under the [MIT License](LICENSE).
