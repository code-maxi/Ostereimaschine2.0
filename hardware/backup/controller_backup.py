import traceback
import math
import time
import RPi.GPIO as GPIO
import stepper
import servo
import threading
from pynput import keyboard

defaultEasterControlerConfig = {
	'ystepper': {
		'motor_pins': [4,17,27,22],
		'start_step_sleep': 0.003,
		'steps_of_turn': 4139,
		'name': 'Y-Stepper'
	},
	'xstepper': {
		'motor_pins': [23,24,25,26],
		'start_step_sleep': 0.003,
		'steps_of_turn': 4159,
		'wheel_radius': 7.65,
		'name': 'X-Stepper',
		'mirror-inverted': True
	},
	'zstepper': {
		'motor_pins': [5,6,13,16],
		'start_step_sleep': 0.002,
		'steps_of_turn': 4159,
		'wheel_radius': 7.8,
		'name': 'Z-Stepper',
		'mirror-inverted': True
	},
	'servo': {
		'controlPin': 12,
		'frequenz': 50,
		'0DC': 2.5,
		'180DC': 12.5,
		'startPos': 1
	},
	'penup_offset': 0.275,
	'penup_sleep': 0.2,
	'egg_length': 58.5,
	'egg_use_percent': 70,
	'max_stepper_speed': 0.002,
	'color_pos': {
		'black': 1,
		'red': 2,
		'green': 3,
		'blue': 4,
		'orange': 5
	},
	'change_color_steps': 50,
	'start_color': 'blue',
	'color_distance': 10.8
}

def em(pn, z):
	n = pn
	while n > z: n -= z
	while n < 0: n += z
	return n

class EasterControler:
	def __init__(self, config: dict):
		self.config = defaultEasterControlerConfig
		self.config.update(config)
		
		self.pen_servo_offset = 0
		self.ispenup = False
		self.current_penhole = self.config['color_pos'][self.config['start_color']]
		
		self.egg_border_width = self.config['egg_use_percent'] / 100 * self.config['egg_length']
		
		self.key_on = threading.Event()

		
		self.log('initialized with following config:')
		self.log(self.config)
		
		self.setup()
		
	def log(self, obj):
		#print('EasterControler: ' + str(obj))
		pass
		
	def setup(self):
		self.log('Easter Controller setup...')
	 	
		GPIO.setmode( GPIO.BCM )

		self.ystepper = stepper.EasterStepper(self.config['ystepper'])
		self.xstepper = stepper.EasterStepper(self.config['xstepper'])
		self.zstepper = stepper.EasterStepper(self.config['zstepper'])
		
		self.servo = servo.EasterServo(self.config['servo'])

	def cleanup(self):
		self.log('cleanup')
		
		self.ystepper.setPinsLow()
		self.xstepper.setPinsLow()
		self.zstepper.setPinsLow()
		self.servo.stopPWM()
		
		GPIO.cleanup()
		
	def getXWay(self, percent: float):
		if percent < -50 or percent > 50: raise Exception(f'the x-pos ({percent}) has to be between -50% and 50%')
		
		way = round(percent / 100 * self.egg_border_width)
		steps = self.xstepper.stepsOfWay(way)
		currentPos = self.xstepper.pos()
		
		self.log(f'x-way: way={way} steps={steps} XPOS={currentPos}')
		
		return steps - currentPos
	
	
	def getYPos(self):
		return em(self.ystepper.pos(), self.ystepper.steps_of_turn())
	
	def getYWay(self, ppercent: float, longWay: bool):				
		percent = em(ppercent, 100)
		steps_of_turn = self.ystepper.steps_of_turn()
		currentPos = self.getYPos()
		
		self.log(f'y-way: YPOS={currentPos}')
		self.log(f'y-way: steps_of_turn={steps_of_turn}')
			
		self.log(f'y-way: stepper_pos={self.ystepper.pos()}')
		
		newPos = round(percent / 100 * steps_of_turn)
		self.log(f'y-way: newPos={newPos}')
		
		way1 = newPos - currentPos
		way2 = way1 + (-steps_of_turn if way1 > 0 else steps_of_turn)
		
		maxway = way1
		minway = way2
		if abs(way2) > abs(way1):
			maxway = way2
			minway = way1
			
		self.log(f'y-way: way1={way1}')
		self.log(f'y-way: way2={way2}')
				
		return maxway if longWay else minway
	
	
	def circle(self, r: int):
		xpos_start = self.xstepper.pos()
		ypos_start = self.ystepper.pos()
		ppos = (r,0)
		
		def quarterCircle(pos: (int,int), x_inc: int, y_inc: int, x_target: int, y_target: int, fx: int, fy: int):
			px = pos[0]
			py = pos[1]
			
			self.log(f'\n quarterCircle: pos={pos} x_inc={x_inc} y_inc={y_inc} x_target={x_target} y_target={y_target}')
			
			while px != x_target and py != y_target:
				opx = px
				opy = py
				
				if abs(px) > abs(py):
					px += x_inc
					if abs(px) > r: px -= x_inc
					py = round(math.sqrt(r*r - px*px) * fy)
				else:
					py += y_inc
					if abs(py) > r: py -= y_inc
					px = round(math.sqrt(r*r - py*py) * fx)
				
				xway = px - opx
				yway = py - opy
				
				self.log(f'circle: way=({xway}|{yway}) ({opx}|{opy}) => ({px}|{py}) | tx-px={x_target-px} ty-py={y_target-py}')
				#self.log(f'circle: xway={xway} yway={yway}\n -------------')
				
				self.wayTo(xway, yway)
				
			return (px, py)
		
		ppos = quarterCircle(ppos, -1, 1, 0, r, 1, 1)
		ppos = quarterCircle(ppos, -1,-1,-r, 0,-1, 1)
		ppos = quarterCircle(ppos,  1,-1, 0,-r,-1,-1)
		ppos = quarterCircle(ppos,  1, 1, r, 0, 1,-1)
	
	
	def stepper(self, name: str):
		stepper = None
		if name == 'xstepper': stepper = self.xstepper
		if name == 'ystepper': stepper = self.ystepper
		if name == 'zstepper': stepper = self.zstepper
		return stepper
	
	def logPos(self):
		x = round(self.xstepper.getCurrentWay()/self.egg_border_width*100,2)
		y = round(self.getYPos()/self.ystepper.steps_of_turn()*100,2)
		self.log(f"({x}% | {y}%) color: {self.current_penhole}")
	
	def wayTo(self, xway: int, yway: int):
		minway = yway
		maxway = xway
		minstepper = self.ystepper
		maxstepper = self.xstepper
		
		if abs(yway) > abs(xway):
			minway = xway
			maxway = yway
			minstepper = self.xstepper
			maxstepper = self.ystepper
		
		self.log(f'way to: xway={xway} yway={yway} ')
		self.log(f'way to: minway={minway} maxway={maxway} ')
						
		duration = (abs(maxway) - 1) * self.config['max_stepper_speed']
		
		self.log(f'way to: duration={duration}s')
		
		maxstepper.setSpeed(self.config['max_stepper_speed'])
		if abs(minway) > 1: minstepper.setSpeed(duration / (abs(minway) - 1))
		
		self.log(f'stepper sleeps: faster={maxstepper.step_sleep} slower={minstepper.step_sleep} ')
		
		self.log(f'Run maxstepper turn {maxway} in thread.')
		thread = maxstepper.turn(maxway, True, True)
		
		if abs(minway) > 0:
			self.log(f'Run minstepper turn {minway}.')
			minstepper.turn(minway, True, False)
			self.log('minstepper turn finished')
		
		thread.join()
		self.log('maxstepper turn finished')
		self.logPos()
	
	def lineTo(self, x: float, y: float, **kwargs):
		xway = self.getXWay(x)
		yway = self.getYWay(y, kwargs.get('longWay', False))
		self.log(f'line to y-way: {yway}')
		self.wayTo(xway, yway)
		
	def moveTo(self, x: float, y: float):
		self.setPenUp(True)
		self.lineTo(x, y)
		self.setPenUp(False)
		
	def zigzag(self, a: float, h: float):
		for y in range(round(100/h)):
			self.lineTo(a/2 if y & 2 == 0 else -a/2, y*h + h/2)
		
	def penup(self):
		self.setPenUp(True)
	
	def pendown(self):
		self.setPenUp(False)
	
	def changeColor(self, color: str):
		self.log(f"changing color to {color}")
		
		pos = self.config['color_pos'][color]
		
		if (pos != self.current_penhole):
			self.penup()
			
			print(type(pos))
			print(type(self.current_penhole))
			print(type(self.config['color_distance']))
			
			way = (pos - self.current_penhole) * self.config['color_distance']
			self.log(f"way: {way}")
			steps = self.zstepper.stepsOfWay(way)
			self.log(f"way: {steps}")
			
			self.zstepper.turn(steps, True, False)
			self.log("zstepper turn finished")
			
			self.current_penhole = pos
			
			self.pendown()
			
			return steps
		
	def setPenUp(self, up: bool):
		newPos = 1 - self.pen_servo_offset - (self.config['penup_offset'] if up else 0)
		self.ispenup = up
		
		self.log(f'penup pos: {newPos}')
		self.servo.setPos(newPos)
		
		time.sleep(self.config.get('penup_sleep', 0))
		
	def consoleDebug(self):
		escape = False
		
		turnCount = 0
				
		while not escape:
			inp = input('?: ')
			
			split = inp.split(':')
			typ = split[0]
			
			try:
				if typ == 'ex': escape = True
			
				elif typ == 'penup': self.setPenUp(True)
				elif typ == 'pendown': self.setPenUp(False)
				
				elif 'stepper' in typ:
					stepper = self.stepper(typ)
					turn = int(split[1])
					log = split[2] == 'True'
					
					self.log(f'{stepper} turns {turn} log {log}')
					
					stepper.turn(int(turn), log, False)
					turnCount += turn
					
					self.log(f'pos: {stepper.pos()}')
					
				elif typ == 'color':
					steps = self.changeColor(split[1])
					self.log(f'change color steps: {steps}')
					
				elif typ == 'key':
					if bool(split[1]): self.key_on.set()
					else: self.key_on.clear()
					print(self.key_on.is_set())
					
				elif typ == 'circle':
					radius = int(split[1])
					self.circle(radius)
					
				elif typ == 'lineto' or type == 'moveto':
					x = float(split[1])
					y = float(split[2])
					
					lw = split[3] == 'True'
					
					self.log(f'line to ({x}|{y}), long={lw}')
					
					if typ == 'lineto': self.lineTo(x, y, longWay=lw)
					if typ == 'moveto': self.moveTo(x, y)
					
				elif typ == 'grid':
					for x in range(-50, 50, 10):
						print(f'x = {x}%: y = ', end='')
						for y in range(10, 100, 10):
							print(f'{y}% ', end='')
							self.moveTo(x,y)
						print('')	
						
				elif typ == 'pos':
					self.logPos()
						
				elif typ == 'zigzag':
					self.zigzag(20, 10)
					
				else: self.log(f'unbekannter typ "{typ}".')
			
			except:
				self.log(f'falscher parameter "{typ}".')
				traceback.print_exc()
				
		self.cleanup()
		exit(0)
		
	def testServo(self):		
		for i in range(100,0,-1):
			time.sleep(0.5)
			self.log('set sevo pos to ' + str(i / 100 * 360))
			self.log()
			self.servo.setPos(i / 100 * math.pi)
		self.servo.setPos(1)

	def startKeyboardControl(self):	
		self.ystepper.ignore_step = True
		self.xstepper.ignore_step = True
		self.zstepper.ignore_step = True
				
		th1 = self.ystepper.turn(-1, True, True)
		th2 = self.xstepper.turn(-1, True, True)
		th3 = self.zstepper.turn(-1, True, True)
		
		def on_press(key):
			if self.key_on.is_set():				
				def checkStepper(stepper: stepper.EasterStepper, key1, key2):
					if key == key1:
						stepper.ignore_step = False
						stepper.step_forward = True
						
					if key == key2:
						stepper.ignore_step = False
						stepper.step_forward = False

				checkStepper(self.ystepper, keyboard.Key.up, keyboard.Key.down)
				checkStepper(self.xstepper, keyboard.Key.left, keyboard.Key.right)
				checkStepper(self.zstepper, keyboard.Key.page_up, keyboard.Key.page_down)
				
				if str(key) == 'w' or str(key) == 's':
					stepperPos += math.pi / 10 * (-1 if str(key) == 's' else 1)
					self.log(stepperPos)
					self.servo.setPos(stepperPos)
					
				if key == keyboard.Key.esc:
					self.ystepper.ignore_step = True
					self.xstepper.ignore_step = True
					self.zstepper.ignore_step = True
					self.log('Esc. pressed!')
					
				if key == keyboard.Key.space:
					self.log('extiting...')
					self.cleanup()
					exit(0)
					
		listener = keyboard.Listener(on_press=on_press)
		listener.start()
		
		th3.join()
		
		self.log('end')

try:
	easterControler = EasterControler({})
	easterControler.consoleDebug()

except KeyboardInterrupt:
	self.log('Program interrupted. Cleanup...')
	easterControler.cleanup()