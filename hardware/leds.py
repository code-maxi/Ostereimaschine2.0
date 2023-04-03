import threading
import RPi.GPIO as GPIO
import time

class EasterLEDs:
    def __init__(self, config: dict):
        self.config = config
        self.exit = False
        self.leds = self.config['status_leds']
        self.state = 0 # 0 adjust, 1 print, 2 finished
        
    def setup_pins(self):
        for led in self.leds.values(): GPIO.setup(led, GPIO.OUT)
        self.led_thread = threading.Thread(target=self.blink_loop)
        self.led_thread.start()

    def output_leds(self, led_out):
        for led in led_out:
            #print(f'setting led {led} on {self.leds[led]} to {led_out[led]}')
            GPIO.output(self.leds[led], GPIO.HIGH if led_out[led] else GPIO.LOW)

    def blink_loop(self):
        on = True
        while not self.exit:
            led_state = {
                 'blue': on if self.state == 2 else not on,
                 'white': True if self.state == 0 else on
            }            

            self.output_leds(led_state)
            
            on = not on
            time.sleep(self.config['led_sleep'])
            
    def cleanup(self):
        self.exit = True
        for led in self.leds.values(): GPIO.output(led, GPIO.LOW)
        