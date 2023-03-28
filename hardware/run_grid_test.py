from controller import EasterControler
from simulator import EasterSimulator
import eastermath as em
import time
import math

def act(ct: EasterSimulator):
    for x in [-50, 0, 50]:
        for y in range(11):
            ct.go_to(x, y*10, move=y % 2 == 0, info=True)
            
    ct.go_to(0,0, move=True)


sim = EasterControler(
    {
        'simulator_start_speed': 0.5,
        'start_color': 'blue',
        'penup_offset': 0.25,
        'color_pos': {
            'black': 0,
            'red': 1,
            'green': 2,
            'blue': 3,
            'orange': None
        }
    }
)
sim.run(act=act, gui=True, console=True)
