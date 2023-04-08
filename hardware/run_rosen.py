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
    rose_max_angle = 2 * math.pi * 5
    rose_radius_increase = (1 + ct.x_to_ysteps(1)) * rose_width / 2 / rose_max_angle
    rose_colors = ['red', 'orange', 'purple']

    leave_width = rose_width * 0.6
    leaves_xpos = ct.egg_xborder_steps/2 - leave_width
    leave_height = ct.x_to_ysteps(leave_width)
    leave_angle = 180/math.pi * 30
    leave_colors = ['green']*3 + ['yellow'] * 10
    leave_fill = len(leave_colors)

    def roses():
        for r in range(rose_number):
            ypos = r / rose_number * ct.egg_y_steps * 1j
            color = rose_colors[r % len(rose_colors)]
            print(color)
            ct.change_color(color, stayup=True)
            ct.step_to(ypos, move=True)
            shapes.rose(
                ct,
                rose_max_angle = rose_max_angle,
                rose_radius_increase = rose_radius_increase,
                rose_hill_number = 0.5,
                rose_hill_size = 0.2
            )

            for leave_xpos in [leaves_xpos,-leaves_xpos]:
                leave_ypos = ((r+0.5) / rose_number) * ct.egg_y_steps * 1j
                ct.step_to(leave_xpos + leave_ypos, move=True)
                for yfac in [1, -1]:
                    turn = yfac*leave_angle if leave_xpos < 0 else math.pi - yfac*leave_angle
                    shapes.heart(
                        ct,
                        heart_size = leave_width + leave_height,
                        heart_turn = turn,
                        heart_fill = leave_fill,
                        heart_subsize = ct.xy_stroke_steps() * 1.5,
                        heart_colors = leave_colors,
                        heart_stretch = 1 + ct.y_velocity / ct.x_velocity * 1j,
                        heart_onecirc = True
                    )

    roses()

sim = EasterCanvas(
    {
        'egg_use_percent': 60,
        'simulator_start_speed': 0,
        'start_color': 'green',
        'penup_offset': 0.25,
        'color_pos': {
            'yellow': 4,
            'green': 3,
            'purple': 2,
            'orange': 1,
            'red': 0
        },
        #'simulator_window_width': None,
        'name': 'Rosen',
        'start_fullscreen': False
    }
)
sim.run(act=act, gui=True, console=True, direct_run=True)
