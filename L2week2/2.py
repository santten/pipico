from filefifo import Filefifo
import time

data = Filefifo(10, name="capture_250Hz_02.txt")
seconds = 0
plotting_list = []
plotting_done = False

def plotting():
    plotting_list.append(latestvalue)

while True:
    latestvalue = data.get()
    seconds += 4
    
    if seconds / 100 < 2:
        plotting()
    elif not plotting_done:
        set_max = max(plotting_list)
        set_min = min(plotting_list)
        print(set_min)
        print(set_max, set_min)
        plotting_done = True
    if plotting_done and seconds / 100 < 10:
        scaled = ((latestvalue - set_min) / (set_max - set_min) * 100)
        print(f"scaled {scaled}")
    time.sleep(0.05)