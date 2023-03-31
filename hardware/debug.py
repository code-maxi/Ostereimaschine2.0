from simulator import EasterSimulator
import eastermath as em
import time
import math
import shapes

def act(ct: EasterSimulator):
    ct.go_to(50j, move=True)
    '''shapes.circle(
        ct,
        circle_rad=300 + 300j,
        circle_center=0,
        circle_colors=['black'] + ['red']*10,
        circle_fill=5
    )
    shapes.flower(
        ct, 
        fcurve_size=(1200 + 800j), 
        fcurve_center=(1),
        fcurve_leaves=10, 
        fcurve_rmin=0.55, 
        fcurve_rmax=0.8,
        dot_size=0.4,

        circle_colors=['black'] + ['red'] * 5,
        circle_fill = 5,
        
        fcurve_colors=['black'] + ['green'] * 5,
        fcurve_fill = 3,
        fcurve_subsize = 0.9
    )'''
    for a in range(4):
        shapes.heart(
            ct,
            heart_w = 500,
            heart_h = 600,
            heart_t = 2,
            heart_turn = a / 4 * math.pi * 2 + math.pi/8
        )

#from controller import EasterControler
sim = EasterSimulator(
    {
        'simulator_start_speed': 0.1,
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
sim.run(act=act, gui=True, console=True, direct_run=True)
