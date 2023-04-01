from simulator import EasterSimulator
import eastermath as em
import shapes
import time
import math
import shapes
import random

def act(ct: EasterSimulator):
    music_lines = 6
    music_distance = round(ct.egg_border_steps * 0.4 / music_lines)
    music_x_offset = - (music_lines-1) * music_distance / 2 * 1.2
    
    note_number = 12
    note_distance = round(ct.egg_y_steps / note_number) * 1j

    note_dot_width = music_distance/2 * 1.5
    note_dot_rad = note_dot_width + ct.x_to_ysteps(note_dot_width * 1.2)
    note_stem_length = ct.egg_border_steps * 0.3
    note_beam_width = 5
    small_dot_distance = - note_dot_rad * 0.8
    small_dot_width = 70
    
    colors = ['red', 'green', 'blue']

    def random_height(): return random.randrange((music_lines-1) * 2) / 2

    def music_dot(value):
        shapes.circle(
            ct,
            circle_rad = note_dot_rad,
            circle_fill = 100 if value <= 1/4 else 0,
            circle_center = 1j,
            circle_angleadd = -math.pi / 2,
            circle_res = 8
        )

    def lines():
        ct.change_color('black')
        for i in range(music_lines):
            yr = i * music_distance + music_x_offset
            ct.step_to(yr, move=True)
            ct.step_to(0, rel=True, long=True)

    def notes():
        y = 0j
        while y.imag < ct.egg_y_steps - note_distance.imag:
            value = em.random_item([ 1/8, 1/8, 1/4, 1/2, 1/4, 1/2, 3/8, 3/4 ]) #
            color = em.random_item(colors)
            height = random_height()
            x = height * music_distance + music_x_offset

            ct.change_color(color, stay_up=True)
            ct.step_to(x + y, move=True)
            music_dot(value)

            if value == 3/8 or value == 3/4:
                ct.step_to(small_dot_distance, move=True, rel=True)
                shapes.circle(
                    ct,
                    circle_rad = small_dot_width + ct.x_to_ysteps(small_dot_width),
                    circle_res = 8
                )
                ct.step_to(x + y, move=True)

            #ct.step_to(x + y)

            ct.step_to((1 if value > 1/8 else 0.6) * note_stem_length, rel=True)
            y += note_distance

            if value == 1/8 and y.imag < ct.egg_y_steps - 2*note_distance.imag:
                x2 = random_height() * music_distance + music_x_offset
                delta = (x2 - x) + note_distance

                smaller = ct.x_stroke_steps / 2
                for i in range(note_beam_width):
                    ct.step_to(smaller, rel=True)
                    ct.step_to(delta * (1 if i % 2 == 0 else -1), rel=True)
                
                ct.step_to(-note_beam_width * smaller - note_stem_length, rel=True)

                music_dot(value)

                y += note_distance
    #lines()
    notes()

#from controller import EasterControler
sim = EasterSimulator(
    {
        'simulator_start_speed': 0,
        'start_color': 'green',
        'penup_offset': 0.25,
        'color_pos': {
            'black': 0,
            'red': 1,
            'green': 2,
            'blue': 3,
            'orange': None
        },
        #'simulator_window_width': None,
        'name': 'Musiknoten'
    }
)
sim.run(act=act, gui=True, console=True)
