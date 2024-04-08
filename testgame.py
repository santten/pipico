from machine import Pin, PWM, I2C
from fifo import Fifo
from ssd1306 import SSD1306_I2C
import time
import micropython
micropython.alloc_emergency_exception_buf(200)

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
rot_button = Pin(12, Pin.IN, Pin.PULL_UP)

## oled set up

OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
oled.fill(0)

## some graphic settings
y_distance = 15

## game class

class Player:
    def __init__(self):
        self.pos = 64
        self.length = 10
        self.y_pos = OLED_HEIGHT - y_distance
        self.state = self.move
    
    def move(self):
        if rot.fifo.has_data():
            dir = rot.fifo.get()
            print(dir)
            if dir == 1:
                if self.pos < (OLED_WIDTH - self.length):
                    self.pos += 1
                else:
                    self.pos -= 1
            if dir == -1:
                if self.pos > (0 + self.length * 2):
                    self.pos -= 1
                else:
                    self.pos += 1
            print(self.pos)
        oled.line(0, self.y_pos, OLED_WIDTH, self.y_pos, 0)
        oled.line(self.pos - self.length, self.y_pos, self.pos + self.length, self.y_pos, 1)
        oled.show()
        
    def execute(self):
        self.state()
        
class Enemy:
    def __init__(self):
        self.pos = 64
        self.length = 10
        self.y_pos = y_distance
        self.state = self.move
        self.dir = 1
    
    def move(self):
        if self.pos > (OLED_WIDTH - (self.length * 2)):
            self.dir = -1
        elif self.pos < (0 + (self.length * 2)):
            self.dir = 1
        
        if self.dir == 1:
            self.pos += 1
        else:
            self.pos -= 1
            
        oled.line(0, self.y_pos, OLED_WIDTH, self.y_pos, 0)
        oled.line(self.pos - self.length, self.y_pos, self.pos + self.length, self.y_pos, 1)
        oled.show()
    
    def execute(self):
        self.state()
        
## start screen
        
class Game:
    def __init__(self):
        self.score = 0
        self.state = self.start_screen
        
    def execute(self):
        self.state()
    
    def start_screen(self):
        ##text = "PING PONG"
        ##for i in range(5):
        ##   oled.text(text, 0, OLED_HEIGHT - 15)
        ##    oled.show()
        ##    time.sleep(0.2)
        ##    oled.fill(0)
        ##    oled.show()
        ##    time.sleep(0.2)
        self.state = self.game_on
    
    def game_on(self):
        player.execute()
        enemy.execute()
        
game = Game()
player = Player()
enemy = Enemy()

while True:
    game.execute()
    oled.rect(10, 10, OLED_WIDTH - 10, OLED_HEIGHT - 10, 1)
    time.sleep(0.001)