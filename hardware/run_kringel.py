#Spiralen:Ein regenbogenfarbenes Muster mit Dreiecken und Spiralen. 
import sys
import random
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    rainbow = ['red', 'yellow', 'green', 'blue']
    sin_width = ct.egg_xborder_steps * 0.2
    distance = 2 * ct.x_velocity
    sin_number = 10
    sin_res = 32
    
    def kringel(d: float):
        colori = 0
        xpos = -ct.egg_xborder_steps * 0.5
        while xpos < - sin_width - distance:
            ct.step_to(xpos * d, move=True, color=rainbow[colori % len(rainbow)])
            ct.step_to(0, rel=True, long=True)
            colori += 1
            xpos += ct.x_stroke_steps * 2
            
    def sin_curves():
        for o in range(len(rainbow)):
            color = rainbow[o]
            yoffset = ct.egg_y_steps / sin_number / len(rainbow) * 1j * o
            for s in range(sin_number * sin_res):
                angle = s / sin_res * math.pi
                delta = math.sin(angle) * sin_width + s / sin_res / sin_number * ct.egg_y_steps * 1j
                ct.step_to(delta + yoffset, move = s == 0, color = color)
    
    kringel(1)
    sin_curves()
    kringel(-1)

from controller import EasterControler
config = {
    'egg_use_percent': 63,
    'simulator_start_speed': 0.0,
    'start_color': 'green',
    'penup_offset': 0.25,
    'color_pos': {
        'purple': 4 + 1j,
        'yellow': 3,
        'green': 2,
        'blue': 1,
        'red': 0
    },
    'name': 'Spiralen',
}
(EasterControler(config) if sys.argv[1] == 'C' else EasterCanvas(config)).run(act=act)
