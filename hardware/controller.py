import traceback
import math
import time
import RPi.GPIO as GPIO
import stepper
import servo
import threading
import eastermath as em

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
	'egg_height': 41
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

class EasterControler:
	def __init__(self, config: dict):
		self.config = defaultEasterControlerConfig
		self.config.update(config)
		
		self.pen_servo_offset = 0
		self.ispenup = False
		self.current_penhole = self.config['color_pos'][self.config['start_color']]
		
		self.egg_border_width = self.config['egg_use_percent'] / 100 * self.config['egg_length']
		
		self.print_piority = 0
		self.log('__init__ with config: ', 10)
		print(self.config)
		print()
		
		self.setup()
		
	def log(self, obj, *args):
		prio = em.get_save(args, 0, 0) 
		if prio >= self.print_piority: print('EasterControler: ' + str(obj))
		
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
		
	def x_percent(self): return self.xstepper.steps_to_distance() / self.egg_border_width * 100
	def y_percent(self): return self.y_pos() / self.ystepper.steps_of_turn() * 100
	
	def y_caliber(self):
		xpercent = self.xstepper.steps_to_distance() / self.config['egg_length']
		return em.egg_caliber(self, xpercent, self.config['egg_height'])
	
	def x_steps(self, percent: float):
		if percent < -50 or percent > 50: raise Exception(f'the x-pos ({percent}) has to be between -50% and 50%')
		distance = percent / 100 * self.egg_border_width
		steps = self.xstepper.distance_to_steps(distance)
		
		self.log(f'x-way: distance={distance}mm steps={steps}x pos={self.x_pos()}')
		return steps - self.xstepper.pos()
		
	def y_steps(self, percent: float, **kwargs):
		factor = em.modulo(percent, 100) / 100
		steps_of_turn = self.ystepper.steps_of_turn()
		
		newPos = round(factor * steps_of_turn)
		steps1 = newPos - self.y_pos()
		steps2 = steps1 + (-steps_of_turn if steps1 > 0 else steps_of_turn)
		
		minmax = em.abs_minmax(steps1, steps2)
		index = 1 if kwargs.get('long', False) == True else 0
		
		return minmax[index]
		
	def way_to(self, xsteps: int, ysteps: int):
		steps_minmax   = em.abs_minmax(xsteps, ysteps)
		isx_max		= steps_minmax[1] == xsteps
		stepper_minmax = (
			self.ystepper if isx_max else self.xstepper,
			self.xstepper if isx_max else self.ystepper
		)
		
		max_sleep = self.config['max_stepper_speed']
		duration = (abs(steps_minmax[1]) - 1) * max_sleep
		min_sleep = duration / (abs(steps_minmax[0]) - 1) if abs(steps_minmax[0]) > 1 else -1
		
		sleep_minmax = (min_sleep, max_sleep)
		
		self.log(f'way_to:\nsteps_minmax:{steps_minmax}\nstepper_minmax:{stepper_minmax}\nsleep_minmax:{sleep_minmax}\n______')
		
		stepper_minmax[1].setSpeed(sleep_minmax[1])
		stepper_minmax[0].setSpeed(sleep_minmax[0])
		
		thread =				   stepper_minmax[1].turn(steps=steps_minmax[1], thread=True)
		if abs(steps_minmax[0]) > 0: stepper_minmax[0].turn(steps=steps_minmax[0], thread=False)
		
		thread.join()
		
	def line_to(self, xpercent: float, ypercent: float, **kwargs):
		xsteps = self.x_steps(xpercent)
		ysteps = self.y_steps(ypercent, long=kwargs.get('long', False))
		self.log(f'line to steps: {xsteps}:{ysteps}')
		self.way_to(xsteps, ysteps)
		
	def move_to(self, xpercent: float, ypercent: float):
		self.penup()
		self.line_to(xpercent, ypercent)
		self.pendown()
		
	def penup(self):   self.set_pen_up(True)
	def pendown(self): self.set_pen_up(False)
	
	def set_pen_up(self, up: bool):
		newPos = 1 - self.pen_servo_offset - (self.config['penup_offset'] if up else 0)
		self.ispenup = up
		
		self.log(f'penup pos: {newPos}')
		self.servo.setPos(newPos)
		
		time.sleep(self.config.get('penup_sleep', 0))
		
	def change_color(self, color: str):
		self.log(f"Changing color to {color}...", 5)
		
		pos = self.config['color_pos'][color]
		
		if (pos != self.current_penhole):
			self.penup()
			
			distance = (pos - self.current_penhole) * self.config['color_distance']
			steps = self.zstepper.distance_to_steps(distance)
			
			self.log(f"distance: {distance}mm")
			self.log(f"steps: {steps}x")
			
			self.zstepper.turn(steps=steps)
			self.current_penhole = pos
			
			self.pendown()
			
			return steps
	
	def cleanup(self):
		self.log('cleanup', 10)
		
		self.ystepper.setPinsLow()
		self.xstepper.setPinsLow()
		self.zstepper.setPinsLow()
		self.servo.stopPWM()
		
		GPIO.cleanup()
		
	def pos_to_string(self):
		dp = 2
		xsteps = round(self.x_pos(), dp)
		ysteps = round(self.y_pos(), dp)
		xdistance = round(self.xstepper.steps_to_distance(), dp)
		xpercent = round(self.x_percent(), dp)
		ypercent = round(self.y_percent(), dp)
		return f"({xpercent}% | {ypercent}%) ({xdistance}mm | ?mm) ({xsteps}x | {ysteps}x)"
		
	def log_pos(self): self.log(self.pos_to_string(), 10)
		
	def consoleDebug(self):
		escape = False
				
		while not escape:
			inp = input('?: ')
			
			split = inp.split(':')
			typ = split[0]
			
			try:
				if typ == 'ex': escape = True
			
				elif typ == 'penup': self.penup()
				elif typ == 'pendown': self.pendown()
				
				elif 'stepper' in typ:
					stepper = self.stepper(typ)
					turn = int(split[1])
					count = split[2] == 'True'
					
					self.log(f'{stepper} turns {turn} count {count}', 5)
					stepper.turn(steps=int(turn), count=count)
					self.log(f'pos: {stepper.pos()}', 5)
					
				elif typ == 'color':
					steps = self.change_color(split[1])
					self.log(f'change color steps: {steps}', 5)
					
				elif typ == 'circle':
					radius = int(split[1])
					self.circle(radius)
					
				elif typ == 'lineto' or typ == 'moveto':
					x = float(split[1])
					y = float(split[2])
					
					lw = split[3] == 'True'
					
					self.log(f'line to ({x}|{y}), long={lw}', 5)
					
					if typ == 'lineto': self.line_to(x, y, long=lw)
					if typ == 'moveto': self.move_to(x, y)
					
				elif typ == 'grid':
					for x in range(-50, 50, 10):
						print(f'x = {x}%: y = ', end='')
						for y in range(10, 100, 10):
							print(f'{y}% ', end='')
							self.move_to(x,y)
						print('')	
						
				elif typ == 'pos': self.log_pos()
				elif typ == 'caliber': self.log(f"{self.y_caliber()}", 10)
					
				else: self.log(f'Unbekannter typ "{typ}".', 10)
			
			except:
				self.log(f'ERROR:', 10)
				traceback.print_exc()
				
		self.cleanup()
		exit(0)
		
controller = EasterControler({})
controller.consoleDebug()

