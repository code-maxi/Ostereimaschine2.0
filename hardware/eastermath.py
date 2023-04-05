import re
import random
import os
from xml.dom import minidom
import math

def modulo(pn: complex, z: complex):
    n = pn
    while n >= z: n -= z
    while n < 0: n += z
    return n
    
def abs_minmax(n1: float, n2: float):
    maxRes = n1
    minRes = n2
    if abs(n2) > abs(n1):
        maxRes = n2
        minRes = n1
    return (minRes, maxRes)

def complex_bigger(z1: complex, z2: complex): return z1.real > z2.real and z1.imag > z2.imag
    
def get_save(array: list, i: int, *arr):
    none = arr[0] if len(arr) > 0 else None
    return array[i] if i < len(array) else none
    
def egg_form(x: float): return 1 + (((-x)**2.43) * -0.46 if x < 0 else -0.575 * (x**2.1)) / 0.75

def egg_caliber(xpercent: float, max_caliber: float):
    fac = xpercent/50
    radius = egg_form(fac) * max_caliber
    return radius

def in_range(n: float, minmax: complex): return n >= minmax.real and n <= minmax.imag
    
def direction(n: float): return -1 if n < 0 else (0 if n == 0 else 1)

def rainbow_colors(l: int): 
    return ['red']*l + ['orange']*l + ['green']*l + ['blue']*l + ['black']*l
    
def color_to_hex(color):
    res = None
    if   color == 'black': res = '#000'
    elif color == 'red': res = '#f00'
    elif color == 'green': res = '#008000'
    elif color == 'blue': res = '#00f'
    elif color == 'orange': res = '#ffa500'
    elif color == 'purple': res = '#800080'
    elif color == 'yellow': res = '#ffff00'
    return res

def round_complex(z: complex, *args):
    digits = get_save(args, 0, 0)
    return round(z.real, digits) + round(z.imag, digits) * 1j

def comlpex_scalar(x: complex, y: complex): return x.real * y.real + x.imag * y.imag * 1j

def relative_path(path: str):
    absolute = os.path.realpath(__file__).split('/')
    absolute.pop()
    return '/'.join(absolute) + '/' + path

def random_item(array: list): return array[random.randrange(0, len(array))]

class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"

'''

def vec_add(v1, v2): return (v1[0] + v2[0], v1[1] + v2[1])
def vec_sub(v1, v2): return (v1[0] - v2[0], v1[1] - v2[1])
def vec_neg(v1): return (-v1[0], -v1[1])
def vec_mul(v1, s): return (v1[0] * s, v1[1] * s)
def vec_len(v1): return math.sqrt(v1[0] ** 2 + v1[1] ** 2)
def vec_max(v1): return max(v1[0], v1[1])
def vec_zero(v1): return v1[0] == 0 and v1[1] == 0

def read_svg(file: str):
    doc = minidom.parse(file)
    command = ''
    
    paths = [ path.getAttribute('d').split(' ') for path in doc.getElementsByTagName('path') ]
    coordinates = [[]]
    
    for path in paths:
        for item in path:
            try:
                pos = [ float(coordinate) for coordinate in item.split(',') ]
                lastcoord = get_save(-1, coordinates)
                if lastcoord != None:
                    if command == 'h': coordinates.append((lastcoord[0] + pos[0], lastcoord[1]))
                    if command == 'v': coordinates.append((lastcoord[0], lastcoord[1] + pos[0]))
                    
                
            except:
                if path.lower() == 'z':
                    firstcoord = get_save(coordinates, 0)
                    if firstcoord != None: coordinates.append(firstcoord)
                else: command = path
            

read_svg(relative_path('images/inkscape-test.svg'))


command = r'\b[a-zA-Z]\b'
path_commands = [ [ found.replace(' ', '') for found in re.findall(command, path_string) ] for path_string in path_strings]
    
path_coordinates = [ [ found.strip().split(' ') for found in re.split(command, path_string) ] for path_string in path_strings ]
path_coordinates = [ list(filter(lambda pc: len(pc) > 0, pcl)) for pcl in path_coordinates ]

print('\n\n'.join(path_strings))
print()
print(path_commands)
print()
print(path_coordinates)
print()
print('\n\n\n'.join([ '\n\n'.join(pc) for pc in path_coordinates ]))

'''
