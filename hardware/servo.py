import threading
import time
import RPi.GPIO as GPIO
import math

class EasterServo:
    def __init__(self, config: dict):
        self.config = config
        self.setup()
        
    def setup(self):
        print(f"Setting up servo motor on GPIO{self.config['controlPin']} with start pos {self.config['startPos']}...")
        
        GPIO.setup(self.config['controlPin'], GPIO.OUT)

        self.pin = GPIO.PWM(self.config['controlPin'], self.config['frequenz']) # GPIO 17 for PWM with 
        self.pin.start(self.newPos(self.config.get('startPos', 0)))
        
    def newPos(self, pos: float):
        return ((self.config['180DC'] - self.config['0DC']) * pos + self.config['0DC']) if pos >= 0 and pos <= 1 else -1
        
    # sets the position of the stepper between 0 and 2pi degrees (0 <= pos <= 2pi)
    def setPos(self, pos: float):
        newpos = self.newPos(pos)
        if newpos == -1: return False
        else:
             self.pin.ChangeDutyCycle(newpos)
             return True

    def stopPWM(self):
        self.pin.stop()
