#Sincostan:Da ich ein Computer bin, ist Mathe meine Leidenschaft!|Ich plotte dir die Funktionsgraphen der drei Trigonomentrischen Funktionen auf das Ei.
import sys
import random
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    rainbow = ['red', 'orange', 'green', 'blue', 'purple']
    sin_width = ct.egg_xborder_steps * 0.2
    distance = 2 * ct.x_velocity
    sin_number = 12
    sin_res = 32
    
    def kringel(d: float):
        colori = 0
        xpos = -ct.egg_xborder_steps * 0.5
        while xpos < - sin_width - distance:
            ct.step_to(xpos * d, move=True, color=rainbow[colori % len(rainbow)])
            ct.step_to(0, rel=True, long=True)
            colori += 1
            xpos += ct.x_stroke_steps * 2

    functions = [
        lambda a: math.sin(a) * sin_width,
        lambda a: math.cos(a) * sin_width,
        #lambda a: (math.cos(a) + math.sin(a) - math.sin(2*a)) * sin_width,
        lambda a: math.tan(a) * sin_width * 0.1
    ]
            
    def sin_curves():
        for f in range(len(functions)):
            fun = functions[f]
            color = rainbow[f]
            #yoffset = ct.egg_y_steps / sin_number / len(rainbow) * 1j * f
            for s in range(sin_number * sin_res):
                angle = s / sin_res * math.pi
                delta = fun(angle) + s / sin_res / sin_number * ct.egg_y_steps * 1j
                ct.step_to(delta, move = s == 0, color = color)
    
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
        'purple': 4,
        'blue': 3,
        'green': 2,
        'orange': 1,
        'red': 0
    },
    'name': 'Sincostan'
}
(EasterControler(config) if sys.argv[1] == 'C' else EasterCanvas(config)).run(act=act)
