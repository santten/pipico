from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo
from fifo import Fifo
import time

data = Filefifo(10, name="capture_250Hz_01.txt")
list = []

OLED_SDA = 14
OLED_SCL = 15

i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
line_height = 8

print("reading...")

for i in range(0, 1000):
    list.append(data.get())
    
print("\nmax value:", max(list))
print("min value:", min(list))
print("amount of values read:", len(list))

del list[(129):]
position = 8

def display_text(dir, position):
    if dir == 1: ## show value on last line when scrolling down
        text = f"{str(list[position])} [{str(position)}]"
        oled.scroll(0, -line_height)
        oled.fill_rect(0, OLED_HEIGHT - line_height, OLED_WIDTH, line_height, 0)
        oled.text(text, 0, OLED_HEIGHT - line_height)
        oled.show()
    if dir == 0: # show value on first line when scrolling up
        text = f"{str(list[position - 7])} [{str(position - 7)}]"
        oled.scroll(0, line_height)
        oled.fill_rect(0, 0, OLED_WIDTH, line_height, 0)
        oled.text(text, 0, 0)
        oled.show()
        
        
class RotaryEncoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(10, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(11, mode = Pin.IN, pull = Pin.PULL_UP)
        self.fifo = Fifo(30, typecode = "i")
        self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
        
    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

rot = RotaryEncoder(10, 11)

## display first 8
for i in range(1, 9):
    display_text(1, i)



while True:
    if rot.fifo.has_data():
        dir = rot.fifo.get()
        if dir == 1:
            print("direction right")
            if position <= 127:
                position += 1
                display_text(1, position)
    
            else:
                position = 128
        if dir == -1:
            print("direction left")
            if position > 8:
                position -= 1
                display_text(0, position)
            else:
                position = 8
    
time.sleep(0.1)
