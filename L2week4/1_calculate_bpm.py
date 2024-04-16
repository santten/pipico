from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
from filefifo import Filefifo

## heart stuff
data = Filefifo(10, name='capture_250Hz_01.txt')
datalist = []
totalrounds = 0
line = 0
linelist = []
linelist.append(0)
seclist = []
button = Pin(7, Pin.IN, Pin.PULL_UP)
frequency = 0
PPI = 1

dictlist = []

## oled
OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

oled.fill(0)

def compare(olderdata, newerdata, newestdata):
    oldcomparison = newerdata - olderdata
    comparison = newestdata - newerdata
    if (oldcomparison > 0 and comparison <= 0):
        return True

def calculateBPM(data1, data2):
    PPI = (data2["line"] - data1["line"]) * (4)
    HR = 60 / (PPI / 1000)
    print("PPI:", PPI, "HR:", HR, "BPM")
    
    

while True:
    ## keep track of which line we are on
    line += 1
    
    ## convert that to milliseconds 1 line = 4 ms 
    ms = line * 4
    
    ## get data and append
    linedata = data.get()
    datalist.append(linedata)

    ## dictlist and print
    if len(datalist) > 3:
        datalist.pop(0)
        comparison = compare(datalist[-3], datalist[-2], datalist[-1])
        if comparison:
            print("\n\n\nPEAK DETECTED")
            dictlist.append({"ms": ms, "line": line, "data": linedata})
            if len(dictlist) >= 2:
                if len(dictlist) > 5:
                    dictlist.pop(0)
                print(dictlist[-2], dictlist[-1], len(dictlist))
                calculateBPM(dictlist[-2], dictlist[-1])
        ## PPI = dictlist[-2]["line"] - dictlist[-1]["line"] dictlist.append({"ms": ms, "line": line, "data": linedata})
        ## print(PPI, dictlist[-1], len(dictlist))
    time.sleep(0.001)
