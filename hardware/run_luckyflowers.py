import random
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    lucky_clover_colors = ['green', 'green', 'yellow', 'yellow', 'yellow', 'orange']
    flower_number = 6
    flower_size = ct.egg_xborder_steps * 0.3
    
    flower_thickness = 0.75
    #flower_leave_height = flower_size / 3 * 1j
    flower_subsize = (100 + flower_thickness * 100j) * 1

    flower_fill = len(lucky_clover_colors) - 1
    flower_halffill = 1
    flower_xpos = 0
    #flower_dot_radius = flower_size * 0.2

    line_spacing = ct.x_velocity
    line_colors = [ 'red', 'orange', 'yellow' ]
    line_sin_width = ct.egg_xborder_steps/4 - flower_size/2 - line_spacing
    line_sin_number = 10
    line_sin_res = 25
    line_sin_offset = 3 * ct.y_velocity

    def lucky_clover(global_rotate: float, fac: float):
        size = (flower_size + flower_size * flower_thickness * 1j) * fac
        c = 0
        while em.complex_bigger(size, flower_subsize) and c <= flower_fill:
            color = lucky_clover_colors[c % len(lucky_clover_colors)]
            for i in range(4):
                angle = i / 2 * math.pi
                turn = angle + global_rotate
                shapes.heart(
                    ct,
                    heart_size = size,
                    heart_turn = turn,
                    heart_colors = [color],
                    heart_subsize = flower_subsize,
                    heart_parts = 2 if c > flower_halffill else 4,
                    heart_t = 0.3,
                    heart_stretch = 1 + ct.y_velocity / ct.x_velocity * 1j
                )
            size -= flower_subsize
            c += 1
        '''shapes.circle(
            ct,
            circle_rad = flower_dot_radius + ct.x_to_ysteps(flower_dot_radius),
            circle_fill = 100,
            #circle_colors=['black'],
            circle_substeps = ct.xy_stroke_steps() / 2
        )'''

    def flowers():
        for f in range(0,flower_number):
            ypos = (f / flower_number) * ct.egg_y_steps * 1j
            ct.step_to(flower_xpos + ypos, move=True)
            turn = 0 if (f+1) % 2 == 0 else math.pi/4#random.random() * 2 * math.pi
            size = (0.1 if f % 2 == 0 else -0.1) + 1
            lucky_clover(turn, size)

    def lines(fac: float):
        for c in range(len(line_colors)):
            color = line_colors[c]
            xpos = (ct.egg_xborder_steps/2 - line_sin_width) * fac
            ypos = line_sin_offset * c * 1j
            oldpos = xpos + ypos
            for s in range(line_sin_res * line_sin_number):
                angle = s / line_sin_res * 2 * math.pi
                delta = em.hill_sin(angle) * line_sin_width + s / line_sin_res / line_sin_number * ct.egg_y_steps * 1j
                ct.step_to(oldpos + delta, move = s == 0, color = color)

    lines(1)
    flowers()
    lines(-1)
    '''ct.go_to(20j, move=True)
    lucky_clover(math.pi / 4, 1)

    print(ct.y_velocity / ct.x_velocity)
    ct.go_to(80j, move=True)
    lucky_clover(math.pi / 4)'''


#from controller import EasterControler
sim = EasterCanvas(
    {
        'egg_use_percent': 60,
        'simulator_start_speed': 0.0,
        'start_color': 'yellow',
        'penup_offset': 0.25,
        'color_pos': {
            'black': 4 + 1j,
            'yellow': 3,
            'orange': 2,
            'green': 1,
            'red': 0
        },
        'name': 'Glücksklee',
        'start_fullscreen': False
    }
)
<<<<<<< HEAD
sim.run(act=act, gui=True, console=False, direct_run=False)
=======
sim.run(act=act, gui=True, console=True, direct_run=True)
>>>>>>> 607f30801e16d8cdaa5f09a0dcd37572b7738781
