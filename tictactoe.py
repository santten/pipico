from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo
from fifo import Fifo
import time
import random

## initial set up

line_height = 10
device_mode = "start_screen" ## start_screen, reading

# oled set up

OLED_SDA = 14
OLED_SCL = 15
i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
line_height = 8
letter_width = 8

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
rotbutton = Pin(12, mode = Pin.IN, pull = Pin.PULL_UP)


## button set up

SW0_PIN = 9
SW1_PIN = 8
SW2_PIN = 7
sw0 = Pin(SW0_PIN, Pin.IN, Pin.PULL_UP)
sw1 = Pin(SW1_PIN, Pin.IN, Pin.PULL_UP)
sw2 = Pin(SW2_PIN, Pin.IN, Pin.PULL_UP)

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
     
    def draw(self):
        oled.pixel(self.x, self.y, 1)
     
class Slot:
    def __init__(self, dot, side, row, column, slotid):
        self.status = 0 ## 1 if taken by player, 0 if available
        self.id = slotid
        self.side = side
        self.dot1 = dot
        self.center = Dot((self.dot1.x + int(side / 2)),(self.dot1.y + int(side / 2)))
        self.row = row
        self.column = column
        
    def drawsquare(self):
        oled.rect(self.dot1.x, self.dot1.y, self.side, self.side, 1)
    
    def update(self, status):
        self.status = status
        oled.fill_rect(self.dot1.x, self.dot1.y, self.side, self.side, 0)
        oled.rect(self.dot1.x, self.dot1.y, self.side, self.side, 1)
        if status == 1:
            mytext = "o"
        elif status == 2:
            mytext = "x"
        else:
            mytext = ""
        oled.text(mytext, (self.dot1.x + 4), (self.dot1.y + 2), 1)
        oled.show()


class Cursor:
    def __init__(self, slot):
        self.slot = slot
        self.graphic = "[]"
    
    def update(self, new_pos):
        old_pos = self.slot
        oled.text(self.graphic, slots[old_pos].dot1.x, slots[old_pos].dot1.y + int(letter_width / 2), 0)
        oled.text(self.graphic, slots[new_pos].dot1.x, slots[new_pos].dot1.y + int(letter_width / 2), 1)
        self.slot = new_pos
        oled.show()

def computer_think(slots):
    freeslots = []
    print("generating list of free slots...")
    for i in slots:
        if i.status == 0:
            freeslots.append(i)
    if len(freeslots) == 0:
        evaluate_board(slots)
    else:
        print(len(freeslots), "freeslots available")
        choice = random.randint(0, len(freeslots) - 1)
        freeslots[choice].update(2)
        print(f"computer generated number {choice}, slot {freeslots[choice].id}")

def blink_text(text, length_in_range):
    oled.fill(0)
    for i in range(int(length_in_range)):
        i += 1
        time.sleep(delay * 2)
        oled.text(text, 5, 5, 1)
        oled.show()
        time.sleep(delay * 2)
        oled.fill(0)
        oled.show()     

def evaluate_board(slots):
    representative_number = 0    
    situation_string = ""
    row_comparison = False
    column_comparison = False
    win_switch = False
    diag_check = False
    for i in slots:
        situation_string += str(i.status)
    print("evaluation:", situation_string)
    diagonal_comparison1 = (situation_string[0] == situation_string[4] == situation_string[8])
    diagonal_comparison2 = (situation_string[2] == situation_string[4] == situation_string[6])
    
    representative_number = 0

    
    if diagonal_comparison1 or diagonal_comparison2:
        representative_number = situation_string[4]
        print("REPR SET: code 1100", representative_number)
        if representative_number != 0:
            diag_check = True
        
    for i in range(0, 3):
        row_comparison = (situation_string[0 + (i*3)] == situation_string[1 + (i*3)] == situation_string[2 + (i*3)])
        column_comparison = (situation_string[0 + (i)] == situation_string[3 + (i)] == situation_string[6 + (i)])
        if row_comparison:
            if int(situation_string[0 + (i)]) != 0:
                representative_number = int(situation_string[0 + (i*3)])
                print("REPR SET: code 1111", representative_number)
        if column_comparison:
            if int(situation_string[0 + (i)]) != 0:
                representative_number = int(situation_string[0 + (i)])
                print("REPR SET: code 1122", representative_number)
                
 #   print(not column_comparison, not row_comparison, not diag_check)    
 #  if not column_comparison and not row_comparison and not diag_check:
 #      print("REPR NUMBER:", representative_number)
    
    
    if representative_number != 0:
        print("Win detected?", representative_number)
        if int(representative_number) == 1:
            blink_text("YOU WIN!", 10)           
            situation_string = ""
            set_new_game()
            return int(representative_number)
        if int(representative_number) == 2:
            blink_text("YOU LOST!", 10) 
            
            situation_string = ""
            set_new_game()
            
            return int(representative_number)
        else:
            return int(0)
        print("row", row_comparison, "col", column_comparison)
        print("diag1", diagonal_comparison1, "diag2", diagonal_comparison2)
    elif "0" not in situation_string:
            blink_text("IT'S A TIE!", 10)
            situation_string = ""
            set_new_game()
    
            return int(3)
    else:
        return int(0)
        

oled.fill(0)

grid_xpos = 20
grid_ypos = -10
slot_width = 16
slots = []


    
cur = Cursor(0)


oled.show()

position = 0
delay = 0.05

def set_new_game():
    global device_mode
    global slots
    slots = []
    row = 0
    column = 0
    
    oled.fill(0)
    oled.text("TIC TAC TOE", 1, 1, 1)
    oled.text("XOXOXOXOXOXOXOXOXOXOXOXOXOXOXOXO", -5, 19, 1)
    oled.show()
    time.sleep(delay * 3)
    oled.fill(0)
        
    for i in range(9):
        if i < 3:
            row = 1
        elif i > 5:
            row = 3
        else:
            row = 2
        if i % 3 == 0:
            column = 1
        elif (i - 1) % 3 == 0:
            column = 2
        else:
            column = 3
            
        print(i, row, column)    
        slot = Slot(Dot((grid_xpos + column * slot_width),(grid_ypos + row * slot_width)), slot_width, row, column, i)
        slot.drawsquare()
        oled.show()
        slots.append(slot)
        print("slot number", len(slots) - 1, "added")

    print(len(slots))
    
    for i in range(9):
        slots[i].update(0)
    device_mode = "player_turn"

set_new_game()
    
while True:
    time.sleep(delay)

    if device_mode == "player_turn":
        if rot.fifo.has_data():
            maxposition = 8
            minposition = 0
            direction = rot.fifo.get()
            if direction == -1:
                if position > minposition:
                    position -= 1
                else:
                    position = minposition
            if direction == 1:
                if position < maxposition:
                    position += 1
                else:
                    position = maxposition
        cur.update(position)
        time.sleep(0.1)
        if rotbutton.value() == 0:
            if slots[position].status == 0:
                slots[position].update(1)
                check = evaluate_board(slots)
                print("check:", check, "\n")
                if check == 0:
                    device_mode = "comp_turn"
            else:
                print("slot taken")
    if device_mode == "comp_turn":
        computer_think(slots)
        check = evaluate_board(slots)
        print("check:", check)
        if check == 0:
            device_mode = "player_turn"
