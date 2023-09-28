#Serie:Ein Serienei.
import sys
import random
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    letters = {
        's': [ 0, 1j, 0.5+1j, 0.5, 1, 1+1j ],
        'e': [ 1j, 0, 0.5, 0.5+1j, 0.5, 1, 1+1j ],
        'r': [ 0, 1, 1+1j, 0.5+1j, 0.5, 1j ],
        'i': [ 0.5j, 1+0.5j ]
    }
    text = [
        ("    se    ", "blue"),
        ("   seri   ", "blue"),
        ("  serieS  ", "purple"),
        (" serieSER ", "blue"),
        ("serieSERIE", "green"),
        (" rieSERIE ", "yellow"),
        ("  eSERIE  ", "orange"),
        ("   ERIE   ", "red"),
        ("    IE    ", "red")
    ]
    fac = 1.6
    serienumber = 2
    size = (ct.egg_xborder_steps/len(text) + ct.egg_y_steps/len(text[0][0])/serienumber * 1j)/fac

    for serie in range(serienumber):
        pos = ct.egg_xborder_steps/2 - size.real
        print(f'Serie {serie}')
        for line in text:
            pos = pos.real + ct.egg_y_steps/serienumber * serie * 1j
            for letter in line[0]:
                move = True
                lowerletter = letter.lower()
                if lowerletter != ' ':
                    for bold in ([0, 1] if letter.isupper() else [0]):
                        offset = (20 + 20j) * bold
                        for letterpos in (letters[lowerletter] if bold % 2 == 0 else reversed(letters[lowerletter])):
                            ct.step_to(pos + letterpos.real*size.real + letterpos.imag*size.imag*1j + offset, move=move, color=line[1])
                            move = False
                pos += size.imag*fac*1j
            pos -= size.real*fac


#from controller import EasterControler
config = {
    'egg_use_percent': 60,
    'simulator_start_speed': 0.0,
    'start_color': 'orange',
    'penup_offset': 0.25,
    'color_pos': {
        'blue': 4,
        'purple': 3,
        'green': 2,
        'orange': 1,
        'red': 0
    },
    'name': 'Glücksklee'
}
EasterCanvas(config).run(act=act)
#(EasterControler(config) if sys.argv[1] == 'C' else EasterCanvas(config)).run(act=act)