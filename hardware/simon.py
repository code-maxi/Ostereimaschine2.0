from simulator import EasterSimulator
import eastermath as em
import time
import math

def act(ct: EasterSimulator):
    iterations = 10
    
    star_height = ct.egg_y_steps / iterations / 2 * 1j
    star_width = ct.egg_x_steps * 0.12
    star_fill = 1
    star_fac = 0.2
    
    star_wsub = ct.x_stroke_steps()
    star_hsub = ct.y_stroke_steps() * 1j
    
    colors = ['red', 'green', 'blue']
    
    egg_res = 40
    egg_fill = 2
    egg_sub = star_wsub + star_hsub * 2
    egg_size = ct.egg_xborder_steps/4 - star_width/2 + star_height
    
    left_line = egg_size.real - ct.egg_xborder_steps/2
    
    sin_seg = 15
    sin_width = egg_size.real * 0.5

    def star(w: int, h: int, fill: int, fac: float, wsub: int, hsub: int, depth: int):
        oldpos = ct.xy_pos()
        sw = round(w * fac)
        sh = em.round_complex(h * fac)
        positions = [(0 - h), (sw - sh), (w), (sw + sh), (h), (-sw + sh), (-w), (-sw - sh), (-h)]
        endpositions = [(sw - sh), (w), (sw + sh), (h)]
        
        repeat = fill > 0 and w > 0 and h.imag > 0 
        
        i = 0
        for pos in (positions if repeat else (positions + endpositions)):
             newpos = oldpos + pos + h
             ct.step_to(newpos, move=i == 0)
             i += 1 
             
        if repeat:
            ct.step_to(hsub, rel=True)
            star(w - wsub, h - hsub, fill - 1, fac, wsub, hsub, depth + 1)
            ct.step_to(hsub, rel=True)
            
    def egg(rad: complex, fill: int):
        center = ct.xy_pos() + rad.imag*1j
        
        new_rad = rad - egg_sub

        repeat = fill > 0 and new_rad.real > 0 and new_rad.imag > 0
        res_iterate = round(egg_res * (1 if repeat else 1.5))
        
        for r in range(res_iterate+1):
            angle = (r / egg_res + 0.75) * 2 * math.pi
            delta = math.cos(angle) * rad.real + math.sin(angle) * rad.imag * 1j
            new_xypos = center + delta
            ct.step_to(new_xypos)
            
        if repeat:
            egg(new_rad, fill - 1) # recursive call
            ct.step_to(egg_sub.imag * 2j, rel=True, info=True)
    
    def pattern():
        ct.change_color('black')
        for n in [1, -1]:
            x = left_line * n
            
            ct.step_to(x, move=True, step=True, info=True)
            ct.sin_wave(seg_number=sin_seg, width=sin_width * n, res=32)
            
            #ct.step_to((ct.x_stroke_steps(), 0),   rel=True)
            #ct.go_to(x, 0)
            
            #ct.sin_wave(seg_number=sin_seg, width=-sin_width, res=4)
            #ct.update_info({})
            #ct.go_to(x, 0)
            
            #ct.step_to((-sin_width * 1.5, 0),   rel=True, move=True)
            #ct.step_to((0, 0), long=True, rel=True)
            
            #ct.step_to((2*sin_width * 1.5, 0),  rel=True, move=True)
            #ct.step_to((0, 0), long=True, rel=True)
    
    def stars():
        ct.go_to(0, move=True)
        for s in range(iterations):
            print(f'star {s} pos {ct.pos_to_string()}')
            ct.change_color(colors[s % len(colors)])
            ct.update_info({'star': f'star  = {s}'})
            star(star_width, star_height, star_fill, star_fac, star_wsub, star_hsub, 0)

    def eggs():
        for d in [1, -1]:
            ct.step_to(left_line * d, move=True)
            for s in range(iterations):
                ct.change_color(colors[s % len(colors)])
                ct.update_info({'star': f'egg   = {s} | {d}'})
                egg(egg_size, egg_fill)
    ct.pendown()    
    
    stars()
    eggs()
    pattern()
    
    ct.go_home()

from controller import EasterControler
sim = EasterControler(
    {
        'simulator_start_speed': 0.0,
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
sim.run(act=act, gui=True, console=True)
