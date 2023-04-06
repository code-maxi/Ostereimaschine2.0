from eastercanvas import EasterCanvas
import eastermath as em
import shapes
import math
import shapes

def act(ct: EasterCanvas):
    flower_number = 8
    flower_width = ct.egg_x_steps * 0.2
    flower_leave_height = flower_width / 3 * 1j
    flower_fill = 3
    flower_halffill = flower_fill
    flower_xpos = 0

    lucky_clover_colors = ['black'] + ['green'] * 100

    def lucky_clover(global_rotate: float):
        for angle in [0, math.pi / 2, math.pi, math.pi / 2 * 3]:
            turn = angle + global_rotate
            size = flower_width/2 + flower_leave_height
            shapes.heart(
                ct,
                heart_size = size,
                heart_turn = turn,
                heart_fill = flower_fill,
                heart_halffill = flower_halffill,
                heart_colors = lucky_clover_colors
            )

    def flowers():
        for f in range(1):
            ypos = f / flower_number * ct.egg_y_steps * 1j
            ct.step_to(flower_xpos + ypos, move=True)
            lucky_clover(0)

    flowers()


sim = EasterCanvas(
    {
        'egg_use_percent': 65,
        'simulator_start_speed': 0.5,
        'start_color': 'green',
        'penup_offset': 0.25,
        'color_pos': {
            'purple': 0,
            'blue': 1,
            'green': 2,
            'orange': 3,
            'red': 4
        },
        'name': 'Glücksklee',
        'start_fullscreen': False
    }
)
sim.run(act=act, gui=True, console=True, direct_run=True)