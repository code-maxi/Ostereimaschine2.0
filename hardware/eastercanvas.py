from screeninfo import get_monitors
import eastermath as em
import tkinter
import tkinter.font
import threading
import time

class EasterCanvas:
    def __init__(self, config: dict, onclose):
        self.config = config
        
        self.height  = self.config['simulator_window_height']
        self.width  = self.config['simulator_window_width']
        
        self.stroke_width = self.config['pen_stroke_width'] * 4 * 2
        
        self.pen_pos = (0,0)
        self.grid_fill = '#333'
        self.background = '#eee'
        self.onclose = onclose
        self.info = {}
        self.fullscreen = True
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
        self.window.title('Easter Simulator')
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
        self.window.bind('<Control-e>', lambda event: self.toggle_fullscreen())

        self.clear_grid()
        self.canvas.pack()
        
        self.set_color(self.config['start_color'])
        
    def main_loop(self): self.window.mainloop()
    
    def y_on_grid(self, y: float): return (1 - y) * self.height
    def x_on_grid(self, x: float): return (x * (self.config['egg_use_percent']/100) + 0.5) * self.width
        
        
    def clear(self): self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.background)
        
    def clear_grid(self):
        self.clear()
        
        for xrow in range(-5, 6):
            xpos = self.x_on_grid(xrow / 10) 
            self.canvas.create_line(xpos, 0, xpos, self.height, width=2 if xrow == 0 else 1, fill='#000')
            self.canvas.create_text((xpos, 0), text=f'  {xrow*10}% ', fill=self.grid_fill, anchor='nw')
            
        left_edge = self.x_on_grid(-0.5)
        right_edge = self.x_on_grid(0.5)
        for yrow in range(0, 11):
            ypos = self.y_on_grid(yrow/10)
            anchor = 'se' if yrow == 0 else ('ne' if yrow == 10 else 'e')
            self.canvas.create_line(
                left_edge, ypos,
                right_edge, ypos,  
                width=3 if yrow == 0 else 1, fill='#000'
            )
            self.canvas.create_text(
                (left_edge, ypos), 
                text=f'{yrow * 10}%  ',
                fill=self.grid_fill, 
                anchor=anchor
            )
            
        if self.infotext != None:
            self.canvas.create_text(
                self.width / 2, self.height / 2,
                text=str(self.infotext),
                fill='#000',
                anchor='n'
            )
            
    def info_text(self, text):
        print('info text')
        self.infotext = text
        self.clear_grid()
        self.paint_color()
        self.paint_info()
            
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
            
    def paint_info(self):
        spacing = 10
        font_size = 10
        lines = self.info.values()
        
        font = tkinter.font.Font(size=font_size, family="monospace")
        text_widths = [font.measure(s) for s in lines]
        
        def clear_info(c):
            c.canvas.create_rectangle(
                c.info_xpos, c.info_ypos,
                c.info_xpos + c.info_max_width,
                c.info_ypos + c.info_max_height,
                fill=c.background, width=0
            )
        
        try: clear_info(self)
        except AttributeError: pass
        
        self.info_max_width = max(text_widths)
        self.info_max_height = (font_size + spacing) * len(lines)
        
        #print(f'text_widths {text_widths} | max_width {max_width} | max_height {max_height}')
        
        self.info_xpos = self.width - self.info_max_width
        self.info_ypos = self.height - self.info_max_height
        
        clear_info(self)
        
        for line in lines:
            self.canvas.create_text(
                self.info_xpos, self.info_ypos,
                text=line,
                fill='#000',
                font=font,
                anchor='nw'
            )
            self.info_ypos += font_size + spacing
            
    def set_color(self, color):
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
    
    def go_to(self, deltapos: (float, float), move: bool, info: dict, paint_info: bool):
        self.info.update(info)
        
        (xpen, ypen) = self.pen_pos
        px = xpen + deltapos[0]
        py = ypen + deltapos[1]
    
        if move: self.pen_pos = (px, py)
            
        else:
            self.canvas.create_line(
                (xpen + 0.5) * self.width, self.y_on_grid(ypen),
                (px   + 0.5) * self.width, self.y_on_grid(py), 
                fill=self.pen_color, width=self.stroke_width
            )
        
            if py > 1 or py < 0:
                yadd = 1 if py < 0 else -1
                self.pen_pos = (xpen, ypen + yadd)
                self.go_to(deltapos, False, info, paint_info)
                
            else:
                self.pen_pos = (px, py)
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
