import math
import random
import eastermath as em
from simulator import EasterSimulator

def curl(ct: EasterSimulator, **config):
    number = config.get('curl_number', 10)
    size = config.get('curl_size', 10)
    center = config.get('curl_center', 0)
    old_pos = ct.xy_pos() + em.cscalar(center, size)

    height_fac = config.get('curl_height_fac', 0.3)
    res = config.get('curl_res', 32)
    
    colors = config.get('curl_colors', [ct.current_color])

    for i in range(res * number):
        ct.change_color(colors[int(i/res/len(colors)) % len(colors)])
        alpha = i / res * math.pi * 2
        move_circ = math.cos(alpha) * size.real/2 + math.sin(alpha) * (size.imag/number) * height_fac * 1j
        move_way = i / res / number * size.imag * 1j
        ct.step_to(old_pos + move_circ + move_way, move=i == 0)

def heart(ct: EasterSimulator, **config):
    old_pos = ct.xy_pos()
    size = config.get('heart_size')
    t = config.get('heart_t', 0.3)
    parts = config.get('heart_parts', 4)
    turn = config.get('heart_turn', 0)
    fill = config.get('heart_fill', 0)
    onecirc = config.get('heart_onecirc', False)

    colors = config.get('heart_colors', [ct.current_color])
    colorindex = config.get('heart_colorindex', 0)

    goback = config.get('heart_goback', True)
    stretch = config.get('heart_stretch', 1 + 1j)

    #ct.log(f'color index {colorindex} length {len(colors)} colors {colors}', 10)
    
    circ_rad = size.imag / (2 if onecirc else 4)
    res = config.get('heart_res', 32)
    sin_points = []
    circ_points = []

    turn_vec = em.complex_rotate(turn)
    sin_width = (1-t) * size.real
    circ_width = t * size.real
    
    for x in range(res + 1):
        f = x / res
        sin_point =  f * sin_width + math.sin(f * math.pi / 2) * size.imag / 2 * 1j
        
        circ_alpha = (0.5 - f) * math.pi
        circ_point = math.cos(circ_alpha) * circ_width + math.sin(circ_alpha) * 1j * circ_rad
        #print(f'heart {x}/{res} – circ_alpha={circ_alpha} circ_point={circ_point}')

        sin_points.append(sin_point)
        circ_points.append(circ_point)

    ct.change_color(colors[colorindex])

    def transform(pos: complex): 
        return em.cscalar(pos * turn_vec, stretch)

    if parts >= 1:
        for s in sin_points:
            ct.step_to(transform(s) + old_pos)
    
    m = sin_width + (0 if onecirc else size.imag / 4) * 1j
    if parts >= 2:
        for c in circ_points: 
            ct.step_to(transform(c + m) + old_pos)

    if parts >= 3 and not onecirc:
        m -= size.imag / 2 * 1j
        for c in circ_points:
            ct.step_to(transform(c + m) + old_pos)

    sin_points.reverse()
    if parts >= 4: 
        for s in sin_points: 
            ct.step_to(transform(s.real - s.imag * 1j) + old_pos)

    ct.step_to(old_pos)

    if fill > 0:
        subsize = config.get('heart_subsize', ct.xy_stroke_steps())
        #subsize = em.cscalar(subsize, stretch)
        halffill = config.get('heart_halffill', -1)
        minsize = config.get('heart_minsize', subsize)
        newsize = size - subsize

        if em.complex_bigger(newsize, minsize):
            old_pos = ct.xy_pos()
            #ct.step_to(subsize.real / 2 * turn_vec, rel=True)
            new_config = dict(config)
            new_config.update({
                'heart_size': newsize,
                'heart_fill': fill - 1,
                'heart_parts': 2 if fill <= halffill else 4,
                'heart_colors': colors,
                'heart_colorindex': (colorindex + 1) % len(colors)
            })
            heart(ct, **new_config)
            if goback: ct.step_to(old_pos)
    

def flower_curve(ct: EasterSimulator, **config):
    size = config.get('fcurve_size')
    res = config.get('fcurve_res', 128)
    leaves = config.get('fcurve_leaves', 10)
    rmin = config.get('fcurve_rmin', 0.2)
    rmax = config.get('fcurve_rmax', 1)
    
    pcenter = config.get('fcurve_center', 0)
    center = config.get('fcurve_center_coordinate', size.real * pcenter.real + size.imag * pcenter.imag * 1j + ct.xy_pos())
    
    fill = config.get('fcurve_fill', 0)
    colors = config.get('fcurve_colors', [ct.current_color])
    colorindex = config.get('fcurve_colorindex', 0)
    smalleave = config.get('fcurve_small_leave', 1)

    ct.change_color(colors[colorindex])

    for a in range(res + 1):
        alpha = a / res * 2 * math.pi
        r = rmin + math.sin(alpha * leaves) * (rmax - rmin)# * (smalleave if a % 2 == 0 else 1)
        delta = r * (size.real * math.cos(alpha) + size.imag * math.sin(alpha) * 1j)
        #print(f'flower step {a} of {res}: alpha={alpha} r={r} delta={delta}')
        ct.step_to(delta + center, move=(a == 0))

    if fill > 0:
        subsize = config.get('fcurve_subsize', 0.9)
        newsize = size * subsize

        print(f'flower fill {fill} rmax {rmax}')
        if newsize.real > 0 and newsize.imag > 0:
            new_config = dict(config)
            new_config.update({
                'fcurve_rmax': rmax,
                'fcurve_rmin': rmin,
                'fcurve_colorindex': (colorindex + 1) % len(colors),
                'fcurve_fill': fill - 1,
                'fcurve_size': newsize,
                'fcurve_center_coordinate': center
            })
            flower_curve(ct, **new_config)
    print(f'flower finish {fill}')

    return center

def circle(ct: EasterSimulator, **config):
    rad = config.get('circle_rad')
    move = config.get('circle_move', False)

    colors = config.get('circle_colors', [ct.current_color])
    colorindex = config.get('circle_colorindex', 0)
    fill = config.get('circle_fill', 0)
    res = config.get('circle_res', 32)
    circle_angleadd = config.get('circle_angleadd', 0)
    
    pcenter = config.get('circle_center', 0)
    center = config.get(
        'circle_center_coordinate', 
        ct.xy_pos()
          + rad.real * pcenter.real
            + rad.imag * pcenter.imag * 1j
    )

    move_back = config.get('circle_move_back', True)

    end_pos: complex

    for a in range(res+1):
        alpha = a / res * 2 * math.pi + circle_angleadd
        delta = (math.cos(alpha) * rad.real + math.sin(alpha) * rad.imag * 1j)
        end_pos = delta + center
        ct.step_to(end_pos, move=(move and a == 0), color=colors[colorindex])

    if fill > 0:
        substeps = config.get('circle_substeps', ct.xy_stroke_steps())
        rad -= substeps
        if rad.real > 0 and rad.imag > 0:
            new_config = dict(config)
            new_config.update({
                'circle_rad': rad,
                'circle_colorindex': (colorindex + 1) % len(colors),
                'circle_fill': fill - 1,
                'circle_center_coordinate': center,
                'circle_move': False
            })
            circle(ct, **new_config)
        if move_back: ct.step_to(end_pos)

def flower(ct: EasterSimulator, **config):
    center = flower_curve(ct, **config)
    size = config.get('fcurve_size')

    dotwidth = size.real * config.get('dotsize', 0.4)
    dotrad = (dotwidth + dotwidth * (size.imag / size.real) * 1j) / 2

    ct.step_to(center + dotrad.real, move=True)

    dotconfig = dict(config)
    dotconfig.update({ 'circle_rad': dotrad, 'circle_center': -1 })
    circle(ct, **dotconfig)

def spiral(ct: EasterSimulator, **config):
    center  = config.get('spiral_center', ct.xy_pos())

    angle  = config.get('spiral_start_angle', 0)
    mirror  = config.get('spiral_mirror', 1 + 1j)
    max_angle = config.get('spiral_max_angle', 8 * math.pi)
    min_angle = config.get('spiral_min_angle', angle)

    radius_increase = config.get('spiral_radius_increase', 1 + 1j)
    angle_increase = config.get('spiral_angle_increase', math.pi / 8)
    radius = 0

    while angle >= min_angle and angle <= max_angle:
        radius = angle * radius_increase
        delta = math.sin(angle) * radius.real * mirror.real + math.cos(angle) * radius.imag * mirror.imag * 1j
        #print(f'spiral delta={delta} angle={180/math.pi * angle} max_angle={180/math.pi * max_angle} angle_increase={180/math.pi * angle_increase}')
        ct.step_to(center + delta)

        angle += angle_increase

    return radius


def rose(ct: EasterSimulator, **config):
    center  = config.get('rose_center', ct.xy_pos())

    angle  = config.get('rose_start_angle', 0)
    max_angle = config.get('rose_max_angle', 8 * math.pi)

    radius_increase = config.get('rose_radius_increase', 1 + 1j)
    angle_increase = config.get('rose_angle_increase', math.pi / 32)
    hill_number = config.get('rose_hill_number', 1) # for angle = pi
    hill_size = config.get('rose_hill_size', 0.3)
    radius = 0

    while angle <= max_angle:
        hn = int(angle * hill_number / math.pi)
        radius_fac = em.hill_sin(angle * hn)
        radius = angle * radius_increase * (1 - hill_size + radius_fac * hill_size)
        delta = math.cos(angle) * radius.real + math.sin(angle) * radius.imag * 1j
        ct.step_to(center + delta)

        angle += angle_increase

    return radius

letters = {
    'S': [ 1, 0, 0.5j, 1+0.5j, 1+1j, 1j ],
    'C': [ 1, 0, 1j, 1+1j ],
    'H': [ 0, 1j, 0.5j, 1+0.5j, 1, 1+1j ],
    'U': [ 0, 1j, 1+1j, 1 ],
    'L': [ 0, 1j, 1+1j ],
    'K': [ 0, 1j, 0.5j, 1, 0.5j, 1+1j ],
    'N': [ 1j, 0, 1+1j, 1 ],
    'T': [ 0, 1, 0.5, 0.5+1j ]
}

def drawLetter(
        l: str, 
        ct: EasterSimulator, 
        pos: complex, 
        size: complex, 
        rotate: complex, 
        color: str,
        boldness: int,
        boldoff: complex
    ):
    for b in range(boldness):
        move = True
        for p in letters[l]:
            off = (p.real*size.real + p.imag*size.imag * 1j) + boldoff*b
            ct.step_to(pos + off*rotate, move=move, color=color)
            move = False

def drawString(ct: EasterSimulator, **config):
    text = config.get('text')
    size = config.get('size')
    pos = config.get('pos')
    colors = config.get('colors', [ct.current_color])
    distance = config.get('dis', 1.8)
    firstletter = config.get('fl', 1.4)
    randturn = config.get('randturn', math.pi/40)
    randy = config.get('randy', 200)
    randsize = config.get('randsize', 0.1)
    rotate = em.complex_rotate(config.get('turn', 0))
    boldness = config.get('bold', 3)
    randcolor = config.get('randcolor', False)
    boldoff = config.get('boldoff', ct.xy_stroke_steps())
    i = 0
    xpos = 0
    for letter in text:
        print(f'draw letter {letter} on {xpos + pos.imag*1j}')
        own_size = (firstletter if i == 0 else 1) * size * (random.random()*2*randsize - randsize + 1)
        yoff = (size.imag - own_size.imag + random.random()*randy*2 - randy) * 1j
        rot = rotate * em.complex_rotate((random.random()*randturn*2 - randturn))
        drawLetter(
            letter, ct, 
            (xpos + yoff)*rotate + pos, 
            own_size, rot,
            colors[int(len(colors)*random.random()) if randcolor else i % len(colors)],
            boldness,
            boldoff
        )
        xpos += own_size.real * distance
        i += 1