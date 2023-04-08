import keyboard
import json
import traceback
import math
import time
import eastermath as em
import sys
import default 
import threading

class EasterSimulator:
    def __init__(self, config: dict):
        self.config = dict(default.defaultEasterControlerConfig)
        self.config.update(config)
        self.initialize()
        
    def log_name(self): return 'EasterSimulator'
    
    def initialize(self):
        self.x_velocity = self.config['xstepper']['steps_per_millimeter']
        self.y_velocity = self.config['ystepper']['steps_of_turn'] / (math.pi * self.config['egg_height'])

        self.x_stroke_steps = self.x_velocity * self.config['pen_stroke_width']
        self.y_stroke_steps =  self.x_to_ysteps(self.x_stroke_steps) #TODO!
        
        self.egg_x_steps = round(self.config['egg_length'] * self.x_velocity)
        self.egg_y_steps = self.config['ystepper']['steps_of_turn']
        
        self.egg_xborder_length = self.config['egg_use_percent'] / 100 * self.config['egg_length']
        self.egg_xborder_steps = round(self.egg_xborder_length * self.x_velocity)
        
        self.simulator_pos = 0
        self.simulator_speed = self.config['simulator_start_speed']
                
        self.current_color = self.config['start_color']
        self.ispenup = False

        self.time_counter = 0

        self.print_piority = 2
        
        self.pause_event = threading.Event()
        self.start_act_event = threading.Event()
        self.exit_event = threading.Event()
        self.repeat_act_event = threading.Event()
        self.count_event = threading.Event()

        self.status_states = []

        self.xkeys = ('d', 'a')
        self.ykeys = ('r', 'f')
        self.zkeys = ('s', 'w')
        self.upkey = 'u'
        self.runkey = 'enter'
        self.pausekey = 'p'

        headline = f'| Drucke "{self.config["name"]}"...  |'
        self.adjust_text = f'''{'_'*len(headline)}
{headline}
{'‾'*len(headline)}
Bitte richte den Roboterarm richtig aus, indem du folgende Tasten drückst.
<{self.xkeys[0].upper()}> Arm nach rechts     <{self.xkeys[1].upper()}> Arm nach links,
<{self.zkeys[0].upper()}> Stifte ausfahren,   <{self.zkeys[1].upper()}> Stifte einfahren,
<{self.ykeys[0].upper()}> Ei vorwärts drehen, <{self.ykeys[1].upper()}> Ei rückwärs drehen,
<{self.upkey.upper()}> Stift heruterlassen,
<{self.pausekey.upper()}> Druck pausieren, 
<{self.runkey.upper()}> Mit dem Drucken beginnen.'''
        self.finish_text = f'''| FERTIG! |
{'‾'*11}
Das Ei "{self.config["name"]}" wurde fertiggestellt.\n    
Du kannst es nun vorsichtig aus der Halterung nehmen.
Zum Neudrucken <Ctrl+R>, Zum Beenden bitte <Ctrl+E> drücken.'''
                
        self.log('Simulator __init__ with config: ', 10)

    def escape(self): pass

    def set_status_state(self, state: int, **_):
        if state < 3: self.right_status = state
        if state == 0: self.time_counter = 0
        if state == 1: self.count_event.set()
        if state == 2: self.count_event.clear()
    
    def set_pause(self, pause: bool):
        if self.pause_event.is_set() != pause:
            if pause: self.pause_event.set()
            else:     self.pause_event.clear()
            self.set_status_state(3 if pause else self.right_status, pause=True)
            
    def adjust_loop(self):
        run_pressed = keyboard.is_pressed(self.runkey)
        if not self.start_act_event.is_set() and run_pressed:
            self.start_act_event.set()
        
        if not self.start_act_event.is_set():
            penup = not keyboard.is_pressed(self.upkey)
            self.set_pen_up(penup)
        
        pause = keyboard.is_pressed(self.pausekey)
        if self.right_status == 1 and pause and not self.pause_pressed:
            self.set_pause(not self.pause_event.is_set())

        self.pause_pressed = pause

    def run_adjust_thread(self):
        self.pause_pressed = False
        while not self.exit_event.is_set():
            time.sleep(self.config['max_stepper_speed'])
            self.adjust_loop()
        
    def update_time(self, _: int): pass

    def run_time_thread(self):
        while not self.exit_event.is_set():
            time.sleep(1)
            if self.count_event.is_set() and not self.pause_event.is_set():
                self.time_counter += 1
                self.update_time(self.time_counter)
    
    def run_act_thread(self):
        while not self.exit_event.is_set():
            if not self.direct_run:
                self.set_status_state(0)
            self.time_counter = 0
            self.update_time(self.time_counter)

            if self.direct_run:
                self.start_act_event.set()

            while not self.start_act_event.is_set():
                time.sleep(self.config['max_stepper_speed'])
            
            self.set_status_state(1)
            self.act(self)
            self.go_home()
            self.set_status_state(2)

            while not self.repeat_act_event.is_set():
                time.sleep(self.config['max_stepper_speed'])

            self.repeat_act_event.clear()
            self.start_act_event.clear()

    def main_loop(self):
        try: 
            self.console_debug_thread.join()
            self.act_thread.join()
        except AttributeError: pass

    def run(self, **kwargs):
        self.act = kwargs.get('act', None)
        self.direct_run = kwargs.get('direct_run', False)
        console = kwargs.get('console', True)
        
        if console:
            self.console_debug_thread = threading.Thread(target=self.console_debug_thread)
            self.console_debug_thread.start()

        self.count_thread = threading.Thread(target=self.run_time_thread)
        self.count_thread.start()

        if self.act != None:
            self.act_thread = threading.Thread(target=self.run_act_thread)
            self.act_thread.start()

            self.adjust_thread = threading.Thread(target=self.run_adjust_thread)
            self.adjust_thread.start()

        self.main_loop()
        
    def log(self, obj, *args):
        prio = em.get_save(args, 0, 0) 
        color = em.get_save(args, 1, em.Colors.LIGHT_CYAN) 
        if prio >= self.print_piority:
            print(f'{color}{self.log_name()}: {obj}{em.Colors.END}')
        
    def pos_to_string(self, *args):
        dp = 1
        pos = em.get_save(args, 0, self.xy_pos())
        xsteps = int(pos.real)
        ysteps = int(pos.imag)
        xdistance = round(pos.real / self.x_velocity, dp)
        xpercent = round(pos.real / self.egg_xborder_steps * 100, dp)
        ypercent = round(em.modulo(pos.imag / self.egg_y_steps * 100, 100), dp)
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
    
    def adjust_steppers(self, _: complex): pass
    def execute_steps_to(self, _: complex, **kwargs): pass
        
    def step_to(self, ppos: complex, **kwargs):
        while self.pause_event.is_set():
            time.sleep(self.config['max_stepper_speed'])
        
        move = kwargs.get('move', False)
        color = kwargs.get('color', None)
        stayup = kwargs.get('stayup', False)
        rel = kwargs.get('rel', False)
        long = kwargs.get('long', False)

        new_pos = ppos + (self.xy_pos() if rel else 0)
        delta_steps = self.delta_steps(new_pos, long=long)
                
        if abs(delta_steps) > 0:
            self.set_pen_up(move)

            self.adjust_steppers(delta_steps)
            if color != None: self.change_color(color, stayup = move)
            
            speed = self.get_simulator_speed()
            if not move and speed > 0:
                length = abs(delta_steps)
                sleep = length / 1000 * speed
                time.sleep(sleep)

            self.execute_steps_to(delta_steps, **kwargs)
            self.simulator_pos = new_pos
            
            if move and not stayup: self.pendown()
                    
            return delta_steps        
        
    def go_to(self, pos: complex, **kwargs):
        if pos.real < -50 or pos.real > 50: raise Exception(f'the x-pos ({pos.real}) has to be between -50% and 50%')
                
        new_pos = em.round_complex(
            pos.real / 100 * self.egg_xborder_steps
            + round(em.modulo(pos.imag, 100) / 100 * self.egg_y_steps) * 1j
        )        
        self.step_to(new_pos, **kwargs)
        
    def go_home(self):
        print('go home')
        self.step_to(
            0, move=True, info=True,
            color=self.config['start_color'], stayup=True
        )
        
    def step_to_multiple(self, poses, **kwargs):
        for pos in poses: self.step_to(pos, **kwargs)
        
    def set_pen_up(self, up: bool):
        changed = up != self.ispenup
        self.ispenup = up
        return changed
        
    def penup(self):   self.set_pen_up(True)
    def pendown(self): self.set_pen_up(False)
    
    def xy_stroke_steps(self): return self.x_stroke_steps + self.y_stroke_steps
        
    def update_color(self, cp, np): pass
    
    def change_color(self, color: str, **kwargs):
        while self.pause_event.is_set():
            time.sleep(self.config['max_stepper_speed'])
        
        new_pos = self.config['color_pos'].get(color, None)
        stayup = kwargs.get('stayup', False)
        if new_pos != None:
            current_pos = self.config['color_pos'][self.current_color]
            self.current_color = color
            if current_pos != new_pos:
                self.penup()
                self.update_color(current_pos, new_pos)
                if not stayup: self.pendown()

        return new_pos
    
    def hide_color(self, color: str):
        self.current_color = color
        
    def on_console_input(self, typ: str, split: list):
        print(f'simulator typ {typ}')
        
        if typ == 'penup': self.penup()
        elif typ == 'pendown': self.pendown()
        
        elif typ == 'pentoggle': self.set_pen_up(not self.ispenup)
        
        elif typ == 'color':
            stayup = int(em.get_save(split, 2, 0)) == 1
            print(stayup)
            self.change_color(split[1], stayup=stayup)
            
        elif typ == 'hidecolor':
            self.hide_color(split[1])
                    
        elif typ == 'lineto' or typ == 'moveto':
            pos = complex(split[1])
            
            lw = em.get_save(split, 2, 0) == '1'
            color = em.get_save(split, 3, self.current_color)
            stayup = em.get_save(split, 4, 0) == '1'
            
            #print(f'long = {lw}')
            
            if typ == 'lineto': self.go_to(pos, long=lw, color=color, info=True)
            if typ == 'moveto': self.go_to(pos, move=True, color=color, stayup=stayup, info=True)
            
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
            
        else: return False
            
    def console_debug_thread(self):
        commands = []
                
        while not self.exit_event.is_set():
            if len(commands) == 0:
                inp = input(f'{em.Colors.RED}?: {em.Colors.END}')
                commands = inp.split('|')
            
            split = commands.pop(0).split(';')
            typ = split[0]
            
            try:
                if typ == 'ex': self.escape()
                elif self.on_console_input(typ, split) == False:
                    raise Exception(f'Unbekannter typ "{typ}".', 10)
            
            except:
                self.log(f'ERROR:', 10)
                traceback.print_exc()

''''
controller = EasterSimulator({})
controller.console_debug()
controller.gui_debug()
'''
