import eastermath as em
import tkinter
import threading
import time

class EasterCanvas:
    def __init__(self, config: dict):
        self.config = config
        
        self.width  = self.config['simulator_window_width']
        self.height = self.config['simulator_window_height']
        self.stroke_width = self.config['pen_stroke_width'] * 4
        
        self.pen_pos = (0,0)
        self.grid_fill = '#333'
        
        self.initialize()
        
    def initialize(self):
        self.window = tkinter.Tk()
        self.window.title('Easter Simulator')
        self.window.config(bg='#345')
        
        self.canvas = tkinter.Canvas(
            self.window,
            height=self.height,
            width=self.width,
            bg="#fff"
        )
        self.clear()
        self.canvas.pack()
        
        self.set_color('black')
        
    def main_loop(self): self.window.mainloop()
    
    def y_on_grid(self, y: float): return (1 - y) * self.height
    def x_on_grid(self, x: float): return (x * (self.config['egg_use_percent']/100) + 0.5) * self.width
        
    def clear(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#eee")
        
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
                width=2 if yrow == 0 else 1, fill='#000'
            )
            self.canvas.create_text(
                (left_edge, ypos), 
                text=f'{yrow * 10}%  ',
                fill=self.grid_fill, 
                anchor=anchor
            )
            
    def paint_color(self):
        size = 30
        offset = 10
        
        i = 0
        for color in self.config['color_pos']:
            xpos = offset
            ypos = (offset + size) * i + offset
            hex_color = em.color_to_hex(color)
            self.canvas.create_rectangle(
                xpos, ypos, 
                xpos + size, ypos + size,
                fill=hex_color,
                outline=hex_color if self.pen_color == hex_color else '#fff',
                width=10
            )
            i += 1
            
            self.canvas.update()
        
    def set_color(self, color: str):
        self.pen_color = em.color_to_hex(color)
        self.paint_color()
        
    def quit(self): self.window.quit()
    
    def go_to(self, deltapos: (float, float), move: bool):
        (xpen, ypen) = self.pen_pos
        px = xpen + deltapos[0]
        py = ypen + deltapos[1]
    
        if move:
            self.pen_pos = (px, py)
            print('moving!')
            
        else:
            self.canvas.create_line(
                (xpen + 0.5) * self.width, self.y_on_grid(ypen),
                (px   + 0.5) * self.width, self.y_on_grid(py), 
                fill=self.pen_color, width=self.stroke_width
            )
        
            if py > 1 or py < 0:
                yadd = 1 if py < 0 else -1
                self.pen_pos = (xpen, ypen + yadd)
                self.go_to(deltapos, False)
                
            else:
                self.pen_pos = (px, py)
                self.canvas.update()
