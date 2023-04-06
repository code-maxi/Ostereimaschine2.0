from screeninfo import get_monitors
monitors = get_monitors()
default_height = monitors[0].height - 50
default_width = monitors[0].width * 0.7

defaultEasterControlerConfig = {
    'ystepper': {
        'motor_pins': [4,17,27,22],
        'start_step_sleep': 0.003,
        'steps_of_turn': 4110, # 4110 +- 50 Abweichung
        #'mirror-inverted': True, # NEW!
        'laziness': 25,
        'name': 'Y-Stepper'
    },
    'xstepper': {
        'motor_pins': [23,24,25,26],
        'start_step_sleep': 0.003,
        'steps_of_turn': 4159,
        'laziness': 50,#50,
        #'wheel_radius': 7.65,
        'name': 'X-Stepper',
        'mirror-inverted': True,
        'steps_per_millimeter': 92 # Exact: 91.74311926605505
    },
    'zstepper': {
        'motor_pins': [5,6,13,16],
        'start_step_sleep': 0.002,
        'steps_of_turn': 4159,
        #'wheel_radius': 7.8,
        'name': 'Z-Stepper',
        'mirror-inverted': True
    },
    'servo': {
        'controlPin': 12,
        'frequenz': 50,
        '0DC': 2.5,
        '180DC': 12.5,
        'startPos': 0.75
    },
    
    'servo_delay': 0.5,
    'servo_times': 100,
    
    'egg_length': 58.5,
    'egg_height': 41,
    'egg_use_percent': 70,
    
    'max_stepper_speed': 0.0025,
    
    'color_pos': {
        'black': 0,
        'red': 1,
        'green': 2,
        'blue': 3,
        'orange': 4
    },
    
    'change_color_steps': 888,
    'start_color': 'blue',
    #'color_distance': 10.8,
    
    'pendown_pos': 0.7,
    'penup_pos': 0.5,
    'penup_sleep': 0.25,
    
    'pen_lazy_sleep': 0.05,
    'pen_stroke_width': 2,
    
    'led_sleep': 0.5,
    'status_leds': {
        'white': 20,
        'blue': 21
    },
    
    'simulator_window_height': default_height,
    'simulator_window_width': default_width,
    'name': 'Unknown',
#    'simulator_window_height': 600,
    'simulator_on': True,
    'simulator_start_speed': 0.1 # sleep per 1000 steps,
}
