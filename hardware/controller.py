import json
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
	
	'egg_length': 58.5,
	'egg_height': 41,
	'egg_use_percent': 50,
	
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
	'color_distance': 10.8,
	
	'penup_offset': 0.25,
	'penup_sleep': 0.5,
	
	'pen_lazy': 25,
	'pen_lazy_sleep': 0.05,
	'pen_stroke_width': 1
}

class EasterControler:
	def __init__(self, config: dict):
		self.config = defaultEasterControlerConfig
		self.config.update(config)
		
		self.pen_servo_offset = 0
		self.ispenup = False
		self.current_color = self.config['start_color']
		
		self.egg_border_width = self.config['egg_use_percent'] / 100 * self.config['egg_length']
		
		self.print_piority = 2
		self.log('__init__ with config: ', 10)
		
		self.current_direction = 0
		
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
		return em.egg_caliber(xpercent, self.config['egg_height'])
	
	def x_steps(self, xunit: float, **kwargs):
	    steps = xunit
	
	    if not kwargs.get('step_unit', False):
		    if xunit < -50 or xunit > 50: raise Exception(f'the x-pos ({xunit}) has to be between -50% and 50%')
		    distance = xunit / 100 * self.egg_border_width
		    steps = self.xstepper.distance_to_steps(distance)
		
		self.log(f'x-way: distance={distance}mm steps={steps}x pos={self.x_pos()}')
		return steps - self.xstepper.pos()
		
	def y_steps(self, yunit: float, **kwargs):
		steps_of_turn = self.ystepper.steps_of_turn()
		
		newPos = yunit
		
		if not kwargs.get('step_unit', False):
			factor = em.modulo(yunit, 100) / 100
			newPos = round(factor * steps_of_turn)
		
		steps1 = newPos - self.y_pos()
		steps2 = steps1 + (-steps_of_turn if steps1 > 0 else steps_of_turn)
		
		minmax = em.abs_minmax(steps1, steps2)
		index = 1 if kwargs.get('long', False) == True else 0
		
		return minmax[index]
		
	def steps_to(self, xsteps: int, ysteps: int):
		if xsteps != 0 or ysteps != 0:
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
			
			self.log(f'steps_to:\nsteps_minmax:{steps_minmax}\nstepper_minmax:{stepper_minmax}\nsleep_minmax:{sleep_minmax}\n______')
			
			stepper_minmax[1].setSpeed(sleep_minmax[1])
			stepper_minmax[0].setSpeed(sleep_minmax[0])
			
			thread =				     stepper_minmax[1].turn(steps=steps_minmax[1], thread=True)
			if abs(steps_minmax[0]) > 0: stepper_minmax[0].turn(steps=steps_minmax[0], thread=False)
			
			thread.join()
		
	def line_to(self, xunit: float, yunit: float, **kwargs):
		move = kwargs.get('move', False)
		step_unit = kwargs.get('step', False)
		
		xsteps = self.x_steps(xunit, step_unit=step_unit)
		ysteps = self.y_steps(yunit, step_unit=step_unit, long=kwargs.get('long', False))
		
		if xsteps != 0 or ysteps != 0: 
		    if move:
			    self.penup()
			    self.current_direction = 0
		    
		    new_direction = em.direction(xsteps)
		    
		    if self.current_direction != new_direction and not move:
			    time.sleep(self.config['pen_lazy_sleep'])
			    
			    adjustment_steps = self.config['pen_lazy'] * (new_direction - self.current_direction)
			    self.log(f'adjustment_steps={adjustment_steps}', 10)
			    self.xstepper.turn(steps=adjustment_steps, count=False)
			    self.current_direction = new_direction
			    
			    time.sleep(self.config['pen_lazy_sleep'])
		    
		    self.log(f'line to steps: {xsteps}:{ysteps}')
		    self.steps_to(xsteps, ysteps)
		    
		    if move: self.pendown()
		
	def move_to(self, xunit: float, yunit: float):
		self.line_to(xpercent, ypercent, move=True)
		
	def x_stroke_steps(self) = self.xstepper.distance_to_steps(self.config['pen_stroke_width'])
	def y_stroke_steps(self) = 50 #TODO!
		
	def circle(self, **kwargs):
		xpos_p = kwargs.get('xpos', self.x_pos())
		ypos_p = kwargs.get('ypos', self.y_pos())
		
		xrad = kwargs.get('rad', 100)
		yrad = kwargs.get('yrad', xrad)
		
		xpos = kwargs.get('xcenter', 0) * xrad + xpos_p
		ypos = kwargs.get('ycenter', 0) * yrad + ypos_p
		
		res = kwargs.get('res', 4)
		
		depthspace = "  " * kwargs.get('depth', 0)
		colors     = kwargs.get('colors', [self.current_color])
		colorindex = kwargs.get('colorindex', 0)
		
		self.change_color(colors[colorindex])
		
		self.log(f'{depthspace}drawing circle with args {kwargs} on pos {self.pos_to_string()}', 10)
				
		for r in range(res+1):
			angle = r / res * 2 * math.pi
			new_xpos = round(xpos + math.cos(angle) * xrad)
			new_ypos = round(ypos + math.sin(angle) * yrad)
			self.log(f'{depthspace}index={r} angle={angle}:{angle/math.pi * 180} cos={math.cos(angle)} sin={math.sin(angle)} newx={new_xpos} newy={new_ypos}')
			
			self.line_to(new_xpos, new_ypos, move=(r == 0), step=True)
			
		if kwargs.get('fill', False):
		    sub_steps_x = kwargs.get('sub_steps_x', self.x_stroke_steps()) # getting pen stroke smaller
		    sub_steps_y = kwargs.get('sub_steps_y', self.y_stroke_steps()) # getting pen stroke smaller
		    new_xrad = xrad - sub_steps_x
		    new_yrad = yrad - sub_steps_y
		    
		    if new_xrad > 0 and new_yrad > 0:
		        new_kwargs = dict(kwargs)
		        
		        new_kwargs.update({
		            'rad': new_xrad, 
		            'yrad': new_yrad, 
		            'depth': depth + 1,
		            'xcenter': -1, # the circle is left placed
		            'colors': colors,
		            'colorindex': colorindex + 1 % len(colors)
	            })
	            
		        self.circle(**new_kwargs) # recursive call
		        
		        
		
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
		
		current_pos = self.config['color_pos'][self.current_color]
		new_pos     = self.config['color_pos'][color]
		
		if (current_pos != new_pos):
			self.penup()
			
			distance = (pos - current_pos) * self.config['color_distance']
			steps = self.zstepper.distance_to_steps(distance)
			
			self.log(f"distance: {distance}mm")
			self.log(f"steps: {steps}x")
			
			self.zstepper.turn(steps=steps)
			self.current_color = color
			
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
				
				elif typ == 'circle':
					res = int(split[1])
					rad = int(split[2])
					self.circle(rad=rad, yrad=round(2/5*rad), res=res)
					
				else: self.log(f'Unbekannter typ "{typ}".', 10)
			
			except:
				self.log(f'ERROR:', 10)
				traceback.print_exc()
				
		self.cleanup()
		exit(0)
		
controller = EasterControler({})
controller.consoleDebug()

