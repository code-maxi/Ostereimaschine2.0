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
        'startPos': 1
    },
    
    'egg_length': 58.5,
    'egg_height': 41,
    'egg_use_percent': 70,
    
    'max_stepper_speed': 0.002,
    
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
    
    'penup_offset': 0.5,
    'penup_sleep': 0.5,
    
    'pen_lazy': 25,
    'pen_lazy_sleep': 0.05,
    'pen_stroke_width': 1,
    
    'simulator_window_width': 1200,
#    'simulator_window_height': 600,
    'simulator_on': True,
    'simulator_start_speed': 0.1 # sleep per 1000 steps
}
