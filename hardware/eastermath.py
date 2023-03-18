from dataclasses import dataclass

def modulo(pn, z):
	n = pn
	while n > z: n -= z
	while n < 0: n += z
	return n

@dataclass
class EasterPos:
	x: float
	y: float
	
	def __add__(self, that: EasterPos): return EasterPos(self.x + that.x, self.y + that.y)
	def __neg__(self): return EasterPos(-self.x, -self.y)
	def __mul__(self, f: float): return EasterPos(self.x * f, self.y * f)
	def __str__(self): return f'({x}|{y})'