#unuse
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    kreise_anzahl = 12
    kreise_breite = [0.35, 0.2]
    kreise_farben = [ 'orange', 'blue', 'green' ]

    kringel_anzahl = 30
    kringel_farben = [ 'orange', 'purple' ]

    wellen_anzahl = 20

sim = EasterCanvas(
    {
        'egg_use_percent': 65,
        'simulator_start_speed': 0.05,
        'start_color': 'green',
        'penup_offset': 0.25,
        'color_pos': {
            'purple': 0,
            'blue': 1,
            'green': 2,
            'orange': 3,
            'red': 4
        },
        'name': 'Glücksklee',
        'start_fullscreen': False
    }
)
sim.run(act=act, gui=True, console=True, direct_run=True)