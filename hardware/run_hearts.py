from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import time
import math
import shapes
import random

def act(ct: EasterCanvas):
    print('pattern run')

    aviable_colors = [ 'red', 'orange', 'green', 'blue', 'purple']

    line_types = [False, True, False] # wheather dashed
    line_dash_number = 60
    mm_way = ct.x_stroke_steps / 2

    hearts_number = 10
    hearts_xpos = 0
    hearts_width = 0.35 * ct.egg_xborder_steps
    heart_height_f = 0.9
    heart_t = 0.3
    heart_fill = 4

    triangle_number = 12
    triangle_fill = 2
    triangle_shrink = 0.6
    triangle_height = ct.egg_y_steps / triangle_number * 1j
    triangle_poses = [0, -0.5j, 1, 0.5j, 0]
    triangle_dot_rad = ct.xy_stroke_steps() * 0.5
    triangle_dot_fill = 0
    triangle_width = (ct.egg_xborder_steps - hearts_width)/2 - mm_way * (len(line_types)+2)
    triangles_xpos = ct.egg_xborder_steps/2 - triangle_width

    curl_number = 20
    curl_width = triangle_width
    curl_xpos = -ct.egg_xborder_steps/2 + curl_width
    curl_colors = aviable_colors

    def hearts():
        heart_height = ct.egg_y_steps / (hearts_number) * heart_height_f * 1j 
        for h in range(hearts_number):
            xfac = 1 if h % 2 == 0 else -1
            color = aviable_colors[h % len(aviable_colors)]
            xpos = hearts_width / 2 * xfac + hearts_xpos
            ypos = h / hearts_number * ct.egg_y_steps * 1j - heart_height/2

            ct.step_to(xpos + ypos, move=True, color=color)
            shapes.heart(
                ct, 
                heart_size = hearts_width + heart_height,
                heart_t = heart_t,
                heart_subsize = ct.xy_stroke_steps() * 1.5,
                heart_halffill = heart_fill,
                heart_turn = 0 if h % 2 == 1 else math.pi,
                heart_fill = heart_fill
            )

    def triangles(xf: float, types: list):
        #for typ in types:
        for i in range(triangle_number):
            pos = triangles_xpos * xf + triangle_height * i
            ct.change_color(aviable_colors[i % len(aviable_colors)], stayup=True)

            if 'tri' in types:
                ct.step_to(pos, move=True)

                for fill in range(triangle_fill):
                    for tpos in triangle_poses:
                        delta = triangle_shrink ** fill * em.comlpex_scalar(tpos, triangle_width * xf + triangle_height)
                        ct.step_to(pos + delta)

            if 'circ' in types:
                ct.step_to(pos + triangle_width * 0.75 * xf + triangle_height / 2, move=True)
                
                shapes.circle(
                    ct,
                    circle_rad = triangle_dot_rad,
                    circle_fill = triangle_dot_fill,
                    circle_res = 8
                )
                
        '''ct.step_to(triangles_xpos * xf, move=True)
        ct.step_to(0, rel=True, long=True)'''

    def lines(xf: float):
        for line in range(len(line_types)):
            dash = line_types[line]
            xpos = (triangles_xpos - mm_way * (line+1)) *  xf
            color = aviable_colors[line % len(aviable_colors)]
            
            ct.step_to(xpos, move=True, color=color, stayup=True)
            
            move = False
            for f in range(line_dash_number + 2):
                dashcolor = aviable_colors[int(f / line_dash_number * len(aviable_colors)) % len(aviable_colors)]
                ct.step_to(
                    xpos + f / line_dash_number * ct.egg_y_steps * 1j,
                    move=move, color = dashcolor if dash and move else ct.current_color
                )
                if dash: move = not move

    def curl():
        ct.step_to(curl_xpos, move=True)
        shapes.curl(
            ct,
            curl_number = curl_number,
            curl_size = curl_width + ct.egg_y_steps * 1j,
            curl_height_fac = 0.5,
            curl_center = -0.5,
            curl_colors = curl_colors
        )

    triangles(1, ['tri', 'circ'])
    lines(1)
    hearts()
    curl()
    lines(-1)
    
    #ct.go_to(20 + 50j)
    #ct.go_to(30 + 60j, move=True)

from controller import EasterControler
sim = EasterControler(
    {
        'egg_use_percent': 62.5,
        'simulator_start_speed': 0.1,
        'start_color': 'orange',
        'color_pos': {
            'purple': 0,
            'blue': 1,
            'green': 2,
            'orange': 3,
            'red': 4
        },
        'name': 'Herzen',
        'start_fullscreen': False,
        #'simulator_window_height': 1000
    }
)
sim.run(act=act, gui=True, console=True, direct_run=False)
