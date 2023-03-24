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
        
        self.current_color = self.config['start_color']
        self.print_piority = 2
        
        if self.config['simulator_on']: self.init_canvas()
        
        self.log('Simulator __init__ with config: ', 10)
        
    def init_canvas(self):
        self.canvas = eastercanvas.EasterCanvas(self.config)
        
    def log(self, obj, *args):
        prio = em.get_save(args, 0, 0) 
        if prio >= self.print_piority: print(colors.green('EasterControler: ' + str(obj)))
        
    def pos_to_string(self):
        dp = 1
        xsteps = round(self.x_pos(), dp)
        ysteps = round(self.y_pos(), dp)
        xdistance = round(self.x_pos() / self.x_velocity, dp)
        xpercent = round(self.x_percent() * 100, dp)
        ypercent = round(self.y_percent() * 100, dp)
        return f"({xpercent}% | {ypercent}%) ({xdistance}mm | ?mm) ({xsteps}x | {ysteps}x)"
        
    def log_pos(self): self.log(self.pos_to_string(), 10)
        
    def x_pos(self): return self.simulator_x
    def y_pos(self): return em.modulo(self.simulator_y, self.egg_y_steps)
    
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
        
    def change_color(self, color: str):
        self.log(f"Changing color to {color}...", 5)
        self.current_color = color
        if self.config['simulator_on']: self.canvas.set_color(self.current_color)
        
    def go_to(self, xunit: float, yunit: float, **kwargs):
        move = kwargs.get('move', False)
        step_unit = kwargs.get('step', False)
        
        xsteps = self.x_delta_steps(xunit, step=step_unit)
        ysteps = self.y_delta_steps(yunit, step=step_unit, long=kwargs.get('long', False))
        
        self.log(f'xstepsr={xsteps / self.egg_border_steps} ystepsr={ysteps / self.egg_y_steps} long={kwargs.get("long", False)}')
        
        try:
            self.canvas.go_to((
                xsteps / self.egg_x_steps,
                ysteps / self.egg_y_steps
            ), move)
        except AttributeError: pass
            
        self.set_x_pos(self.x_pos() + xsteps)
        self.set_y_pos(self.y_pos() + ysteps)
        
        return (xsteps, ysteps)
        
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
                    'depth': depth + 1,
                    'xcenter': -1, # the circle is left placed
                    'colors': colors,
                    'colorindex': colorindex + 1 % len(colors)
                })
                
                self.circle(**new_kwargs) # recursive call
        
    def on_console_input(self, typ: str, split: list[str]):
        if typ == 'color': self.change_color(split[1])
            
        elif typ == 'lineto' or typ == 'moveto':
            x = float(split[1])
            y = float(split[2])
            
            lw = em.get_save(split, 3, 'False') == 'True'
            
            if typ == 'lineto': self.go_to(x, y, long=lw)
            if typ == 'moveto': self.go_to(x, y, move=True)
            
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
            res = int(split[1])
            rad = int(split[2])
            self.circle(rad=rad, yrad=round(2/5*rad), res=res)
            
        else: return False
        
    def cleanup(self): pass
        
    def consoleDebug(self):
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
                elif self.on_console_input(typ, split) != False: pass
                else: raise Exception(f'Unbekannter typ "{typ}".', 10)
            
            except:
                self.log(f'ERROR:', 10)
                traceback.print_exc()
                
        if self.config['simulator_on']: self.canvas.quit()
        
        self.cleanup()
        exit(0)
        
controller = EasterSimulator({})
thread = threading.Thread(target=controller.consoleDebug)
thread.start()
controller.canvas.main_loop()
