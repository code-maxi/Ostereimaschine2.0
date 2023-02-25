import RPi.GPIO as GPIO
import stepper

easterControlerConfig = {
	'stepper1': {
		'motor_pins': [4,17,27,22],
		'start_step_sleep': 0.005
	},
	'stepper2': {
		'motor_pins': [23,24,25,26],
		'start_step_sleep': 0.005
	},
	'stepper3': {
		'motor_pins': [5,6,13,16],
		'start_step_sleep': 0.005
	}
}

class EasterControler:
	def __init__(self, config: dict):
		self.config = config
		self.setup()
		
	def setup(self):
		GPIO.setmode( GPIO.BCM )

		self.stepper1 = stepper.EasterStepper(self.config['stepper1'])
		self.stepper2 = stepper.EasterStepper(self.config['stepper2'])
		self.stepper3 = stepper.EasterStepper(self.config['stepper3'])

	def cleanup(self):
		self.stepper1.setPinsLow()
		self.stepper2.setPinsLow()
		self.stepper3.setPinsLow()
		
		GPIO.cleanup()
		
	def test(self):
		self.stepper1.turn(500, True)
		self.stepper2.turn(500, True).join()
		
		self.cleanup()
		

easterControler = EasterControler(easterControlerConfig)
easterControler.test()
