from controller import EasterControler
from simulator import EasterSimulator
import eastermath as em
import time
import math

def act(ct: EasterSimulator):
    iterations = 10
    
    star_height = ct.egg_y_steps / iterations / 2
    star_width = ct.egg_x_steps * 0.14
    star_fill = 1
    star_fac = 0.2
    
    star_wsub = ct.x_stroke_steps()
    star_hsub = ct.y_stroke_steps()
    
    colors = ['red', 'green', 'blue']
    
    sin_seg = 15
    sin_width = 300
    
    left_line = -30
    
    egg_res = 40
    egg_fill = 3
    egg_wsub = star_wsub
    egg_hsub = star_hsub * 2
    egg_width = round(ct.egg_x_steps * 0.1)
    egg_height = star_height

    def star(w: int, h: int, fill: int, fac: float, wsub: int, hsub: int, depth: int):
        oldpos = ct.xy_pos()
        sw = round(w * fac)
        sh = round(h * fac)
        positions = [(0, -h), (sw, -sh), (w, 0), (sw, sh), (0, h), (-sw, sh), (-w, 0), (-sw, -sh), (0, -h)]
        endpositions = [(sw, -sh), (w, 0), (sw, sh), (0, h)]
        
        repeat = fill > 0 and w > 0 and h > 0 
        
        i = 0
        for pos in (positions if repeat else (positions + endpositions)):
             newpos = em.vec_add(oldpos, (pos[0], pos[1] + h))
             ct.step_to(newpos, move=i == 0)
             i += 1 
             
        if repeat:
            ct.step_to((0, hsub), rel=True)
            star(w - wsub, h - hsub, fill - 1, fac, wsub, hsub, depth + 1)
            ct.step_to((0, hsub), rel=True)
            
    def egg(xrad: int, yrad: int, fill: int):
        xypos = ct.xy_pos()
        center = em.vec_add(xypos, (0, yrad))
        
        new_xrad = xrad - egg_wsub
        new_yrad = yrad - egg_hsub
        repeat = fill > 0 and new_xrad > 0 and new_yrad > 0
        res_iterate = round(egg_res * (1 if repeat else 1.5))
        
        for r in range(res_iterate+1):
            angle = (r / egg_res + 0.75) * 2 * math.pi
            delta = (math.cos(angle) * xrad, math.sin(angle) * yrad)
            new_xypos = em.vec_add(center, delta)
            ct.step_to(new_xypos, step=True)
            
        if repeat:
            #ct.step_to((0, 0), rel=True, info=True)
            egg(new_xrad, new_yrad, fill - 1) # recursive call
            ct.step_to((0, egg_hsub * 2), rel=True, info=True)
    
    def pattern():
        ct.change_color('black')
        for n in [1, -1]:
            x = left_line * n
            
            ct.go_to(x, 0, move=True, info=True)
            ct.sin_wave(seg_number=sin_seg, width=sin_width, res=4)
            
            ct.step_to((ct.x_stroke_steps(), 0),   rel=True)
            ct.go_to(x, 0)
            
            ct.sin_wave(seg_number=sin_seg, width=-sin_width, res=4)
            ct.update_canvas_info({})
            ct.go_to(x, 0)
            
            #ct.step_to((-sin_width * 1.5, 0),   rel=True, move=True)
            #ct.step_to((0, 0), long=True, rel=True)
            
            #ct.step_to((2*sin_width * 1.5, 0),  rel=True, move=True)
            #ct.step_to((0, 0), long=True, rel=True)
    
    def stars():
        ct.go_to(0, 0, move=True)
        for s in range(iterations):
            print(f'star {s} pos {ct.pos_to_string()}')
            ct.change_color(colors[s % len(colors)])
            ct.update_canvas_info({'star': f'star  = {s}'})
            star(star_width, star_height, star_fill, star_fac, star_wsub, star_hsub, 0)

    def eggs():
        for d in [1, -1]:
            ct.go_to(left_line * d, 0, move=True)
            for s in range(iterations):
                ct.change_color(colors[s % len(colors)])
                ct.update_canvas_info({'star': f'egg   = {s} | {d}'})
                egg(egg_width, egg_height, egg_fill)
        
    stars()
    eggs()
    pattern()

sim = EasterControler(
    {
        'simulator_start_speed': 0.0,
        'start_color': 'blue',
        'penup_offset': 0.25,
        'color_pos': {
            'black': 0,
            'red': 1,
            'green': 2,
            'blue': 3,
            'orange': None
        }
    }
)
sim.run(act=act, gui=True, console=True)
