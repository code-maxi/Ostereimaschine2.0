import math
import threading
import time
import RPi.GPIO as GPIO

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
		self.step_forward = False
		self.step_sleep = self.config.get('start_step_sleep', 0.003)
		self.ignore_step = False
		
	    self.wheel_extent = 2 * math.pi * self.config.get('wheel_radius', 10)
		
		self.step_pos = 0
		self.log_priority = 0
		
		self.setupPins()
		
	def __str__(self):
		return self.config['name']+str(self.config['motor_pins'])
		
	def log(self, obj, **kwargs):
		if kwargs.get('prio', 10) self.log_priority: print(self.config['name'] + ': ' + str(obj))
		
	def setupPins(self):
		self.log(f"Setting up stepper motor on GPIO{str(self.config['motor_pins'])}...")
		
		for pin in self.config['motor_pins']: GPIO.setup( pin, GPIO.OUT )
		self.setPinsLow()
	
	def getCurrentWay(self): return self.step_pos / self.steps_of_turn() * self.wheel_extent
	
	def stepsOfWay(self, millimeters: float): return round(millimeters / self.wheel_extent * self.steps_of_turn())
	
	def steps_of_turn(self):
		return self.config['steps_of_turn']

	def pos(self):
		return self.step_pos
	
	def setSpeed(self, sleep: float):
		self.step_sleep = sleep
		
	def step(self, **kwargs):
		#self.log(f'log ignore_step: {self.ignore_step}')
		
		if not self.ignore_step:
			for pinIndex in range(len(self.config['motor_pins'])): 
				GPIO.output( self.config['motor_pins'][pinIndex], step_sequence[self.motor_step_counter][pinIndex] ) # setting the outputs for the sequence state
			
			orientation = kwargs.get('orientation', 1)
			mirror = -1 if self.config.get('mirror-inverted', False) else 1
			
			self.motor_step_counter = (self.motor_step_counter + orientation * mirror) % len(step_sequence) # count motor_step_counter
			
			if kwargs.get('countStep', False) == True:
				#self.log(orientation)
				self.step_pos += orientation
		
	def setPinsLow(self):
		for pin in self.config['motor_pins']: GPIO.output( pin, GPIO.LOW )
		

	def turn(self, step_count_p: int, countStep: bool, thread: bool): # step_count < 0 means endless
		if thread:	
			thread = threading.Thread(target=self.turn, args=(step_count_p, countStep, False))
			thread.start()
			return thread
			
		else:
			step_count = abs(step_count_p)
			
			GPIO.setmode( GPIO.BCM )
			i = 0
			
			while i < step_count or step_count == -1:
				self.step(orientation=1 if step_count_p > 0 else -1, countStep=countStep)
				
				if i < step_count-1 or step_count == -1:
					time.sleep(self.step_sleep)
					
				i += 1
