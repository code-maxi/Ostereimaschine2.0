import math
import threading
import time
import RPi.GPIO as GPIO
import eastermath as em

step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]
                 
class EasterStepper:
    def __init__(self, config: dict):
        self.config = config
        
        self.motor_step_counter = 0 # position in step_sequence
        self.step_pos = 0 # whole step pos
        
        self.step_sleep = self.config.get('start_step_sleep', 0.003)
        self.ignore_step = False
        
        self.setupPins()
        
    def __str__(self): return self.config['name'] + str(self.config['motor_pins'])
    def log(self, o): print(f"{self.__str__()}: {o}")
        
    def setupPins(self):
        self.log("Setting up...")
        for pin in self.config['motor_pins']: GPIO.setup(pin, GPIO.OUT)
        self.setPinsLow()
        
    def steps_of_turn(self): return self.config['steps_of_turn']
    def velocity(self): return self.config['steps_per_millimeter']
    def pos(self): return self.step_pos
    def modulo_pos(self): return em.modulo(self.step_pos, self.steps_of_turn())
    
    def setSpeed(self, sleep: float): 
        if sleep > 0: self.step_sleep = sleep
        
    def setPinsLow(self):
        for pin in self.config['motor_pins']: GPIO.output( pin, GPIO.LOW )
        
    def step(self, **kwargs):
        if not self.ignore_step:
            for pinIndex in range(len(self.config['motor_pins'])): 
                GPIO.output(
                    self.config['motor_pins'][pinIndex], 
                    step_sequence[self.motor_step_counter][pinIndex]
                ) # setting the outputs for the sequence state
            
            orientation = kwargs.get('orientation', 1) # either 1 or -1
            mirror = -1 if self.config.get('mirror-inverted', False) else 1
            
            self.motor_step_counter = (self.motor_step_counter + orientation * mirror) % len(step_sequence) # count motor_step_counter
            if kwargs.get('count', True): self.step_pos += orientation
            
    def turn(self, **kwargs): # step_count < 0 means endless, turn(thread=False, steps=1, count=True)
        if kwargs.get('thread', False):
            kwargsNew = dict(kwargs)
            kwargsNew.update({'thread': False})
            thread = threading.Thread(target=self.turn, kwargs=kwargsNew)
            thread.start()
            return thread
            
        else:
            step_count_p = kwargs.get('steps', 1)
            step_count = abs(step_count_p)
            count = kwargs.get('count', True)
            if not count: print('!count is being ignored!')
            i = 0
            while i < step_count or step_count == -1:
                self.step(orientation=1 if step_count_p > 0 else -1, count=count)
                
                if i < step_count-1 or step_count == -1: time.sleep(self.step_sleep)
                i += 1
