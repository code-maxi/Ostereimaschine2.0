from simulator import EasterSimulator
import eastermath as em
import shapes
import time
import math
import shapes
import random

def act(ct: EasterSimulator):
    print('pattern run')
    ct.go_to(50j, move=True)

    aviable_colors = [ 'red', 'orange', 'green', 'blue']

    triangle_width = ct.egg_border_steps * 0.3
    spiral_width = ct.egg_border_steps * 0.28

    triangle_number = 12
    triangle_fill = 2
    triangle_shrink = 0.5
    triangle_height = ct.egg_y_steps / triangle_number * 1j
    triangle_poses = [0, -0.5j, 1, 0.5j, 0]
    triangle_dot_size = ct.xy_stroke_steps() * 2
    triangle_dot_fill = 1

    print(triangle_dot_size)

    spiral_number = 6

    spiral_max_angle = 4 * math.pi
    spiral_increase = math.pi / 16
    spiral_radius_increase = (1 + ct.x_to_ysteps(1)) * spiral_width / 2 / spiral_max_angle
    spiral_radius = spiral_max_angle * spiral_radius_increase

    def triangles():
        for i in range(triangle_number):
            pos = triangle_height * i
            ct.change_color(aviable_colors[i % len(aviable_colors)], stay_up=True)
            ct.step_to(pos, move=True)

            for fill in range(triangle_fill):
                for tpos in triangle_poses:
                    delta = triangle_shrink ** fill * em.comlpex_scalar(tpos, triangle_width + triangle_height)
                    ct.step_to(pos + delta)

            ct.step_to(pos + triangle_width * 0.75 + triangle_height / 2, move=True)
            
            shapes.circle(
                ct,
                circle_rad = triangle_dot_size,
                circle_fill = triangle_dot_fill,
                circle_res = 8
            )



    spirals_pos = ct.xy_pos()
    def spirals():
        for spiral_index in range(spiral_number):
            ypos = spiral_index / spiral_number * ct.egg_y_steps * 1j
            
            ct.change_color(aviable_colors[spiral_index % len(aviable_colors)], stay_up=True)
            ct.step_to(spirals_pos + ypos, move=True)
            
            shapes.spiral(
                ct,
                spiral_max_angle = spiral_max_angle,
                spiral_start_angle = 0,
                spiral_radius_increase = spiral_radius_increase,
                spiral_angle_increase = spiral_increase
            )
            #time.sleep(0.5)
            shapes.spiral(
                ct,
                spiral_min_angle = 0,
                spiral_start_angle = spiral_max_angle,
                spiral_mirror = -1 - 1j,
                spiral_center = ct.xy_pos() + spiral_radius.imag * 1j,
                spiral_radius_increase = spiral_radius_increase,
                spiral_angle_increase = -spiral_increase
            )

    triangles()
    #spirals()

#from controller import EasterControler
sim = EasterSimulator(
    {
        'simulator_start_speed': 0.2,
        'start_color': 'green',
        'penup_offset': 0.25,
        'color_pos': {
            'purple': 0,
            'red': 1,
            'green': 2,
            'blue': 3,
            'orange': 4
        },
        #'simulator_window_width': None,
        'name': 'Musiknoten',
        'start_fullscreen': False,
        'simulator_window_height': 1000
    }
)
sim.run(act=act, gui=True, console=True, direct_run=True)
