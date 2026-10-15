import time
from machine import Pin, PWM

servo = PWM(Pin(6))
servo.freq(50)

def set_servo_pulse(ms):
    duty = int((ms / 20.0) * 65535)
    servo.duty_u16(duty)

print("Starting servo loop...")

try:
    while True:
        print("Rotating full speed clockwise...")
        set_servo_pulse(1.0)
        time.sleep(3)

        print("Stopping...")
        set_servo_pulse(1.48)
        time.sleep(2)

        print("Rotating full speed counterclockwise...")
        set_servo_pulse(2.0) 
        time.sleep(3)

        print("Stopping...")
        set_servo_pulse(1.48)
        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped. Turning off PWM.")
    servo.deinit()
