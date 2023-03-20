import json
import traceback
import math
import time
import eastermath as em
import sys
import default 

class EasterSimulator:
    def __init__(self, config: dict):
        self.config = dict(default.defaultEasterControlerConfig)
        self.config.update(config)
        
        self.x_velocity = self.config['xstepper']['steps_per_millimeter']
        
        self.simulator_x = 0
        self.simulator_y = 0
        
        self.simulator_width = self.config['egg_length'] * self.x_velocity 
        self.simulator_height = self.config['ystepper']['steps_of_turn']
        
        self.egg_border_length = self.config['egg_use_percent'] / 100 * self.config['egg_length']
        
        self.egg_steps = round(self.config['egg_length'] * self.x_velocity)
        self.egg_border_steps = round(self.egg_border_width * self.x_velocity)
        
        self.current_color = self.config['start_color']
        self.print_piority = 2
        
        self.log('Simulator __init__ with config: ', 10)
        
    def log(self, obj, *args):
        prio = em.get_save(args, 0, 0) 
        if prio >= self.print_piority: print('EasterControler: ' + str(obj))
        
    def x_pos(self): return simulator_x
    def y_pos(self): return simulator_y
    
    def x_percent(self): return self.simulator_x / self.egg_border_steps
    def y_percent(self): return self.simulator_y / self.config['ystepper']['steps_of_turn']
    
    def y_caliber(self):
        xpercent = self.x_pos() / self.egg_steps
        return em.egg_caliber(xpercent, self.config['egg_height'])
    
    def x_delta_steps(self, xunit: float, **kwargs):
        steps = xunit
    
        if not kwargs.get('step', False):
            if xunit < -50 or xunit > 50: raise Exception(f'the x-pos ({xunit}) has to be between -50% and 50%')
            steps = xunit / 100 * self.egg_border_length * self.x_velocity
        
        return steps - self.x_pos()
        
    def y_delta_steps(self, yunit: float, **kwargs):
        steps_of_turn = self.config['ystepper']['steps_of_turn']
        
        newPos = yunit
        
        if not kwargs.get('step', False):
            factor = em.modulo(yunit, 100) / 100
            newPos = round(factor * steps_of_turn)
        
        steps1 = newPos - self.y_pos()
        steps2 = steps1 + (-steps_of_turn if steps1 > 0 else steps_of_turn)
        
        minmax = em.abs_minmax(steps1, steps2)
        index = 1 if kwargs.get('long', False) == True else 0
        
        return minmax[index]
        
    
    def steps_to(self, xsteps: int, ysteps: int):
        pass
        
    def go_to(self, xunit: float, yunit: float, **kwargs):
        move = kwargs.get('move', False)
        step_unit = kwargs.get('step', False)
        
        xsteps = self.x_delta_steps(xunit, step=step_unit)
        ysteps = self.y_delta_steps(yunit, step=step_unit, long=kwargs.get('long', False))
        
        return (xsteps, ysteps)
