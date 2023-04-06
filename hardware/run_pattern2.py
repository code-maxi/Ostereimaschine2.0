from simulator import EasterSimulator
import eastermath as em
import shapes
import time
import math
import shapes
import random

def act(ct: EasterSimulator):
    print('pattern run')

    aviable_colors = [ 'red', 'orange', 'green', 'blue', 'purple']

    triangle_width = ct.egg_xborder_steps * 0.25

    triangle_number = 12
    triangle_fill = 2
    triangle_shrink = 0.6
    triangle_height = ct.egg_y_steps / triangle_number * 1j
    triangle_poses = [0, -0.5j, 1, 0.5j, 0]
    triangle_dot_rad = ct.xy_stroke_steps() * 0.5
    triangle_dot_fill = 0
    triangles_xpos = ct.egg_xborder_steps * 0.5 - triangle_width

    print(triangle_dot_rad)
    
    line_types = [False, True, False] # wheather dashed
    line_dash_number = 50
    mm_way = ct.x_stroke_steps
    spiral_space = mm_way * (len(line_types)-1)

    spiral_number = 5
    spiral_width = ct.egg_xborder_steps - 2*triangle_width - 2*spiral_space
    spiral_max_angle = 6 * math.pi
    spiral_increase = math.pi / 32
    spiral_radius_increase = (1 + ct.x_to_ysteps(1)) * spiral_width / 2 / spiral_max_angle
    spiral_radius = spiral_max_angle * spiral_radius_increase
    spiral_xpos = 0#triangles_xpos - spiral_radius.real - mm_way
    spiral_min_angle = mm_way / 2 / spiral_radius_increase.real

    def triangles(xf: float, types: list):
        for typ in types:
            for i in range(triangle_number):
                pos = triangles_xpos * xf + triangle_height * i
                ct.change_color(aviable_colors[i % len(aviable_colors)], stayup=True)

                if typ == 'tri':
                    ct.step_to(pos, move=True)

                    for fill in range(triangle_fill):
                        for tpos in triangle_poses:
                            delta = triangle_shrink ** fill * em.comlpex_scalar(tpos, triangle_width * xf + triangle_height)
                            ct.step_to(pos + delta)

                if typ == 'circ':
                    ct.step_to(pos + triangle_width * 0.75 * xf + triangle_height / 2, move=True)
                    
                    shapes.circle(
                        ct,
                        circle_rad = triangle_dot_rad,
                        circle_fill = triangle_dot_fill,
                        circle_res = 8
                    )
                    

    spirals_pos = ct.xy_pos()
    def spirals():
        ct.update_info({ 'spiral_min_angle': f'spiral_min_angle={round(spiral_min_angle) * 180 / math.pi}' })
        for spiral_index in range(spiral_number):
            ypos = spiral_xpos + spiral_index / spiral_number * ct.egg_y_steps * 1j
            
            color = aviable_colors[spiral_index % len(aviable_colors)]
            ct.step_to(spirals_pos + ypos, move=True, color=color)
            
            shapes.spiral(
                ct,
                spiral_max_angle = spiral_max_angle,
                spiral_start_angle = spiral_min_angle,
                spiral_radius_increase = spiral_radius_increase,
                spiral_angle_increase = spiral_increase
            )
            
            #time.sleep(0.5)
            shapes.spiral(
                ct,
                spiral_min_angle = spiral_min_angle,
                spiral_start_angle = spiral_max_angle,
                spiral_mirror = -1 - 1j,
                spiral_center = ct.xy_pos() + spiral_radius.imag * 1j,
                spiral_radius_increase = spiral_radius_increase,
                spiral_angle_increase = -spiral_increase
            )
            
    def lines(xf: float):
        for line in range(len(line_types)):
            dash = line_types[line]
            xpos = (triangles_xpos - mm_way * line) *  xf
            color = aviable_colors[line % len(aviable_colors)]
            
            ct.step_to(xpos, move=True, color=color)
            
            move = False
            for f in range(line_dash_number + 1):
                ct.step_to(xpos + f / line_dash_number * ct.egg_y_steps * 1j, move=move)
                if dash:
                    ct.change_color(aviable_colors[int(f / len(aviable_colors)) % len(aviable_colors)])
                    move = not move
            
    triangles(1, ['tri', 'circ'])
    lines(1)
    
    spirals()
    triangles(-1, ['tri'])
    lines(-1)
    
    ct.go_home()
    #line_dots()
    #sin_dots()

#from controller import EasterControler
sim = EasterSimulator(
    {
        'egg_use_percent': 65,
        'simulator_start_speed': 0.0,
        'start_color': 'green',
        'penup_offset': 0.25,
        'color_pos': {
            'purple': 0,
            'blue': 1,
            'green': 2,
            'orange': 3,
            'red': 4
        },
        #'simulator_window_width': None,
        'name': 'Spiralen und Dreiecke Typ 2',
        'start_fullscreen': False,
        #'simulator_window_height': 1000
    }
)
sim.run(act=act, gui=True, console=True, direct_run=True)
