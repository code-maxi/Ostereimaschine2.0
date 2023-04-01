#from screeninfo import get_monitors
import traceback
import eastermath as em
import tkinter
import tkinter.font
import threading
import time
import math

class EasterCanvas:
    def __init__(self, config: dict, onclose):
        self.config = config
        
        self.height  = self.config['simulator_window_height']
        self.width   = self.config['simulator_window_width']
        self.eggwidth   = self.config.get('simulator_egg_width', None)

        if self.eggwidth == None: 
            self.eggwidth = round(self.config['egg_length'] / (self.config['egg_height'] * math.pi) * self.height)
        
        self.stroke_width = self.config['pen_stroke_width'] * 4 * 2
        
        self.pen_pos = 0j
        self.grid_fill = '#333'
        self.background = '#ddd'
        self.onclose = onclose
        self.info = {}
        self.fullscreen = not self.config.get('start_fullscreen', True)
        self.infotext = None
        
        self.initialize()
        
    def close_me(self):
        self.onclose()
        self.window.destroy()
        exit(0)
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        print('fullscreen toggled')
        self.window.attributes("-fullscreen", self.fullscreen)
        
    def initialize(self):
        self.window = tkinter.Tk()
        self.window.title(f'Easter Simulator – {self.config.get("name", "NONAME")}')
        self.window.config(bg='#345')
        self.window.attributes("-topmost", True)
        self.toggle_fullscreen()
        
        self.canvas = tkinter.Canvas(
            self.window,
            height=self.height,
            width=self.width,
            bg="#fff"
        )
        self.window.protocol("WM_DELETE_WINDOW", self.close_me)
        self.window.bind('<Control-e>', lambda event: self.close_me())
        self.window.bind('<Control-f>', lambda event: self.toggle_fullscreen())

        self.set_color(self.config['start_color'])
        self.paint_all()
        
        self.canvas.pack()
        
    def main_loop(self): self.window.mainloop()

    def pos_on_grid(self, pos: complex):
        xpos = pos.real * (self.config['egg_use_percent']/100) * self.eggwidth + self.width / 2
        ypos = (1 - pos.imag) * self.height
        return xpos + ypos * 1j
        
    def clear(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.background)
        self.canvas.create_rectangle((self.width - self.eggwidth)/2, 0, (self.width + self.eggwidth)/2, self.height, fill='#fff', width=0)
    
    def paint_all(self):
        self.clear_grid()
        self.paint_color()
        self.paint_info()
        
    def clear_grid(self):
        self.clear()
        
        for xrow in range(-5, 6):
            pos = xrow / 10
            xpos = self.pos_on_grid(pos)
            #print(f'pos {pos} real {xpos.real} img {xpos.imag} xpos {xpos}')

            self.canvas.create_line(xpos.real, 0, xpos.real, self.height, width=2 if xrow == 0 else 1, fill='#000')
            self.canvas.create_text(xpos.real, 0, text=f'  {xrow*10}% ', fill=self.grid_fill, anchor='nw')
            
        left_edge = self.pos_on_grid(-0.5).real
        right_edge = self.pos_on_grid(0.5).real
        
        for yrow in range(0, 11):
            ypos = self.pos_on_grid(yrow/10 * 1j)

            anchor = 'se' if yrow == 0 else ('ne' if yrow == 10 else 'e')
            self.canvas.create_line(
                left_edge, ypos.imag,
                right_edge, ypos.imag,  
                width=3 if yrow == 0 else 1, fill='#000'
            )
            self.canvas.create_text(
                (left_edge, ypos.imag), 
                text=f'{yrow * 10}%  ',
                fill=self.grid_fill, 
                anchor=anchor
            )
            
            
    def info_text(self, text):
        self.infotext = text
        
        padding = 5
        font_size = 13
        text = str(self.infotext)
        self.paint_text_box(
            text=text, padding=padding,
            fontsize=font_size, x=self.width/2, y=self.height/2,
            fill='#fff'
        )
            
    def paint_color(self):
        size = 30
        offset = 10
        
        for color in self.config['color_pos']:
            colorpos = self.config['color_pos'][color]
            if colorpos != None:
                i = len(self.config['color_pos']) - 1 - colorpos
                xpos = offset
                ypos = (offset + size) * i + offset
                hex_color = em.color_to_hex(color)
                self.canvas.create_rectangle(
                    xpos, ypos, 
                    xpos + size, ypos + size,
                    fill=hex_color,
                    outline=hex_color if self.pen_color == hex_color and hex_color != None else '#fff',
                    width=10
                )
                
    def paint_text_box(self, **kwargs):
        padding = kwargs.get('padding', 10)

        fontsize = kwargs.get('size', 12)
        lines = kwargs.get('text', 'Lorem\n ipsum.').split('\n')

        spacing = kwargs.get('spacing', 8)
        font = tkinter.font.Font(size=fontsize, family="monospace")
        outline = kwargs.get('outline', '#000')
        
        boxw = max([font.measure(s) for s in lines])
        boxh = 2*padding - spacing + (fontsize + spacing) * len(lines)
        
        boxx = kwargs.get('x', 5) - kwargs.get('w', 0.5) * boxw
        boxy = kwargs.get('y', 5) - kwargs.get('h', 0.5) * boxh
        
        self.canvas.create_rectangle(
            boxx, boxy,
            boxx + boxw,
            boxy + boxh,
            fill=kwargs.get('fill', self.background),
            outline= outline,
            width=1
        )
        
        for line in lines:
            self.canvas.create_text(
                boxx, boxy,
                text=line,
                fill=kwargs.get('textcolor', '#000'),
                font=font,
                anchor='nw'
            )
            boxy += fontsize + spacing
            
        return (boxw, boxh)
            
    def paint_info(self):
        spacing = 10
        font_size = 10
        lines = self.info.values()
        
        try:
            self.canvas.create_rectangle(
                self.width - self.info_size[0],
                self.height - self.info_size[1],
                self.width, self.height,
                fill=self.background, width=0
            )
        except AttributeError: pass
        
        #print(f'text_widths {text_widths} | max_width {max_width} | max_height {max_height}')
        
        self.info_size = self.paint_text_box(
            text = '\n'.join(lines), 
            x=self.width, y=self.height,
            w=1, h=1, fontsize=font_size,
            outline=self.background
        )
            
    def set_color(self, color):
        #print(f'canvas change color to {color}')
        self.pen_color = em.color_to_hex(color)
        self.info.update({
            'color': f'color = {color if color != None else "–"}',
            'pen':   f'pen   = {"down" if color != None else "up"}'
        })
        self.paint_color()
        self.paint_info()
        
    def update_info(self, info: dict):
        self.info.update(info)
        self.paint_info()
        
    def quit(self): self.window.quit()
    
    def go_to(self, deltapos: complex, move: bool, info: dict, paint_info: bool):
        if abs(deltapos) > 0:
            self.info.update(info)
            
            new_pos = self.pen_pos + deltapos
            
            display_penpos = self.pos_on_grid(self.pen_pos)
            display_newpos = self.pos_on_grid(new_pos)
        
            if move:
                #print('move')
                self.canvas.create_rectangle(
                    display_newpos.real - self.stroke_width / 2, display_newpos.imag - self.stroke_width / 2,
                    display_newpos.real + self.stroke_width / 2, display_newpos.imag + self.stroke_width / 2, 
                    fill=self.pen_color
                )
                self.pen_pos = new_pos
                
            else:
                self.canvas.create_line(
                    display_penpos.real, display_penpos.imag, 
                    display_newpos.real, display_newpos.imag,
                    fill=self.pen_color, width=self.stroke_width
                )
            
                if new_pos.imag > 1 or new_pos.imag < 0:
                    self.pen_pos += 1j if new_pos.imag < 0 else -1j
                    self.go_to(deltapos, False, info, paint_info)
                    
                else:
                    self.pen_pos = new_pos
                    if paint_info: self.paint_info()
                    self.canvas.update()
         
         
         
'''
pos1 = ((xpen + 0.5) * self.width, self.y_on_grid(ypen))
pos2 = ((px + 0.5) * self.width, self.y_on_grid(py))
delta = em.vec_sub(pos2, pos1)
length = em.vec_len(delta)
pos3 = em.vec_add(em.vec_mul(delta, (length - self.stroke_width) / length), pos1)

self.canvas.create_line(
    pos1[0], pos1[1], pos2[0], pos2[1], 
    fill='#f00', width=self.stroke_width
)
self.canvas.create_line(
    pos1[0], pos1[1], pos3[0], pos3[1],
    fill=self.pen_color, width=self.stroke_width
)
'''
