from ssd1306 import SSD1306_I2C
import fifo
import time
from machine import Pin, I2C
from filefifo import Filefifo


import micropython
micropython.alloc_emergency_exception_buf(200)

led = Pin("LED", Pin.OUT)
    
from filefifo import Filefifo
data = Filefifo(10, name = 'capture_250Hz_01.txt')

OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
line_height = 8 

def display_text(text):
    oled.scroll(0, -line_height)  # Scroll the display up by one line height
    oled.fill_rect(0, OLED_HEIGHT - line_height, OLED_WIDTH, line_height, 0)  # Clear the last line
    oled.text(text, 0, OLED_HEIGHT - line_height)  # Draw the new text at the bottom
    oled.show()


while True:
    led.toggle()
    display_text(str(data.get()))
    time.sleep(1)
