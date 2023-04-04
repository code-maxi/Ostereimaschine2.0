import keyboard
import json
import traceback
import math
import time
import eastermath as em
import sys
import default 
import eastercanvas
import threading

class EasterSimulator:
    def __init__(self, config: dict):
        self.config = dict(default.defaultEasterControlerConfig)
        self.config.update(config)
        
        self.x_velocity = self.config['xstepper']['steps_per_millimeter']
        self.y_velocity = self.config['ystepper']['steps_of_turn'] / (math.pi * self.config['egg_height'])

        self.x_stroke_steps = self.x_velocity * self.config['pen_stroke_width']
        self.y_stroke_steps =  self.x_to_ysteps(self.x_stroke_steps) #TODO!
        
        self.egg_x_steps = round(self.config['egg_length'] * self.x_velocity)
        self.egg_y_steps = self.config['ystepper']['steps_of_turn']
        
        self.egg_xborder_length = self.config['egg_use_percent'] / 100 * self.config['egg_length']
        self.egg_xborder_steps = round(self.egg_xborder_length * self.x_velocity)
        
        self.simulator_pos = (0 + 0j)
        self.simulator_speed = self.config['simulator_start_speed']
        
        self.ispenup = False
        
        self.current_color = self.config['start_color']
        self.print_piority = 2
                
        self.log('Simulator __init__ with config: ', 10)
        
    def init_canvas(self):
        self.canvas = eastercanvas.EasterCanvas(
            self.config,
            self.canvas_close
        )
    
    def canvas_close(self):
        self.pendown()
        self.cleanup()
        print('canvas close!')
        
    def using_canvas(self):
        try:
            self.canvas
            return True
        except AttributeError:
            return False
            
    def adjust_loop(self):
        time.sleep(self.config['max_stepper_speed'])
        penup = not keyboard.is_pressed(self.upkey)
        self.escape = keyboard.is_pressed(self.escapekey)
        self.set_pen_up(penup)
        
    def set_status_state(self, state): pass
        
    def run_egg(self):
        self.xkeys = ('d', 'a')
        self.ykeys = ('r', 'f')
        self.zkeys = ('s', 'w')
        self.upkey = 'u'
        self.escapekey = 'enter'
    
        adjust_text = f'''
    ________________________________
    | Drucke "{self.config["name"]}"... |
      ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    Bitte richte den Roboterarm richtig aus, indem du folgende Tasten drückst.  
    <{self.xkeys[0].upper()}> Arm nach rechts     <{self.xkeys[1].upper()}> Arm nach links, 
    <{self.zkeys[0].upper()}> Stifte ausfahren,   <{self.zkeys[1].upper()}> Stifte einfahren,   
    <{self.ykeys[0].upper()}> Ei vorwärts drehen, <{self.ykeys[1].upper()}> Ei rückwers drehen, 
    <{self.upkey.upper()}> Stift heruterlassen, 
    <{self.escapekey.upper()}> Mit dem Drucken beginnen.    
        '''
        print('info text')
        self.canvas.info_text(adjust_text)
        self.canvas.window.update()
        
        self.set_status_state(0)
        self.escape = self.direct_run
        while not self.escape: self.adjust_loop()
        
        self.canvas.paint_all()
        
        self.set_status_state(1)
        self.act(self)
        self.set_status_state(2)
        
        finish_text = f'''
    | FERTIG! |
     ‾‾‾‾‾‾‾‾‾‾
    Das Ei "{self.config["name"]}" wurde fertiggestellt.\n    
    Du kannst es nun vorsichtig aus der Halterung nehmen.
    Zum Beenden bitte <Ctrl+E> drücken.
        '''
        print('finish')
        if not self.direct_run: self.canvas.info_text(finish_text)
        
    def run(self, **kwargs):
        self.act = kwargs.get('act', None)
        self.direct_run = kwargs.get('direct_run', False)
        gui = kwargs.get('gui', True)
        console = kwargs.get('console', True)
        
        if gui:
            self.init_canvas()
            if self.act != None:
                self.act_thread = threading.Thread(target=self.run_egg)
                self.act_thread.start()
        
        if console: self.console_debug()
        
        if self.using_canvas(): self.canvas.main_loop()
        else: self.console_debug_thread.join()
        
    def console_debug(self, **kwargs):
        self.console_debug_thread = threading.Thread(target=self.console_debug_thread)
        self.console_debug_thread.start()
        if kwargs.get('wait', False) == True: self.console_debug_thread.join()
        
    def log(self, obj, *args):
        prio = em.get_save(args, 0, 0) 
        if prio >= self.print_piority: print(f'EasterSimulator: {obj}')
        
    def pos_to_string(self):
        dp = 1
        xsteps = round(self.x_pos())
        ysteps = round(self.y_pos())
        xdistance = round(self.x_pos() / self.x_velocity, dp)
        xpercent = round(self.x_percent() * 100, dp)
        ypercent = round(self.y_percent() * 100, dp)
        return f"({xpercent: 5.1f}% | {ypercent: 5.1f}%)_({xdistance: 5.1f}mm|    ?mm)_({xsteps: 5}x | {ysteps: 5}x)"
        
    def log_pos(self): self.log(self.pos_to_string(), 10)
    
    def xy_pos(self): return self.simulator_pos
    def x_pos(self): return self.xy_pos().real
    def y_pos(self): return self.xy_pos().imag

    def way_to_xsteps(self, way: float): return self.x_velocity * way
    def way_to_ysteps(self, way: float): return self.y_velocity * way * 1j
    
    def get_simulator_speed(self): return self.simulator_speed
    
    def x_percent(self): return self.x_pos() / self.egg_xborder_steps
    def y_percent(self): return self.y_pos() / self.egg_y_steps

    def x_to_ysteps(self, xsteps: complex):
        return xsteps.real * self.y_velocity / self.x_velocity * 1j
    
    def y_to_xsteps(self, ysteps: complex): 
        return ysteps.imag * self.x_velocity / self.y_velocity
    
    def y_caliber(self):
        xpercent = self.x_pos() / self.egg_x_steps
        return em.egg_caliber(xpercent, self.config['egg_height'])
    
    def delta_steps(self, new_pos: complex, **kwargs):
        ysteps1 = new_pos.imag - self.y_pos()
        ysteps2 = ysteps1 + (-self.egg_y_steps if ysteps1 > 0 else self.egg_y_steps)
        
        yminmax = em.abs_minmax(ysteps1, ysteps2)
        yindex = 1 if kwargs.get('long', False) == True else 0
        
        xsteps = round(new_pos.real - self.x_pos())
        ysteps = round(yminmax[yindex])
    
        return xsteps + ysteps * 1j
        
    def step_to(self, ppos: complex, **kwargs):
        move = kwargs.get('move', False)
        color = kwargs.get('color', None)
        new_pos = ppos + self.xy_pos() if kwargs.get('rel', False) else ppos
        delta_steps = self.delta_steps(new_pos, long=kwargs.get('long', False))

        #print(f'step_to new_pos {new_pos}')
                
        self.simulator_pos = new_pos
                
        if abs(delta_steps) > 0:
            if self.using_canvas():
                canvas_pos = (delta_steps.real / self.egg_xborder_steps + delta_steps.imag / self.egg_y_steps * 1j)
                #print(f'step_to canvas {canvas_pos}')
                self.canvas.go_to(
                    canvas_pos,
                    move,
                    self.canvas_info_pos(),
                    kwargs.get('info', False)
                )
                
                speed = self.get_simulator_speed()
                if not move and speed > 0:
                    length = abs(delta_steps)
                    sleep = length / 1000 * speed
                    time.sleep(sleep)
                    
                if color != None: self.change_color(color, stayup=move)
                    
            return delta_steps
        else: return None
        
        
    def go_to(self, pos: complex, **kwargs):
        if pos.real < -50 or pos.real > 50: raise Exception(f'the x-pos ({pos.real}) has to be between -50% and 50%')
        
        #print(f'go_to pos {pos}')
        
        new_pos = em.round_complex(
            pos.real / 100 * self.egg_xborder_steps
            + round(em.modulo(pos.imag, 100) / 100 * self.egg_y_steps) * 1j
        )
        
        #print(f'go_to new_pos {new_pos}')
        
        self.step_to(new_pos, **kwargs)
        
    def go_home(self):
        self.change_color(self.config['start_color'], stay_up=True)
        self.go_to(0, move=True, stay_up=True)
        
    def step_to_multiple(poses, **kwargs):
        for pos in poses: self.step_to(pos, **kwargs)
        
    def set_pen_up(self, up: bool):
        if up != self.ispenup:
            self.ispenup = up
            time.sleep(self.get_simulator_speed() * 4)
            if self.using_canvas(): self.canvas.set_pen_up(up)
            
            return True
            
        else: return False
        
    def penup(self):   self.set_pen_up(True)
    def pendown(self): self.set_pen_up(False)
    
    def xy_stroke_steps(self): return self.x_stroke_steps + self.y_stroke_steps
        
    def change_color(self, color: str, **kwargs):
        new_pos = self.config['color_pos'].get(color, None)
        if new_pos != None:
            self.log(f"Changing color to {color}...", 0)
            if self.using_canvas(): self.canvas.set_color(color)
            
        return new_pos        
        
    def update_canvas_info(self, info: dict):
        if self.using_canvas(): self.canvas.update_info(info)
        
    def canvas_info_pos(self):
        string_pos = self.pos_to_string().split('_')
        return {
            'p1': string_pos[0],
            'p2': string_pos[1],
            'p3': string_pos[2]
        }
        
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
            
            self.step_to(new_xpos, new_ypos, move=(r == 0))
            
        if kwargs.get('fill', False):
            sub_steps_x = kwargs.get('sub_steps_x', self.x_stroke_steps) # getting pen stroke smaller
            sub_steps_y = kwargs.get('sub_steps_y', self.y_stroke_steps) # getting pen stroke smaller
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
        
        old_pos = self.xy_pos()
        seg_length = round(kwargs.get('length', self.egg_y_steps) / seg_number)
        
        for i in range(res * seg_number):
            xpos = (math.sin(i / res * math.pi * 2) * width + (i / res * seg_length) * 1j) + old_pos
            new_pos = xpos
            self.step_to(new_pos)
        
    def on_console_input(self, typ: str, split: list):
        print(f'simulator typ {typ}')
        
        if typ == 'penup': self.penup()
        elif typ == 'pendown': self.pendown()
        elif typ == 'pentoggle': self.set_pen_up(not self.ispenup)
        
        elif typ == 'color': self.change_color(split[1])
        elif typ == 'hidecolor':
            self.current_color = split[1]
            if self.using_canvas(): self.canvas.set_color(None if self.ispenup else self.current_color)
        
        elif typ == 'sin': self.sin_wave(200, self.egg_y_steps, 5, 50)
            
        elif typ == 'lineto' or typ == 'moveto':
            pos = complex(split[1])
            
            lw = em.get_save(split, 3, 'False') == 'True'
            
            if typ == 'lineto': self.go_to(pos, long=lw, info=True)
            if typ == 'moveto': self.go_to(pos, move=True, info=True)
            
            self.log(f'{typ} => {self.pos_to_string()}', 10)
            
        elif typ == 'grid':
            for x in range(-50, 50, 10):
                print(f'x = {x}%: y = ', end='')
                for y in range(10, 100, 10):
                    print(f'{y}% ', end='')
                    self.go_to((x + y * 1j), move=True)
                    
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
                inp = input('?: ')
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
