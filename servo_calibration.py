from machine import ADC, Pin, PWM
import time

STOP_PULSE = 1.46 # Adjust these as needed
SLOW_CW_PULSE = 1.44
SLOW_CCW_PULSE = 1.48

SECONDS_PER_DEGREE = 0.06666666667

servo = PWM(Pin(6))
servo.freq(50)

def set_servo_pulse(ms):
    duty = int((ms / 20.0) * 65535)
    servo.duty_u16(duty)

def calibrate(seconds=2):
    """Run once by hand: spins CCW for `seconds`. Measure the degrees it
    turned, then set SECONDS_PER_DEGREE = seconds / degrees_turned."""
    set_servo_pulse(SLOW_CCW_PULSE)
    time.sleep(seconds)
    set_servo_pulse(STOP_PULSE)
