import math

def modulo(pn: float, z: float):
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
    
def get_save(array: list, i: int, *arr):
    none = arr[0] if len(arr) > 0 else None
    return array[i] if i < len(array) else none
    
def egg_form(x: float): return 1 + (((-x)**2.43) * -0.46 if x < 0 else -0.575 * (x**2.1)) / 0.75

def egg_caliber(xpercent: float, max_caliber: float):
    fac = xpercent/50
    radius = egg_form(fac) * max_caliber
    return radius
    
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
    return res
    
def vec_add(v1, v2): return (v1[0] + v2[0], v1[1] + v2[1])
def vec_sub(v1, v2): return (v1[0] - v2[0], v1[1] - v2[1])
def vec_neg(v1): return (-v1[0], -v1[1])
def vec_mul(v1, s): return (v1[0] * s, v1[1] * s)
def vec_len(v1): return math.sqrt(v1[0] ** 2 + v1[1] ** 2)
def vec_max(v1): return max(v1[0], v1[1])
def vec_zero(v1): return v1[0] == 0 and v1[1] == 0
