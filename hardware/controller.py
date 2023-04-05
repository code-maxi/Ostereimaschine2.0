import keyboard
import time
import RPi.GPIO as GPIO
import stepper
import servo
import eastermath as em
import simulator
import leds

class EasterControler(simulator.EasterSimulator):
    def __init__(self, config: dict):
        super().__init__(config)
        
        self.pen_servo_offset = 0
        
        self.setup()
        
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
        
    def stepper_step_to(self, xsteps: int, ysteps: int):        
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
        
    def step_to(self, ppos: complex, **kwargs):
        move = kwargs.get('move', False)
        info = kwargs.get('info', False)
        stayup = kwargs.get('stayup', False)
    
        new_kwargs = dict(kwargs)
        new_kwargs.update({'info':False})

        delta_steps = super().step_to(ppos, **new_kwargs)
        
        if delta_steps != None:
            xthread = None
            
            if move: self.penup()
            else: xthread = self.xstepper.adjust_lazy(delta_steps.real, self.config['max_stepper_speed'])
            
            ythread = self.ystepper.adjust_lazy(delta_steps.imag, self.config['max_stepper_speed'])
            
            if xthread != None:
                xthread.join()
                if self.using_canvas:
                    self.canvas.update_info({
                        'x-adj':  f'x adjust = {self.xstepper.adjust_count}',
                        'x-last': f'x direc = {self.xstepper.last_direction}'
                    })
                
            if ythread != None:
                ythread.join()
                if self.using_canvas:
                    self.canvas.update_info({
                        'y-adj':  f'y adjust = {self.ystepper.adjust_count}',
                        'y-last': f'y direc =  {self.ystepper.last_direction}'
                    })
                                        
            self.stepper_step_to(delta_steps.real, delta_steps.imag)
            
            if move and not stayup: self.pendown()
            if info: self.update_canvas_info(self.canvas_info_pos())
    
    def set_pen_up(self, up: bool):
        #print(f'try pen up {up}')
        if super().set_pen_up(up):
            print(f'set pen up {up}')
            newPos = self.config['penup_pos'] if up else self.config['pendown_pos']
            self.log(f'penup pos: {newPos}')
            
            time.sleep(self.config.get('penup_sleep', 0))
            self.servo.set_pos(newPos, times=self.config['servo_times'], delay=self.config['servo_delay'])
            time.sleep(self.config.get('penup_sleep', 0))

    def update_color(self, cp, np):
        super().update_color(cp, np)
        steps = (np - cp) * self.config['change_color_steps']
        self.zstepper.turn(steps=steps)

    def change_color(self, color: str, **kwargs):
        new_pos = super().change_color(color)
        #print(new_pos)
        
        if new_pos != None:
            current_pos = self.config['color_pos'][self.current_color]
            #new_pos     = self.config['color_pos'][color]
            #print(current_pos)
            if current_pos != new_pos:
                self.penup()
                
                steps = (new_pos - current_pos) * self.config['change_color_steps']
                self.log(f"steps: {steps}x")
                self.zstepper.turn(steps=steps)
                
                if not stayup: self.pendown()
                
            self.current_color = color
        
    def set_status_state(self, state):
        print('controler set status to ' + str(state))
        self.leds.state = state
    
    def cleanup(self):
        self.log('cleanup', 10)
        
        self.ystepper.set_pins_low()
        self.xstepper.set_pins_low()
        self.zstepper.set_pins_low()
        self.servo.stopPWM()
        self.leds.cleanup()
        
        GPIO.cleanup()
        
    def on_console_input(self, typ: str, split: list):
        print(f'coltroler typ {typ}')
        
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
