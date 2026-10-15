from machine import ADC, Pin
import time

distance = input("Distance: ")
time.sleep(1)
sensor = ADC(Pin(26))
sum = 0

def get_reading():
    raw = sensor.read_u16()
    voltage = raw * 3.3 / 65535
    global sum
    sum += round(voltage, 3)

    print("Raw:", raw, "| Voltage:", round(voltage, 3), "V")

    time.sleep(0.2)

for i in range(21):
	get_reading()

avg = sum / 20
print(f"{distance}cm - {avg}")
