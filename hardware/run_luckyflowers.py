import random
from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    flower_number = 5
    flower_size = ct.egg_xborder_steps * 0.3
    
    flower_thickness = 0.8
    #flower_leave_height = flower_size / 3 * 1j
    flower_subsize = (50 + flower_thickness * 166j) * 3.5

    flower_fill = 100
    flower_halffill = flower_fill - 1
    flower_xpos = 0
    #flower_dot_radius = flower_size * 0.2

    lucky_clover_colors = ['green'] * 1 + ['yellow', 'orange'] + ['green'] * 10

    line_spacing = 1.5 * ct.x_velocity
    line_colors = [ 'red', 'orange', 'yellow' ]
    line_sin_width = ct.egg_xborder_steps/4 - flower_size/2 - line_spacing
    line_sin_number = 10
    line_sin_res = 25
    line_sin_offset = 3 * ct.y_velocity

    def lucky_clover(global_rotate: float, fac: float):  
        for i in range(4):
            angle = i / 2 * math.pi
            turn = angle + global_rotate
            size = (flower_size + flower_size * flower_thickness * 1j) * fac
            shapes.heart(
                ct,
                heart_size = size,
                heart_turn = turn,
                heart_fill = flower_fill,
                heart_halffill = flower_halffill,
                heart_colors = lucky_clover_colors,
                heart_subsize = flower_subsize * fac,
                heart_stretch = 1 + ct.y_velocity / ct.x_velocity * 1j
            )
        '''shapes.circle(
            ct,
            circle_rad = flower_dot_radius + ct.x_to_ysteps(flower_dot_radius),
            circle_fill = 100,
            #circle_colors=['black'],
            circle_substeps = ct.xy_stroke_steps() / 2
        )'''

    def flowers():
        for f in range(flower_number):
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
                delta = math.sin(angle) * line_sin_width + s / line_sin_res / line_sin_number * ct.egg_y_steps * 1j
                ct.step_to(oldpos + delta, move = s == 0, color = color)

    #lines(1)
    flowers()
    lines(-1)
    '''ct.go_to(20j, move=True)
    lucky_clover(math.pi / 4, 1)

    print(ct.y_velocity / ct.x_velocity)
    ct.go_to(80j, move=True)
    lucky_clover(math.pi / 4)'''


from controller import EasterControler
sim = EasterControler(
    {
        'egg_use_percent': 63,
        'simulator_start_speed': 0.0,
        'start_color': 'green',
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
sim.run(act=None, gui=True, console=True, direct_run=False)