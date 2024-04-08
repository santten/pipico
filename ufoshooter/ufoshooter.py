from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import utime
from time import sleep
OLED_SDA = 14
OLED_SCL = 15

SW0_PIN = 9
SW2_PIN = 7

i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
oled.fill(0)

UFO = "<=>"
ufo_position = 50
ufoY = 56
sw0 = Pin(SW0_PIN, Pin.IN, Pin.PULL_UP)
sw2 = Pin(SW2_PIN, Pin.IN, Pin.PULL_UP)
line_height = 8

def display_ufo(position):
    oled.fill_rect(0, OLED_HEIGHT - line_height, OLED_WIDTH, 56, 0)
    oled.text(UFO, position, ufoY) 
    oled.show()

def is_button_pressed_SW0():
    return not sw0.value()

def is_button_pressed_SW2():
    return not sw2.value()

while True:
    if is_button_pressed_SW2() and ufo_position > 0:
        ufo_position -= 5 
    elif is_button_pressed_SW0() and ufo_position < 100:
        ufo_position += 5 

    display_ufo(ufo_position)
    sleep(0.1)