#Schulkunst:Ein Schulkunstei, welches jedes mal ein bisschen anders aussieht.
import sys
import random
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    rainbow = ['red', 'orange', 'green', 'blue', 'purple']
    textsize = (1+5j)*210
    textpos = -textsize.real*2

    shapes.drawString(
        ct, 
        text="SCHULKUNST", 
        size=textsize, 
        pos=textpos,
        colors=rainbow,
        turn=-math.pi/2,
        boldoff=15+40j
    )

    sin_width = ct.egg_xborder_steps * 0.08
    sin_number = 10
    sin_res = 32

    for d in [1, -1]:
        for o in range(len(rainbow)):
            color = rainbow[o]
            offset = ct.egg_y_steps / sin_number / len(rainbow) * 1j * o + (sin_width - ct.egg_xborder_steps/2)*d
            for s in range(sin_number * sin_res):
                angle = s / sin_res * math.pi
                delta = math.sin(angle) * sin_width + s / sin_res / sin_number * ct.egg_y_steps * 1j
                ct.step_to(delta + offset, move = s == 0, color = color)

#from controller import EasterControler
config = {
    'egg_use_percent': 60,
    'simulator_start_speed': 0,
    'start_color': 'red',
    'penup_offset': 0.25,
    'color_pos': {
        'red': 4 ,
        'orange': 3,
        'green': 2,
        'blue': 1,
        'purple': 0
    },
    'name': 'Glücksklee',
    'start_fullscreen': True
}
EasterCanvas(config).run(act=act)
#(EasterControler(config) if sys.argv[1] == 'C' else EasterCanvas(config)).run(act=act)