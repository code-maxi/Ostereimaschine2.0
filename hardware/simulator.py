import json
import traceback
import math
import time
import eastermath as em
import sys
import default 
import eastercanvas
import threading
import colors

class EasterSimulator:
    def __init__(self, config: dict):
        self.config = dict(default.defaultEasterControlerConfig)
        self.config.update(config)
        
        self.x_velocity = self.config['xstepper']['steps_per_millimeter']
        
        self.egg_x_steps = round(self.config['egg_length'] * self.x_velocity)
        self.egg_y_steps = self.config['ystepper']['steps_of_turn']
        
        self.egg_border_length = self.config['egg_use_percent'] / 100 * self.config['egg_length']
        self.egg_border_steps = round(self.egg_border_length * self.x_velocity)
        
        self.simulator_x = 0
        self.simulator_y = 0
        self.simulator_speed = self.config['simulator_start_speed']
        
        self.ispenup = False
        
        self.current_color = self.config['start_color']
        self.print_piority = 2
                
        self.log('Simulator __init__ with config: ', 10)
        
    def canvas_close(self):
        self.cleanup()
        print('canvas close!')
        
    def gui_debug(self, *args):
        self.canvas = eastercanvas.EasterCanvas(
            self.config,
            self.egg_y_steps / self.egg_x_steps,
            self.canvas_close
        )
        callback = em.get_save(args, 0, None)
        if callback != None:
            threading.Thread(target=callback).start()
        self.canvas.main_loop()
        
    def console_debug(self, **kwargs):
        self.console_debug_thread = threading.Thread(target=self.console_debug_thread)
        self.console_debug_thread.start()
        if kwargs.get('wait', False) == True: self.console_debug_thread.join()
        
    def log(self, obj, *args):
        prio = em.get_save(args, 0, 0) 
        if prio >= self.print_piority: print(colors.green('EasterSimulator: ' + str(obj)))
        
    def pos_to_string(self):
        dp = 1
        xsteps = round(self.x_pos())
        ysteps = round(self.y_pos())
        xdistance = round(self.x_pos() / self.x_velocity, dp)
        xpercent = round(self.x_percent() * 100, dp)
        ypercent = round(self.y_percent() * 100, dp)
        return f"({xpercent: 5.1f}% | {ypercent: 5.1f}%)_({xdistance: 5.1f}mm|    ?mm)_({xsteps: 5}x | {ysteps: 5}x)"
        
    def log_pos(self): self.log(self.pos_to_string(), 10)
        
    def x_pos(self): return self.simulator_x
    def y_pos(self): return em.modulo(self.simulator_y, self.egg_y_steps)
    def xy_pos(self): return (self.x_pos(), self.y_pos())
    
    def get_simulator_speed(self): return self.simulator_speed
    
    def set_x_pos(self, x: float): self.simulator_x = x
    def set_y_pos(self, y: float): self.simulator_y = y
    
    def x_percent(self): return self.x_pos() / self.egg_border_steps
    def y_percent(self): return self.y_pos() / self.egg_y_steps
    
    def y_caliber(self):
        xpercent = self.x_pos() / self.egg_x_steps
        return em.egg_caliber(xpercent, self.config['egg_height'])
    
    def x_delta_steps(self, xunit: float, **kwargs):
        steps = xunit
    
        if not kwargs.get('step', False):
            if xunit < -50 or xunit > 50: raise Exception(f'the x-pos ({xunit}) has to be between -50% and 50%')
            steps = xunit / 100 * self.egg_border_length * self.x_velocity
        
        return steps - self.x_pos()
        
    def y_delta_steps(self, yunit: float, **kwargs):
        newPos = yunit
        
        if not kwargs.get('step', False):
            factor = em.modulo(yunit, 100) / 100
            newPos = round(factor * self.egg_y_steps)
        
        steps1 = newPos - self.y_pos()
        steps2 = steps1 + (-self.egg_y_steps if steps1 > 0 else self.egg_y_steps)
        
        minmax = em.abs_minmax(steps1, steps2)
        index = 1 if kwargs.get('long', False) == True else 0
        
        return minmax[index]
    
    def set_pen_up(self, up: bool):
        self.ispenup = up
        self.change_color(self.current_color)
        time.sleep(self.get_simulator_speed() * 4)
        
    def penup(self):   self.set_pen_up(True)
    def pendown(self): self.set_pen_up(False)
    
    def x_stroke_steps(self): return self.x_velocity * self.config['pen_stroke_width']
    def y_stroke_steps(self): return round(self.config['pen_stroke_width'] / (self.config['egg_height'] * math.pi) * self.egg_y_steps) #TODO!
        
    def change_color(self, color: str):
        self.log(f"Changing color to {color}...", 5)
        self.current_color = color
        
        try: self.canvas.set_color(None if self.ispenup else self.current_color)
        except AttributeError: pass
        
    def update_canvas_info(self, info: dict):
        try: self.canvas.update_info(info)
        except AttributeError: pass
        
    def canvas_info_pos(self):
        string_pos = self.pos_to_string().split('_')
        return {
            'p1': string_pos[0],
            'p2': string_pos[1],
            'p3': string_pos[2]
        }
        
    def go_to(self, pxunit: float, pyunit: float, **kwargs):
        move = kwargs.get('move', False)
        step_unit = kwargs.get('step', False)
        
        xunit = pxunit + self.x_pos() if kwargs.get('rel', False) else pxunit
        yunit = pyunit + self.y_pos() if kwargs.get('rel', False) else pyunit
                
        xsteps = self.x_delta_steps(xunit, step=step_unit)
        ysteps = self.y_delta_steps(yunit, step=step_unit, long=kwargs.get('long', False))
        
        self.log(f'xstepsr={xsteps / self.egg_border_steps} ystepsr={ysteps / self.egg_y_steps} long={kwargs.get("long", False)}')
        
        self.set_x_pos(self.x_pos() + xsteps)
        self.set_y_pos(self.y_pos() + ysteps)
        
        if abs(xsteps) > 0 or abs(ysteps) > 0:
            try:
                self.canvas.go_to((
                    xsteps / self.egg_x_steps,
                    ysteps / self.egg_y_steps
                ), move, self.canvas_info_pos(), kwargs.get('info', False))
                
                speed = self.get_simulator_speed()
                if speed > 0:
                    length = em.vec_len((xsteps, ysteps))
                    sleep = length / 1000 * speed
                    time.sleep(sleep)
                    
            except AttributeError: pass
        
        return (xsteps, ysteps)
        
    def step_to(self, pos, **kwargs):
        newkwargs = dict(kwargs)
        newkwargs.update({'step':True})
        self.go_to(pos[0], pos[1], **newkwargs)
        
    def go_to_multiple(poses, **kwargs):
        for pos in poses: self.go_to(pos[0], pos[1], **kwargs)
        
    def circle(self, **kwargs):
        xpos_p = kwargs.get('xpos', self.x_pos())
        ypos_p = kwargs.get('ypos', self.y_pos())
        
        xrad = kwargs.get('rad', 100)
        yrad = kwargs.get('yrad', xrad)
        
        xpos = kwargs.get('xcenter', 0) * xrad + xpos_p
        ypos = kwargs.get('ycenter', 0) * yrad + ypos_p
        
        res = kwargs.get('res', 4)
        
        depth = kwargs.get('depth', 0)
        depthspace = "  " * depth 
        colors     = kwargs.get('colors', [self.current_color])
        colorindex = kwargs.get('colorindex', 0)
        
        self.log(f'{depthspace}drawing circle with args {kwargs}', 10)
        self.log(f'{depthspace}using color {colors[colorindex]}', 10)

        self.change_color(colors[colorindex])

        for r in range(res+1):
            angle = r / res * 2 * math.pi
            new_xpos = round(xpos + math.cos(angle) * xrad)
            new_ypos = round(ypos + math.sin(angle) * yrad)
            self.log(f'{depthspace}index={r} angle={angle}:{angle/math.pi * 180} cos={math.cos(angle)} sin={math.sin(angle)} newx={new_xpos} newy={new_ypos}')
            
            self.go_to(new_xpos, new_ypos, move=(r == 0), step=True)
            
        if kwargs.get('fill', False):
            sub_steps_x = kwargs.get('sub_steps_x', self.x_stroke_steps()) # getting pen stroke smaller
            sub_steps_y = kwargs.get('sub_steps_y', self.y_stroke_steps()) # getting pen stroke smaller
            new_xrad = xrad - sub_steps_x
            new_yrad = yrad - sub_steps_y
            max_depth = kwargs.get('maxdepth', sys.maxsize) # getting pen stroke smaller
            
            if new_xrad > 0 and new_yrad > 0 and depth < max_depth:
                new_kwargs = dict(kwargs)
                
                new_kwargs.update({
                    'rad': new_xrad,
                    'yrad': new_yrad,
                    'xpos': self.x_pos() - sub_steps_x,
                    'depth': depth + 1,
                    'xcenter': -1, # the circle is left placed
                    'colors': colors,
                    'colorindex': (colorindex + 1) % len(colors)
                })
                
                self.circle(**new_kwargs) # recursive call
                
    def sin_wave(self, **kwargs):
        width = kwargs.get('width', 100)
        seg_number = kwargs.get('seg_number', 5)
        res = kwargs.get('res', 10)
        
        old_ypos = self.y_pos()
        old_xpos = self.x_pos()
        seg_length = round(kwargs.get('length', self.egg_y_steps) / seg_number)
        
        for i in range(res * seg_number):
            xpos = math.sin(i / res * math.pi * 2) * width + old_xpos
            ypos = i / res * seg_length + old_ypos
            self.go_to(xpos, ypos, step=True)
        
    def on_console_input(self, typ: str, split: list):
        print(f'simulator typ {typ}')
        
        if typ == 'penup': self.penup()
        elif typ == 'pendown': self.pendown()
        elif typ == 'pentoggle': self.set_pen_up(not self.ispenup)
        
        elif typ == 'color': self.change_color(split[1])
        elif typ == 'hidecolor':
            self.current_color = split[1]
            try: self.canvas.set_color(None if self.ispenup else self.current_color)
            except AttributeError: pass
        
        elif typ == 'sin': self.sin_wave(200, self.egg_y_steps, 5, 50)
            
        elif typ == 'lineto' or typ == 'moveto':
            x = float(split[1])
            y = float(split[2])
            
            lw = em.get_save(split, 3, 'False') == 'True'
            
            if typ == 'lineto': self.go_to(x, y, long=lw, info=True)
            if typ == 'moveto': self.go_to(x, y, move=True, info=True)
            
            self.log(f'{typ} => {self.pos_to_string()}', 10)
            
        elif typ == 'grid':
            for x in range(-50, 50, 10):
                print(f'x = {x}%: y = ', end='')
                for y in range(10, 100, 10):
                    print(f'{y}% ', end='')
                    self.go_to(x,y, move=True)
                print('')    
                
        elif typ == 'pos': self.log_pos()
        elif typ == 'caliber': self.log(f"{self.y_caliber()}", 10)
        
        elif typ == 'circle':
            res = int(em.get_save(split, 1, 100))
            rad = int(em.get_save(split, 2, 1000))
            fill = int(em.get_save(split, 3, 1))
            rainbow = int(em.get_save(split, 1, 1))
            colors = em.rainbow_colors(rainbow) if rainbow > 0 else [self.current_color]
            print(colors)
            
            self.circle(
                rad=rad, 
                yrad=round(2/5*rad), 
                res=res, 
                fill = fill == 1, 
                colors = colors
            )
            
        else: return False
        
    def cleanup(self): pass
            
    def console_debug_thread(self):
        escape = False
        commands = []
                
        while not escape:
            if len(commands) == 0:
                inp = input(colors.blue('?: '))
                commands = inp.split('|')
            
            split = commands.pop(0).split(';')
            typ = split[0]
            
            try:
                if typ == 'ex': escape = True
                elif self.on_console_input(typ, split) == False:
                    raise Exception(f'Unbekannter typ "{typ}".', 10)
            
            except:
                self.log(f'ERROR:', 10)
                traceback.print_exc()
                
        try: self.canvas.quit()
        except AttributeError: pass
        
        self.cleanup()
        time.sleep(0.5)
        exit(0)

''''
controller = EasterSimulator({})
controller.console_debug()
controller.gui_debug()
'''
