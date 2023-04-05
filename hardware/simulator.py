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
                
        self.current_color = self.config['start_color']
        self.print_piority = 2
        
        self.pause_event = threading.Event()
        self.ispenup = False
                
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
        run_pressed = keyboard.is_pressed(self.runkey)
        if not self.script_thread_started.is_set() and (run_pressed or self.direct_run):
            self.script_thread.start()
            self.script_thread_started.set()
        
        penup = not keyboard.is_pressed(self.upkey)
        self.set_pen_up(penup)
        
        pause = keyboard.is_pressed(self.pausekey)
        if pause and not self.pause_pressed: self.set_pause(not self.pause_event.is_set())
        self.pause_pressed = pause
        
        time.sleep(self.config['max_stepper_speed'])
        
    def set_status_state(self, state: int):
        if state < 3: self.status_state = state
        infotext = 'ADJUSTING' if state == 0 else ('RUNNING' if state == 1 else ('FINISHED' if state == 2 else 'PAUSED'))
        self.update_canvas_info({
            'state': f'State = {infotext}'
        })
    
    def set_pause(self, pause: bool):
        if self.pause_event.is_set() != pause:
            if pause: self.pause_event.set()
            else:     self.pause_event.clear()
            self.set_status_state(3 if pause else self.status_state)
        
    def run_egg(self):
        self.xkeys = ('d', 'a')
        self.ykeys = ('r', 'f')
        self.zkeys = ('s', 'w')
        self.upkey = 'u'
        self.runkey = 'enter'
        self.pausekey = 'p'
    
        adjust_text = f'''
    ________________________________
    | Drucke "{self.config["name"]}"... |
      ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    Bitte richte den Roboterarm richtig aus, indem du folgende Tasten drückst.  
    <{self.xkeys[0].upper()}> Arm nach rechts     <{self.xkeys[1].upper()}> Arm nach links, 
    <{self.zkeys[0].upper()}> Stifte ausfahren,   <{self.zkeys[1].upper()}> Stifte einfahren,   
    <{self.ykeys[0].upper()}> Ei vorwärts drehen, <{self.ykeys[1].upper()}> Ei rückwers drehen, 
    <{self.upkey.upper()}> Stift heruterlassen,
    <{self.pausekey.upper()}> Druck pausieren, 
    <{self.runkey.upper()}> Mit dem Drucken beginnen.    
        '''

        self.canvas.info_text(adjust_text)
        self.canvas.window.update()
        
        self.set_status_state(0)
        self.escape = False
        self.pause_pressed = False
        self.script_thread = threading.Thread(target=self.run_act_script)
        self.script_thread_started = threading.Event()
        
        print('adjust loop start')
        
        while not self.escape:
            self.adjust_loop()
        
    def run_act_script(self):
        self.canvas.paint_all()
        
        self.set_status_state(1)
        
        self.act(self)
        self.go_home()
        
        self.set_status_state(2)
        
        finish_text = f'''
    | FERTIG! |
     ‾‾‾‾‾‾‾‾‾‾
    Das Ei "{self.config["name"]}" wurde fertiggestellt.\n    
    Du kannst es nun vorsichtig aus der Halterung nehmen.
    Zum Beenden bitte <Ctrl+E> drücken.
        '''
        
        if self.using_canvas() and not self.direct_run:
            self.canvas.info_text(finish_text)
            
        print('!finished!')
        
    def run(self, **kwargs):
        self.act = kwargs.get('act', None)
        self.direct_run = kwargs.get('direct_run', False)
        gui = kwargs.get('gui', True)
        console = kwargs.get('console', True)
        
        if gui:
            self.init_canvas()
            print('start_act')
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
        color = em.get_save(args, 1, em.Colors.LIGHT_CYAN) 
        if prio >= self.print_piority: print(f'{color}EasterSimulator: {obj}{em.Colors.END}')
        
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
    
    def adjust_steppers(self, delta_steps): pass
    def stepper_step_to(self, xsteps: int, ysteps: int): pass
        
    def step_to(self, ppos: complex, **kwargs):
        while self.pause_event.is_set(): time.sleep(0.001)
        
        move = kwargs.get('move', False)
        color = kwargs.get('color', None)
        stayup = kwargs.get('stayup', False)
        info = kwargs.get('info', False)
        
        new_pos = ppos + self.xy_pos() if kwargs.get('rel', False) else ppos
        delta_steps = self.delta_steps(new_pos, long=kwargs.get('long', False))
                
        if abs(delta_steps) > 0:
            if move: self.penup()
            
            self.adjust_steppers(delta_steps)
            
            self.simulator_pos = new_pos
            
            if self.using_canvas():
                if info: self.update_canvas_info(self.canvas_info_pos())
                
                canvas_delta = (delta_steps.real / self.egg_xborder_steps + delta_steps.imag / self.egg_y_steps * 1j)
                self.canvas.cursor_to(canvas_delta, self.ispenup, self.canvas_info_pos(), info)
                
                speed = self.get_simulator_speed()
                if not move and speed > 0:
                    length = abs(delta_steps)
                    sleep = length / 1000 * speed
                    time.sleep(sleep)
                
            if color != None: self.change_color(color, stayup = move)
            
            self.stepper_step_to(delta_steps.real, delta_steps.imag)
            
            if move and not stayup:
                self.pendown()
                    
            return delta_steps        
        
    def go_to(self, pos: complex, **kwargs):
        if pos.real < -50 or pos.real > 50: raise Exception(f'the x-pos ({pos.real}) has to be between -50% and 50%')
                
        new_pos = em.round_complex(
            pos.real / 100 * self.egg_xborder_steps
            + round(em.modulo(pos.imag, 100) / 100 * self.egg_y_steps) * 1j
        )        
        self.step_to(new_pos, **kwargs)
        
    def go_home(self):
        self.go_to(0, move=True, color=self.config['start_color'], stayup=True)
        
    def step_to_multiple(poses, **kwargs):
        for pos in poses: self.step_to(pos, **kwargs)
        
    def set_pen_up(self, up: bool):
        if up != self.ispenup:            
            self.ispenup = up
            if self.using_canvas(): self.canvas.set_pen_up(up)
            
            time.sleep(self.get_simulator_speed() * 4)
            return True
            
        else: return False
        
    def penup(self):   self.set_pen_up(True)
    def pendown(self): self.set_pen_up(False)
    
    def xy_stroke_steps(self): return self.x_stroke_steps + self.y_stroke_steps
        
    def update_color(self, cp, np):
        self.log(f'Updating color from {cp} to {np} → {np - cp}')
        if self.using_canvas(): self.canvas.set_color(self.current_color)
    
    def change_color(self, color: str, **kwargs):
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
        
    def update_canvas_info(self, info: dict):
        if self.using_canvas(): self.canvas.update_info(info)
        
    def canvas_info_pos(self):
        string_pos = self.pos_to_string().split('_')
        return {
            'p1': string_pos[0],
            'p2': string_pos[1],
            'p3': string_pos[2]
        }
        
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
            self.current_color = split[1]
            if self.using_canvas(): self.canvas.set_color(None if self.ispenup else self.current_color)
                    
        elif typ == 'lineto' or typ == 'moveto':
            pos = complex(split[1])
            
            lw = em.get_save(split, 2, 0) == 1
            color = em.get_save(split, 3, self.current_color)
            stayup = em.get_save(split, 4, 0) == 1
            
            print(stayup)
            
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
        
    def cleanup(self):
        self.set_pause(False)
            
    def console_debug_thread(self):
        escape = False
        commands = []
                
        while not escape:
            if len(commands) == 0:
                inp = input(f'{em.Colors.RED}?: {em.Colors.END}')
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
