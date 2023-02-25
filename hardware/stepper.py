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
		self.step_sleep = self.config.get('start_step_sleep', 0.002)
		
		self.setupPins()
		
	def setupPins(self):
		for pin in self.config['motor_pins']: GPIO.setup( pin, GPIO.OUT )
		self.setPinsLow()
		
	def step(self):
		for pinIndex in range(len(self.config['motor_pins'])): 
			GPIO.output( self.config['motor_pins'][pinIndex], step_sequence[self.motor_step_counter][pinIndex] ) # setting the outputs for the sequence state
			
		self.motor_step_counter = (self.motor_step_counter + (1 if self.step_forward else -1)) % len(step_sequence) # count motor_step_counter
		
	def setPinsLow(self):
		for pin in self.config['motor_pins']: GPIO.output( pin, GPIO.LOW )
		
		
	def turn(self, step_count: int, thread: bool): # step_count < 0 means endless
		if thread:
			print('Thread...')
			
			thread = threading.Thread(target=self.turn, args=(step_count, False))
			thread.start()
			return thread
			
		else:
			print('No thread.\n')
			i = 0
			while i < step_count:
				self.step()
				time.sleep(self.step_sleep)
				i += 1
