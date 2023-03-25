#from controller import EasterController
from simulator import EasterSimulator
import eastermath as em
import time

ct = EasterSimulator({})

def act():
    iterations = 4

    def star(w: int, h: int, fill: int, fac: float, wsub: int, hsub: int, depth: int):
        oldpos = ct.xy_pos()
        sw = round(w * fac)
        sh = round(h * fac)
        positions = [(0, -h), (sw, -sh), (w, 0), (sw, sh), (0, h), (-sw, sh), (-w, 0), (-sw, -sh), (0, -h)]
        endpositions = [(sw, -sh), (w, 0), (sw, sh), (0, h)]
        
        #ct.update_canvas_info({'depth': f'depth = {depth}'})
        
        repeat = fill > 0 and w > 0 and h > 0 
        
        i = 0
        for pos in (positions if repeat else (positions + endpositions)):
             newpos = em.vec_add(oldpos, (pos[0], pos[1] + h))
             ct.step_to(newpos, move=i == 0)
             #time.sleep(0.25)
             i += 1 
             
        if repeat:
            ct.step_to((0, hsub), rel=True)
            star(w - wsub, h - hsub, fill - 1, fac, wsub, hsub, depth + 1)
            ct.step_to((0, hsub), rel=True)
            
    star_height = ct.egg_y_steps / iterations / 2
    star_width = ct.egg_x_steps * 0.1
    star_fill = 3
    star_fac = 0.2
    star_wsub = ct.x_stroke_steps()
    star_hsub = ct.y_stroke_steps()
    colors = em.rainbow_colors(1)

    for s in range(iterations):
        print(f'star {s} pos {ct.pos_to_string()}')
        ct.change_color(colors[s % len(colors)])
        ct.update_canvas_info({'star': f'star = {s}'})
        star(star_width, star_height, star_fill, star_fac, star_wsub, star_hsub, 0)
        ct.update_canvas_info({})

ct.console_debug()
ct.gui_debug(act)
