import keyboard
import time
import RPi.GPIO as GPIO
import stepper
import servo
import eastermath as em
import eastercanvas
import leds

class EasterControler(eastercanvas.EasterCanvas):
    def __init__(self, config: dict):
        super().__init__(config)
        
    def setup(self):
        self.log('Easter Controller setup...', 10)
         
        GPIO.setmode( GPIO.BCM )

        self.xstepper = stepper.EasterStepper(self.config['xstepper'])
        self.ystepper = stepper.EasterStepper(self.config['ystepper'])
        self.zstepper = stepper.EasterStepper(self.config['zstepper'])
        
        self.servo = servo.EasterServo(self.config['servo'])
        self.leds = leds.EasterLEDs(self.config)
        
        self.xstepper.setup_pins()
        self.ystepper.setup_pins()
        self.zstepper.setup_pins()
        self.servo.setup_pins()
        self.leds.setup_pins()
        
    def log_name(self): return 'EasterControler'

    def initialize(self):
        super().initialize()
        self.pen_servo_offset = 0
        self.setup()
        
    def stepper(self, name: str):
        stepper = None
        if name == 'xstepper': stepper = self.xstepper
        if name == 'ystepper': stepper = self.ystepper
        if name == 'zstepper': stepper = self.zstepper
        return stepper
        
    def x_pos(self): return self.xstepper.pos()
    def y_pos(self): return self.ystepper.modulo_pos()
        
    def x_percent(self): return (self.x_pos() / self.egg_xborder_steps) * 100
    def y_percent(self): return (self.y_pos() / self.ystepper.steps_of_turn()) * 100
    
    def get_simulator_speed(self): return 0 # ignore simulator_speed

    def adjust_loop(self):
        super().adjust_loop()
    
        xdirection = -1 if keyboard.is_pressed(self.xkeys[0]) else (1 if keyboard.is_pressed(self.xkeys[1]) else 0)
        ydirection = -1 if keyboard.is_pressed(self.ykeys[0]) else (1 if keyboard.is_pressed(self.ykeys[1]) else 0)
        zdirection = -1 if keyboard.is_pressed(self.zkeys[0]) else (1 if keyboard.is_pressed(self.zkeys[1]) else 0)
                
        self.zstepper.step(direction=zdirection, count=False)
        self.xstepper.step(direction=xdirection, count=False)
        self.ystepper.step(direction=ydirection, count=False)
        
    def execute_steps_to(self, deltapos: complex, **kwargs):
        super().execute_steps_to(deltapos)
        xsteps = deltapos.real
        ysteps = deltapos.imag
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
            
            stepper_minmax[1].set_speed(sleep_minmax[1])
            stepper_minmax[0].set_speed(sleep_minmax[0])
            
            thread =                     stepper_minmax[1].turn(steps=steps_minmax[1], thread=True)
            if abs(steps_minmax[0]) > 0: stepper_minmax[0].turn(steps=steps_minmax[0], thread=False)
            
            thread.join()
            
    def adjust_steppers(self, delta_steps: complex):
        xthread = None
        if not self.ispenup: xthread = self.xstepper.adjust_lazy(delta_steps.real, self.config['max_stepper_speed'])
        ythread = self.ystepper.adjust_lazy(delta_steps.imag, self.config['max_stepper_speed'])
        
        if xthread != None:
            xthread.join()
            '''self.update_info({
                'x-adj':  f'x adjust = {self.xstepper.adjust_count}',
                'x-last': f'x direc = {self.xstepper.last_direction}'
            })'''
                
            
        if ythread != None:
            ythread.join()
            '''self.update_info({
                'y-adj':  f'y adjust = {self.ystepper.adjust_count}',
                'y-last': f'y direc =  {self.ystepper.last_direction}'
            })'''
    
    def set_pen_up(self, up: bool):
        if super().set_pen_up(up):
            #self.log(f'contr set penup {up}')
            newPos = self.config['penup_pos'] if up else self.config['pendown_pos']
            time.sleep(self.config.get('penup_sleep', 0))
            times = 1 if up and False else self.config['servo_times']
            self.servo.set_pos(newPos, times=times, delay=self.config['servo_delay'])
            time.sleep(self.config.get('penup_sleep', 0))

    def update_color(self, cp, np):
        super().update_color(cp, np)
        steps = (np - cp) * self.config['change_color_steps']
        self.zstepper.adjust_lazy(steps, self.config['max_stepper_speed'])
        self.update_info({
            'y-adj':  f'y adjust = {self.zstepper.adjust_count}',
            'y-last': f'y direc =  {self.zstepper.last_direction}'
        })
        self.zstepper.turn(steps=steps)
        
    def set_status_state(self, state: int, **_):
        super().set_status_state(state)
        self.leds.state = state
    
    def cleanup(self):
        self.log('cleanup', 10)
        
        self.ystepper.set_pins_low()
        self.xstepper.set_pins_low()
        self.zstepper.set_pins_low()
        self.servo.stopPWM()
        self.leds.cleanup()
        
        GPIO.cleanup()

    def escape(self):
        self.pendown()
        self.cleanup()
        super().escape()
        
    def on_console_input(self, typ: str, split: list):        
        if typ == 'servo':
            pos = float(split[1])
            times = int(em.get_save(split, 2, '1'))
            delay = float(em.get_save(split, 3, '0.5'))
            print(self.servo.set_pos(pos, times=times, delay=delay))
        
        elif 'stepper' in typ:
            stepper = self.stepper(typ)
            turn = int(split[1])
            count = split[2] == 'True'
            
            self.log(f'{stepper} turns {turn} count {count}', 5)
            stepper.turn(steps=int(turn), count=count)
            self.log(f'pos: {stepper.pos()}', 5)
            
        else: return super().on_console_input(typ, split)
