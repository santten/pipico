from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo
from fifo import Fifo
import time

## initial set up

filename = "capture_250Hz_02.txt"
data = Filefifo(10, name=filename)
datalist = []
line_height = 10
device_mode = "start_screen" ## start_screen, reading
delay = 0.1
plottedmax = 0
plottedmin = 0
position = 1
offset = 1000
scaling_value = 10
scrollstepsize = 10

# oled set up

OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
line_height = 8


## functions
def minmaxcalculation(linelist):
    listmax = max(linelist)
    listmin = min(linelist)
    return {"max": listmax, "min": listmin} 

def scaling(value, plottedmax, plottedmin, offset, scaling_value):
    ourmax = 63 - scaling_value
    ourmin = 0 + scaling_value
    scaled = ourmin + (((value - offset) - plottedmin)/(plottedmax - plottedmin)) * (ourmax - ourmin)
    if scaled < 0:
        return 0
    if scaled > ourmax:
        return ourmax
    return int(scaled)

## rotary encoder set up

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

## button set up

SW0_PIN = 9
SW1_PIN = 8
SW2_PIN = 7
sw0 = Pin(SW0_PIN, Pin.IN, Pin.PULL_UP)
sw1 = Pin(SW1_PIN, Pin.IN, Pin.PULL_UP)
sw2 = Pin(SW2_PIN, Pin.IN, Pin.PULL_UP)

def draw_128_values(datalist, position, offset, scaling_value, text = ''):
    oled.fill(0)
    oled.text(text, 5, line_height, 1)
    xpos = 0
    drawlist = []
    for i in range(position, position + 128):
        drawlist.append(datalist[i])
    if position < scrollstepsize:
        oled.line(1, OLED_HEIGHT, 1, 0, 1)
    if position >= (len(datalist) - OLED_WIDTH - scrollstepsize):
        oled.line(OLED_WIDTH - 1, OLED_HEIGHT, OLED_WIDTH - 1, 0, 1)
        oled.text("END", OLED_WIDTH - 30, OLED_HEIGHT - line_height, 1)
    while xpos < 127:
        global plottedmax
        global plottedmin
        xpos += 1
        scaled = scaling(drawlist[xpos], plottedmax, plottedmin, offset, scaling_value)
        oled.pixel(xpos, scaled, 1)
    oled.show()

position = 0
print(f"Press SW1 on the device to read 360 values from {filename}")

def execute(mode):
    global position
    global offset
    global scaling_value
    global device_mode
    
    if mode == "start_screen":
        oled.fill(0)
        oled.text("Press SW1 to", 1, line_height, 1)
        oled.text("read 1800 lines", 1, line_height * 2, 1)
        oled.text("from file:", 1, line_height * 3, 1)
        oled.text(filename, 1, line_height * 5, 1)
        oled.show()
    if mode == "sw0_pressed":
        text = f"OFFSET: {offset}"
        print(f"SW0 PRESSED, adjusting OFFSET: {offset}")
        oled.show()
        if rot.fifo.has_data():
            direction = rot.fifo.get()
            if direction == -1:
                offset -= 100
            if direction == 1:
                offset += 100
        draw_128_values(datalist, position, offset, scaling_value, text)
        device_mode = "normal"
    if mode == "sw2_pressed":
        text = f"SCALING: {scaling_value + 33}"
        print(f"SW2 PRESSED, adjusting SCALING: {scaling_value + 33}")
        if rot.fifo.has_data():
            direction = rot.fifo.get()
            if direction == -1:
                scaling_value -= 1
            if direction == 1:
                scaling_value += 1
            if scaling_value < -32:
                scaling_value = -32        
                text = f"SCALING: MIN"
            if scaling_value > 32:
                scaling_value = 32
                text = f"SCALING: MAX"
        draw_128_values(datalist, position, offset, scaling_value, text)
        device_mode = "normal"
    if mode == "reading":
        oled.fill(0)
        oled.text("reading data...", 1, line_height * 3, 1)
        oled.show()
        line = 0
        while line < 1800: 
            line += 1
            if line % 5 == 0:
                datalist.append(data.get())
                if len(datalist) > 0:
                    print(f"DATA #{len(datalist)} ADDED from the file's LINE {line}: value {datalist[-1]}")
        global plottedmax, plottedmin
        plottedmax = max(datalist)
        plottedmin = min(datalist)
        oled.fill(0)
        device_mode = "normal"
    if mode == "normal":
        draw_128_values(datalist, position, offset, scaling_value)
        if rot.fifo.has_data():
            maxposition = len(datalist) - OLED_WIDTH - scrollstepsize
            direction = rot.fifo.get()
            if direction == -1:
                if position > scrollstepsize:
                    position -= scrollstepsize
                else:
                    position = 1
                print(f"ROTARY knob turned LEFT, POSITION: {position}")
                
            if direction == 1:
                if position < maxposition:
                    position += scrollstepsize
                else:
                    position = maxposition
                print(f"ROTARY knob turned RIGHT, POSITION: {position}")
                
        


## start screen
while True:
    if len(datalist) == 0:
        device_mode = "start_screen"
    if sw0.value() == 0:
        if (device_mode !="start_screen") and (device_mode != "reading"):
            device_mode = "sw0_pressed"
    if sw1.value() == 0:
        device_mode = "reading"
    if sw2.value() == 0:
        if (device_mode !="start_screen") and (device_mode != "reading"):
           device_mode = "sw2_pressed"
        
    execute(device_mode)
    time.sleep(delay)
