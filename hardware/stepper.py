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
		
		self.wheel_extent = 2 * math.pi * self.config['wheel_radius']
		
		self.step_pos = 0
		
		self.setupPins()
		
	def setupPins(self):
		print(f"Setting up stepper motor on GPIO{str(self.config['motor_pins'])}...")
		
		for pin in self.config['motor_pins']: GPIO.setup( pin, GPIO.OUT )
		self.setPinsLow()
	
	def getCurrentWay(self):
		return self.step_pos / self.steps_of_turn() * self.wheel_extent
	
	def stepsOfWay(self, millimeters: float):
		return millimeters / self.wheel_extent * self.steps_of_turn()
	
	def steps_of_turn(self):
		return self.config.get['steps_of_turn']

	def pos(self):
		return self.step_pos
	
	def setSpeed(sleep: float):
		self.step_sleep = sleep
		
	def step(self, **kwargs):
		if not self.ignore_step:
			for pinIndex in range(len(self.config['motor_pins'])): 
				GPIO.output( self.config['motor_pins'][pinIndex], step_sequence[self.motor_step_counter][pinIndex] ) # setting the outputs for the sequence state
				
			add = (1 if self.step_forward else -1)	
			self.motor_step_counter = (self.motor_step_counter + add) % len(step_sequence) # count motor_step_counter
			if (kwargs.get('countStep', False)) self.step_pos += add
		
	def setPinsLow(self):
		for pin in self.config['motor_pins']: GPIO.output( pin, GPIO.LOW )
		
	def turn(self, step_count_p: int, countStep: bool, thread: bool): # step_count < 0 means endless
		self.step_forward = step_count_p < 0
		step_count = abs(step_count_p)
		
		if thread:	
			thread = threading.Thread(target=self.turn, args=(step_count, countStep, False))
			thread.start()
			return thread
			
		else:
			GPIO.setmode( GPIO.BCM )
			i = 0
			
			while i < step_count or step_count == -1:
				self.step(countStep=countStep)
				if (i < step_count-1) time.sleep(self.step_sleep)
				i += 1
