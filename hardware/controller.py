import math
import time
import RPi.GPIO as GPIO
import stepper
import servo
from pynput import keyboard

defaultEasterControlerConfig = {
	'ystepper': {
		'motor_pins': [4,17,27,22],
		'start_step_sleep': 0.003,
		'steps_of_turn': 4139
	},
	'xstepper': {
		'motor_pins': [23,24,25,26],
		'start_step_sleep': 0.003,
		'steps_of_turn': 4159,
		'wheel_radius': 7.65
	},
	'pstepper': {
		'motor_pins': [5,6,13,16],
		'start_step_sleep': 0.003,
		'steps_of_turn': 4159,
		'wheel_radius': 8.75
	},
	'servo': {
		'controlPin': 12,
		'frequenz': 50,
		'0DC': 2.5,
		'180DC': 12.5,
		'startPos': 1
	},
	'penup_offset': 0.25,
	'penup_sleep': 0.2,
	'egg_length': 58.5,
	'egg_use_percent': 80,
	'max_stepper_speed': 0.002,
	'color_pos': {
		'black': 2,
		'red': 2,
		'green': 3,
		'blue': 4,
		'orange': 4
	},
	'start_color': 'red',
	'color_distance': 10.8
}

class EasterControler:
	def __init__(self, config: dict):
		self.config = defaultEasterControlerConfig
		self.config.update(config)
		
		self.pen_servo_offset = 0
		self.penup = False
		self.current_penhole = self.config['start_color']]
		
		self.egg_border_width = self.config['egg_use_percent'] / 100 * self.config['egg_length']
		self.left_egg_border = -egg_border_width/2
		self.right_egg_border = egg_border_width/2
		
		print('Easter Controller initialized with following config:')
		print(self.config)
		
		self.setup()
		
	def setup(self):
		GPIO.setmode( GPIO.BCM )

		self.ystepper = stepper.EasterStepper(self.config['ystepper'])
		self.xstepper = stepper.EasterStepper(self.config['xstepper'])
		self.pstepper = stepper.EasterStepper(self.config['pstepper'])
		
		self.servo = servo.EasterServo(self.config['servo'])

	def cleanup(self):
		print('cleanup')
		
		self.ystepper.setPinsLow()
		self.xstepper.setPinsLow()
		self.pstepper.setPinsLow()
		self.servo.stopPWM()
		
		GPIO.cleanup()
		
	def getYWay(percent: float, longWay: bool):
		if percent < 0 or percent > 100: raise Exception(f'the y-pos ({percent}) has to be between 0% and 100%')
		
		steps_of_turn = self.ystepper.steps_of_turn()
		currentPos = self.ystepper.pos() % steps_of_turn
		newPos = round(percent / 100 * steps_of_turn)
		
		way1 = newPos - currentPos
		way2 = way1 + (-steps_of_turn if way1 > 0 else steps_of_turn)
		
		return max(way1, way2) if longWay else min(way1, way2)
	
	def xPos():
		return self.xstepper.pos()
		
	def yPos():
		return self.ystepper.pos()
	
	def getXWay(percent: float):
		if percent < -50 or percent > 50: raise Exception(f'the x-pos ({percent}) has to be between -50% and 50%')
		
		way = round(self.egg_border_width * percent / 100)
		
		return self.ystepper.stepsOfWay(way) - self.xstepper.pos()
	
	def stepper(coordinate: str):
		return self.xstepper if coordinate == 'x' else self.ystepper
	
	def lineTo(x: float, y: float, longWay: bool):
		xway = self.getXWay(x)
		yway = self.getYWay(y)
		
		print(f'line to: xway={xway} yway={yway} ')
		
		steppers = [self.xstepper, self.ystepper] if xway > yway else [self.ystepper, self.xstepper]
		time = (max(xway, yway) - 1) * self.config['max_stepper_speed']
		
		steppers[0].setSpeed(self.config['max_stepper_speed'])
		steppers[1].setSpeed(time / (min(xway, yway) - 1))
		
		print(f'stepper sleeps: faster={steppers[0].step_sleep} slower={steppers[1].step_sleep} ')
		
		print('Run steppers[0] turn in thread.')
		thread = steppers[0].turn(max(xway, yway), True, True)
		print('Run steppers[1] turn.')
		steppers[0].turn(min(xway, yway), True, False)
		
		print('steppers[1] turn finished')
		thread.join()
		print('steppers[0] turn finished\n')
		
	def moveTo(x: float, y: float, longWay: bool):
		self.penup()
		self.lineTo(x: float, y: float, longWay)
		self.pendown()
		
	def penup(): self.setPenUp(True)
	def pendown(): self.setPenUp(False)
	
	def changeColor(color: str):
		pos = self.config['color_pos'][color]
		way = (pos - self.current_penhole) * self.config['color_distance']
		steps = self.pstepper.stepsOfWay(way)
		
		self.pstepper.turn(steps, True, False)
		
		self.current_penhole = pos
		
	def setPenUp(self, up: bool):
		newPos = 1 - self.pen_servo_offset - (self.config['penup_offset'] if up else 0)
		self.penup = up
		
		print(f'penup pos: {newPos}')
		self.servo.setPos(newPos)
		
		time.sleep(self.config.get('penup_sleep', 0))
		
	def consoleDebug(self):
		escape = False
		
		turnCount = 0
		
		while not escape:
			inp = input('?: ')
			
			typ = inp.split(':')[0]
			
			if typ == 'ex': escape = True
			
			elif typ == 'penup': self.penup()
			elif typ == 'pendown': self.pendown()
			
			elif 'stepper' in typ:
				stepper = self.ystepper if typ[-1] == '1' else (self.xstepper if typ[-1] == '2' else self.pstepper)
				stepper.turn(int(turn), True, False)
				turnCount += int(turn)
				
			print(f'unbekannter typ "{typ}".')
				
		self.cleanup()
		exit(0)
		
	def testServo(self):		
		for i in range(100,0,-1):
			time.sleep(0.5)
			print('set sevo pos to ' + str(i / 100 * 360))
			print()
			self.servo.setPos(i / 100 * math.pi)
		self.servo.setPos(1)

	def startKeyboardControl(self):	
		self.ystepper.ignore_step = True
		self.xstepper.ignore_step = True
		self.pstepper.ignore_step = True
				
		th1 = self.ystepper.turn(-1, True, True)
		th2 = self.xstepper.turn(-1, True, True)
		th3 = self.pstepper.turn(-1, True, True)
		
		def on_press(key):			
			def checkStepper(stepper: stepper.EasterStepper, key1, key2):
				if key == key1:
					stepper.ignore_step = False
					stepper.step_forward = True
					
				if key == key2:
					stepper.ignore_step = False
					stepper.step_forward = False

			checkStepper(self.ystepper, keyboard.Key.up, keyboard.Key.down)
			checkStepper(self.xstepper, keyboard.Key.left, keyboard.Key.right)
			checkStepper(self.pstepper, keyboard.Key.page_up, keyboard.Key.page_down)
			
			if str(key) == 'w' or str(key) == 's':
				stepperPos += math.pi / 10 * (-1 if str(key) == 's' else 1)
				print(stepperPos)
				self.servo.setPos(stepperPos)
				
			if key == keyboard.Key.esc:
				self.ystepper.ignore_step = True
				self.xstepper.ignore_step = True
				self.pstepper.ignore_step = True
				print('Esc. pressed!')
				
			if key == keyboard.Key.space:
				print('extiting...')
				self.cleanup()
				exit(0)
                
		listener = keyboard.Listener(on_press=on_press)
		listener.start()
		
		th3.join()
		
		print('end')

try:
	easterControler = EasterControler(easterControlerConfig)
	easterControler.consoleDebug()
	easterControler.cleanup()

except KeyboardInterrupt:
	print('Program interrupted. Cleanup...')
	easterControler.cleanup()