import math
from simulator import EasterSimulator

def heart(ct: EasterSimulator, **config):
    old_pos = ct.xy_pos()
    w = config.get('heart_w')
    h = config.get('heart_h')
    t = config.get('heart_t', 2)
    turn = config.get('heart_turn', 0)
    r = w / 4
    res = config.get('heart_res', 32)
    sin_points = []
    circ_points = []

    turn_vec = math.cos(turn) + math.sin(turn) * 1j
    
    for x in range(res + 1):
        f = x / res
        sin_point =  f * h + math.sin(f * math.pi / 2) * w / 2 * 1j
        
        circ_alpha = (0.5 - f) * math.pi
        circ_point = (math.cos(circ_alpha) * t + math.sin(circ_alpha) * 1j) * r
        #print(f'heart {x}/{res} – circ_alpha={circ_alpha} circ_point={circ_point}')

        sin_points.append(sin_point)
        circ_points.append(circ_point)

    for s in sin_points: ct.step_to( s * turn_vec + old_pos)
    
    m = h + w / 4 * 1j
    for c in circ_points: ct.step_to((c + m) * turn_vec + old_pos)
    m -= w / 2 * 1j
    for c in circ_points: ct.step_to((c + m) * turn_vec + old_pos)

    sin_points.reverse()
    for s in sin_points: ct.step_to((s.real - s.imag * 1j) * turn_vec + old_pos)

    

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

    colors = config.get('circle_colors', [ct.current_color])
    colorindex = config.get('circle_colorindex', 0)
    fill = config.get('circle_fill', 0)
    res = config.get('circle_res', 32)
    
    pcenter = config.get('circle_center', 0)
    center = config.get('circle_center_coordinate', rad.real * pcenter.real + rad.imag * pcenter.imag * 1j + ct.xy_pos())

    ct.change_color(colors[colorindex])

    for a in range(res+1):
        alpha = a / res * 2 * math.pi
        delta = (math.cos(alpha) * rad.real + math.sin(alpha) * rad.imag * 1j)
        ct.step_to(delta + center, move=(a == 0))

    if fill > 0:
        substeps = config.get('circle_substeps', ct.xy_stroke_steps())
        rad -= substeps
        if rad.real > 0 and rad.imag > 0:
            new_config = dict(config)
            new_config.update({
                'circle_rad': rad,
                'circle_colorindex': (colorindex + 1) % len(colors),
                'circle_fill': fill - 1,
                'circle_center_coordinate': center
            })
            circle(ct, **new_config)

def flower(ct: EasterSimulator, **config):
    center = flower_curve(ct, **config)
    size = config.get('fcurve_size')

    dotwidth = size.real * config.get('dotsize', 0.4)
    dotrad = (dotwidth + dotwidth * (size.imag / size.real) * 1j) / 2

    ct.step_to(center + dotrad.real, move=True)

    print(f'dotrad={dotrad}')

    dotconfig = dict(config)
    dotconfig.update({ 'circle_rad': dotrad, 'circle_center': -1 })
    circle(ct, **dotconfig)

