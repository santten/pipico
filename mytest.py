from filefifo import Filefifo
from ssd1306 import SSD1306_I2C


data = Filefifo(10, name = 'capture_250Hz_01.txt')
for _ in range(100):
    print(data.get())