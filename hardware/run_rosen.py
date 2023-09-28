#Rosen:Blaue, rote und rosane Rosen mit Blättern.
import sys
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import time
import math
import shapes
import random

def act(ct: EasterCanvas):
    rose_width = 0.6 * ct.egg_xborder_steps
    rose_number = 6
    rose_max_angle = 2 * math.pi * 6
    rose_radius_increase = (1 + ct.x_to_ysteps(1)) * rose_width / 2 / rose_max_angle
    rose_colors = ['red', 'blue']

    leave_width = rose_width * 0.55
    leaves_xpos = ct.egg_xborder_steps/2 - leave_width
    leave_height = ct.x_to_ysteps(leave_width) * 1.2
    leave_angle = 0.2 * math.pi
    leave_colors = [['green'], ['green'], ['yellow']]
    leave_fill = 100

    def roses():
        for r in range(rose_number):
            ypos = r / rose_number * ct.egg_y_steps * 1j
            color = rose_colors[r % len(rose_colors)]
            ct.change_color(color, stayup=True)
            ct.step_to(ypos, move=True)
            shapes.rose(
                ct,
                rose_max_angle = rose_max_angle,
                rose_radius_increase = rose_radius_increase,
                rose_hill_number = 0.5,
                rose_hill_size = 0.27
            )

            for leave_xpos in [leaves_xpos,-leaves_xpos]:
                leave_ypos = ((r+0.5) / rose_number) * ct.egg_y_steps * 1j
                ct.step_to(leave_xpos + leave_ypos, move=True, color=leave_colors[0][0])
                d = em.direction(leave_xpos)
                yi = 0
                for yfac in [d, -d, d]:
                    turn = yfac*leave_angle if leave_xpos > 0 else math.pi - yfac*leave_angle
                    subsize = ct.xy_stroke_steps() * 1.5
                    size = (leave_width + leave_height) * (1.1 if leave_xpos * yfac > 0 else 0.9)
                    fill = leave_fill if yi == 2 else 1
                    size -= subsize * int(yi / 2)
                    colors = leave_colors[yi]
                    shapes.heart(
                        ct,
                        heart_size = size,
                        heart_turn = turn,
                        heart_fill = fill,
                        heart_subsize = subsize,
                        heart_colors = colors,
                        heart_stretch = 1 + ct.y_velocity / ct.x_velocity * 1j,
                        heart_onecirc = True
                    )
                    yi += 1

    roses()

from controller import EasterControler
config = {
    'egg_use_percent': 60,
    'simulator_start_speed': 0,
    'start_color': 'green',
    'penup_offset': 0.25,
    'color_pos': {
        'purple': 4 + 1j,
        'yellow': 3,
        'green': 2,
        'blue': 1,
        'red': 0
    },
    'name': 'Rosen'
}
(EasterControler(config) if sys.argv[1] == 'C' else EasterCanvas(config)).run(act=act)
