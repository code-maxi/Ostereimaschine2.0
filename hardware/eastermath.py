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

def rainbow_colors(l: int): return ['red']*l + ['orange']*l + ['green']*l + ['blue']*l + ['black']*l
