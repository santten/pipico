from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
from filefifo import Filefifo

## heart stuff
data = Filefifo(10, name='capture_250Hz_01.txt')
value1 = data.get()
value2 = data.get()
value3 = data.get()
comparison = value3 - value1
totalrounds = 0
rounds = 0
roundlist = []
roundlist.append(0)
seclist = []
button = Pin(7, Pin.IN, Pin.PULL_UP)
frequency = 0
even = False

## oled
OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

oled.fill(0)

while True:
    totalrounds += 1
    rounds += 1
    value1 = value2
    value2 = data.get()
    
    if totalrounds % 10 == 0:
        oled.scroll(1, 0)
        pixelY = value2 / 700 + 10
        oled.pixel(5, int(pixelY) , 1)
        oled.show()
    if totalrounds % 250 == 0:
        oled.line(5, 8, 5, 1, 1)
        oled.show()
        
    
    oldcomparison = comparison
    comparison = value2 - value1
    if (oldcomparison <= 0 and comparison > 0) or (oldcomparison > 0 and comparison <= 0):
        even = not even
        if even: 
            oled.line(5, 0, 5, OLED_HEIGHT, 1)
            oled.show()
            
            roundlist.append(rounds)
            print (f"\npeak at {totalrounds / 250:.2f} sec, {roundlist[-1]} rounds since last peak")
            rounds = 0
            freq = (1 / totalrounds / 250) * 100000
            print(f"{freq:.3f} Hz")
    time.sleep(0.001)
