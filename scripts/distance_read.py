from machine import ADC, Pin
import time

sensors = [ADC(Pin(26)), ADC(Pin(27))]

calibration = [
    (0.08495, 5),
    (0.16785, 10),
    (0.22420, 15),
    (0.27025, 20),
    (0.37630, 25),
    (0.41340, 30),
    (0.52155, 35),
    (0.57375, 40),
    (0.62400, 45),
    (0.68980, 50),
    (0.75625, 55),
    (0.84400, 60),
    (0.91745, 65),
    (0.96665, 70),
    (1.04145, 75),
    (1.10760, 80),
    (1.17860, 85),
    (1.24115, 90)
]


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

            distance = d1 + (voltage - v1) * (d2 - d1) / (v2 - v1)

            return distance

    return None


while True:
	distances = [None, None]
	for i in range(0, 2):
		voltage = get_voltage(sensors[i])
		distance = get_distance(voltage)
		distances[i] = distance # type: ignore

	print(f"Sensor 0: {distances[0]} | Sensor 1: {distances[1]}")
	time.sleep(0.1)
