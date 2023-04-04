import RPi.GPIO as GPIO
import time

class EasterServo:
    def __init__(self, config: dict):
        self.config = config
        self.current_pos = self.config.get('startPos', 0)
        
    def setup_pins(self):
        print(f"Setting up servo motor on GPIO{self.config['controlPin']} with start pos {self.config['startPos']}...")
        
        GPIO.setup(self.config['controlPin'], GPIO.OUT)

        self.pin = GPIO.PWM(self.config['controlPin'], self.config['frequenz']) # GPIO 17 for PWM with 
        self.pin.start(self.new_pos(self.current_pos))
        
    def new_pos(self, pos: float):
        return ((self.config['180DC'] - self.config['0DC']) * pos + self.config['0DC']) if pos >= 0 and pos <= 1 else -1
        
    # sets the position of the stepper between 0 and 2pi degrees (0 <= pos <= 2pi)
    def set_pos(self, pos: float, **kwargs):
        times = kwargs.get('times', 1)
        delay = kwargs.get('delay', 0.25)
        #print(f'times={times} delay={delay}')
        new_pos = float
        delta = (pos - self.current_pos) / times
        for i in range(times):
            new_pos = delta * (i+1) + self.current_pos
            if new_pos != -1:  self.pin.ChangeDutyCycle(self.new_pos(new_pos))
            if i < times - 1: time.sleep(delay / (times-1))
            
        self.current_pos = new_pos
            
        return new_pos

    def stopPWM(self):
        self.pin.stop()
