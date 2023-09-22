#unuse
from simulator import EasterSimulator
import eastermath as em
import time
import math

def act(ct: EasterSimulator):
    flower_config = {
        'leaves_config': [
            
        ]
    }
    leave_config = {
        'h2': 500,
        'h1': 1000,
        'd': 400,
        'g': 200,
        'res': 100,
        'angle': 0
    }
    def paint_leave(**config):
        alpha = math.asin(config['g'] / (2*config['d']*config['h1']))
        for a in range(config['res'] + 1):
            angle = a / config['res'] * math.pi + alpha + config['angle']


#from controller import EasterControler
sim = EasterSimulator(
    {
        'simulator_start_speed': 0.0,
        'start_color': 'red',
        'penup_offset': 0.25,
        'color_pos': {
            'black': 0,
            'red': 1,
            'green': 2,
            'blue': 3,
            'orange': None
        },
        'name': 'Sterne und Eier'
    }
)
sim.run(act=act, gui=True, console=False)