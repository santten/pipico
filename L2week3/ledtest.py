from machine import Pin, PWM
import time

led_pwm = PWM(Pin(20))
led_pwm.freq(1000)

def fade_led():
    for duty_cycle in range(0, 65535, 256):  # 16-bit PWM resolution
        led_pwm.duty_u16(duty_cycle)
        time.sleep_ms(10)  # Adjust the sleep time for the desired fading speed

    for duty_cycle in range(65535, 0, -256): 
        led_pwm.duty_u16(duty_cycle)
        time.sleep_ms(10)  # Adjust the sleep time for the desired fading speed
        
while True:
    fade_led()