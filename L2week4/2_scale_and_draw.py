from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
from filefifo import Filefifo

## set up

line = 0
data = Filefifo(10, name='capture_250Hz_01.txt')
datalist = []
delay = 0.001 ## seconds
samplespeed = 5 ## how many samples you want to see on screen * 2

OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

oled.fill(0)

## functions :P

def minmaxcalculation(linelist):
    listmax = max(linelist)
    listmin = min(linelist)
    return {"max": listmax, "min": listmin} 

def scaling(value, plottedmax, plottedmin):
    ourmax = 63
    ourmin = 0
    scaled = ourmin + ((value - plottedmin)/(plottedmax - plottedmin)) * (ourmax - ourmin)
    if scaled < 0:
        return 0
    if scaled > ourmax:
        return ourmax
    return int(scaled)

## set datalist for minmax calculation
print("plotting min and max values for scaling...")
while line < 250:
    datalist.append(data.get())
    line += 1

## set minandmax
minandmax = minmaxcalculation(datalist)
print(f"plotting done! min: {minandmax['min']} max: {minandmax['max']}")

while line >= 250:
    scaled = scaling(data.get(), minandmax["min"], minandmax["max"])
    oled.pixel(5, scaled, 1)
    if line % samplespeed == 0:
        oled.pixel(5, scaled, 1)
        oled.scroll(1, 0)
        oled.show()
        time.sleep(delay)
    line += 1
    