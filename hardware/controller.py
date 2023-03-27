import keyboard
import json
import traceback
import math
import time
import RPi.GPIO as GPIO
import stepper
import servo
import threading
import eastermath as em
import sys
import default
import simulator

class EasterControler(simulator.EasterSimulator):
    def __init__(self, config: dict):
        super().__init__(config)
        
        self.pen_servo_offset = 0
        self.current_direction = 0
        
        self.setup()
        
    def setup(self):
        self.log('Easter Controller setup...', 10)
         
        GPIO.setmode( GPIO.BCM )

        self.ystepper = stepper.EasterStepper(self.config['ystepper'])
        self.xstepper = stepper.EasterStepper(self.config['xstepper'])
        self.zstepper = stepper.EasterStepper(self.config['zstepper'])
        
        self.servo = servo.EasterServo(self.config['servo'])
        
    def stepper(self, name: str):
        stepper = None
        if name == 'xstepper': stepper = self.xstepper
        if name == 'ystepper': stepper = self.ystepper
        if name == 'zstepper': stepper = self.zstepper
        return stepper
        
    def x_pos(self): return self.xstepper.pos()
    def y_pos(self): return self.ystepper.modulo_pos()
        
    def x_percent(self): return (self.x_pos() / self.egg_border_steps) * 100
    def y_percent(self): return (self.y_pos() / self.ystepper.steps_of_turn()) * 100
    
    def get_simulator_speed(self): return 0 # ignore simulator_speed
    
    def gui_start_act(self):
        try: self.canvas.info_text('Please locate the robot arm by pressing W, S, A and D. Finally press CTRL + O.')
        except AttributeError: pass
        
        escape = False
        while not escape:
            time.sleep(self.config['max_stepper_speed'])
            zdirection = -1 if keyboard.is_pressed('w') else (1 if keyboard.is_pressed('s') else 0)
            xdirection = -1 if keyboard.is_pressed('a') else (1 if keyboard.is_pressed('d') else 0)
            ydirection = -1 if keyboard.is_pressed('r') else (1 if keyboard.is_pressed('f') else 0)
            penup = keyboard.is_pressed('u')
            
            escape = keyboard.is_pressed('enter')
            #print(f'zdirection={zdirection} and xdirection={xdirection} and escape={escape}')
            
            self.set_pen_up(penup)
            self.zstepper.step(orientation=zdirection, count=False)
            self.xstepper.step(orientation=xdirection, count=False)
            self.ystepper.step(orientation=ydirection, count=False)
            
        try: self.canvas.info_text(None)
        except AttributeError: pass
        
        super().gui_start_act()
        
    def steps_to(self, xsteps: int, ysteps: int):        
        if xsteps != 0 or ysteps != 0:
            steps_minmax   = em.abs_minmax(xsteps, ysteps)
            isx_max        = steps_minmax[1] == xsteps
            stepper_minmax = (
                self.ystepper if isx_max else self.xstepper,
                self.xstepper if isx_max else self.ystepper
            )
            
            max_sleep = self.config['max_stepper_speed']
            duration = (abs(steps_minmax[1]) - 1) * max_sleep
            min_sleep = duration / (abs(steps_minmax[0]) - 1) if abs(steps_minmax[0]) > 1 else -1
            
            sleep_minmax = (min_sleep, max_sleep)
            
            self.log(f'steps_to:\nsteps_minmax:{steps_minmax}\nstepper_minmax:{stepper_minmax}\nsleep_minmax:{sleep_minmax}\n______')
            
            stepper_minmax[1].setSpeed(sleep_minmax[1])
            stepper_minmax[0].setSpeed(sleep_minmax[0])
            
            thread =                     stepper_minmax[1].turn(steps=steps_minmax[1], thread=True)
            if abs(steps_minmax[0]) > 0: stepper_minmax[0].turn(steps=steps_minmax[0], thread=False)
            
            thread.join()
        
    def go_to(self, xunit: float, yunit: float, **kwargs):
        move = kwargs.get('move', False)
        info = kwargs.get('info', False)
    
        new_kwargs = dict(kwargs)
        new_kwargs.update({'info':False})
        (xsteps, ysteps) = super().go_to(xunit, yunit, **new_kwargs)
        
        if xsteps != 0 or ysteps != 0: 
            if move:
                self.penup()
                self.current_direction = 0
            
            new_direction = em.direction(xsteps)
            
            if self.current_direction != new_direction and not move:
                time.sleep(self.config['pen_lazy_sleep'])
                
                adjustment_steps = self.config['pen_lazy'] * (new_direction - self.current_direction)
                self.log(f'adjustment_steps={adjustment_steps}', 10)
                
                self.xstepper.setSpeed(self.config['max_stepper_speed'])
                self.xstepper.turn(steps=adjustment_steps, count=False)
                
                self.current_direction = new_direction
                
                time.sleep(self.config['pen_lazy_sleep'])
            
            self.log(f'line to steps: {xsteps}:{ysteps}')
            self.steps_to(xsteps, ysteps)
            
            if move: self.pendown()
            if info: self.update_canvas_info(self.canvas_info_pos())
    
    def set_pen_up(self, up: bool):
        if super().set_pen_up(up):
            newPos = self.config['penup_pos'] if up else self.config['pendown_pos']
            
            self.log(f'penup pos: {newPos}')
            
            time.sleep(self.config.get('penup_sleep', 0))
            self.servo.setPos(newPos)
            time.sleep(self.config.get('penup_sleep', 0))
        
    def change_color(self, color: str):
        current_pos = self.config['color_pos'][self.current_color]
        new_pos     = self.config['color_pos'][color]
        
        if current_pos != new_pos:
            self.penup()
            
            steps = (new_pos - current_pos) * self.config['change_color_steps']
            self.log(f"steps: {steps}x")
            self.zstepper.turn(steps=steps)
            
            self.pendown()
            
        super().change_color(color)
    
    def cleanup(self):
        self.log('cleanup', 10)
        
        self.ystepper.setPinsLow()
        self.xstepper.setPinsLow()
        self.zstepper.setPinsLow()
        self.servo.stopPWM()
        
        GPIO.cleanup()
        
    def on_console_input(self, typ: str, split: list):
        print(f'coltroler typ {typ}')
        
        if typ == 'servo':
            pos = float(split[1])
            print(self.servo.setPos(pos))
        
        elif 'stepper' in typ:
            stepper = self.stepper(typ)
            turn = int(split[1])
            count = split[2] == 'True'
            
            self.log(f'{stepper} turns {turn} count {count}', 5)
            stepper.turn(steps=int(turn), count=count)
            self.log(f'pos: {stepper.pos()}', 5)
            
        else: return super().on_console_input(typ, split)
