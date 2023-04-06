#from screeninfo import get_monitors
import traceback
import eastermath as em
import tkinter
import tkinter.font
import threading
import time
import math
import simulator

class EasterCanvas(simulator.EasterSimulator):
    def __init__(self, config: dict):
        super().__init__(config)
        
    def log_name(self): return 'EasterCanvas'

    def initialize(self):
        super().initialize()

        self.window_height  = self.config['simulator_window_height']
        self.window_width   = self.config['simulator_window_width']
        self.window_eggwidth   = self.config.get('simulator_egg_width', None)

        if self.window_eggwidth == None: 
            self.window_eggwidth = round(self.config['egg_length'] / (self.config['egg_height'] * math.pi) * self.window_height)
        
        self.stroke_width = self.config['pen_stroke_width'] * 3
        
        self.grid_fill = '#333'
        self.background = '#ddd'
        self.info = {}
        self.fullscreen = not self.config.get('start_fullscreen', True)
        self.infotext = None

        self.window = tkinter.Tk()
        self.window.title(f'Easter Simulator – {self.config.get("name", "NONAME")}')
        self.window.config(bg='#345')
        self.window.attributes("-topmost", True)
        self.toggle_fullscreen()
        
        self.canvas = tkinter.Canvas(
            self.window,
            height=self.window_height,
            width=self.window_width,
            bg="#fff"
        )
        self.window.protocol("WM_DELETE_WINDOW", self.escape)
        self.window.bind('<Control-e>', lambda _: self.escape())
        self.window.bind('<Control-f>', lambda _: self.toggle_fullscreen())
        self.window.bind('<Control-r>', lambda _: self.repeat_act_event.set())

        self.paint_all()        
        self.canvas.pack()

        self.update_info({'egg_name': 'Drucke "'+self.config['name']+'"'})

        self.log('Canvas __init__.', 10)
        
    def escape(self):
        self.log('Canvas EXIT', 10)
        self.window.destroy()
        super().escape()

    def hide_color(self, color: str):
        super().hide_color(color)
        self.paint_color()

    def update_color(self, cp, np):
        super().update_color(cp, np)
        '''
        self.info.update({
            'color': f'color = {color if color != None else "–"}',
            'pen':   f'pen   = {"down" if color != None else "up"}'
        })
        self.paint_info()
        '''
        self.paint_color()

    def set_status_state(self, state: int, **kwargs):
        super().set_status_state(state)
        infotext = 'PAUSED'
        pause = kwargs.get('pause', False)

        if state == 0:
            infotext = 'ADJUSTING'
            if not pause: self.paint_all()
            self.info_text(self.adjust_text)

        elif state == 1: 
            infotext = 'RUNNING'
            if not pause: self.paint_all()

        elif state == 2:
            infotext = 'FINISHED'
            if not self.direct_run: self.info_text(self.finish_text)

        self.update_info({
            'state': f'State = {infotext}'
        })

    def update_time(self, time: int):
        text = f'{time % 60}:{int(time / 60) % 60}:{int(time / 60 / 60) % 60}'
        #self.log('Update time to ' + text, 10)
        self.paint_text_box(
            text=text,
            x=self.window_width, y=0,
            w=1, h=0, padding=5+5j,
            fill='#fff'
        )

    def set_pen_up(self, up: bool):
        changed = super().set_pen_up(up)
        if changed:
            if not up:
                display_penpos = self.pos_on_grid(self.xy_pos())
                self.canvas.create_rectangle(
                    display_penpos.real - self.stroke_width / 2, display_penpos.imag - self.stroke_width / 2,
                    display_penpos.real + self.stroke_width / 2, display_penpos.imag + self.stroke_width / 2, 
                    fill=self.current_color, outline='#000', width=1
                )
            self.paint_color()
        return changed
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        print('fullscreen toggled')
        self.window.attributes("-fullscreen", self.fullscreen)
        
    def main_loop(self): 
        self.window.mainloop()

    def pos_on_grid(self, pos: complex):
        xpos = pos.real / self.egg_xborder_steps * (self.config['egg_use_percent']/100) * self.window_eggwidth + self.window_width / 2
        ypos = pos.imag / self.egg_y_steps * self.window_height # (1 - pos.imag) * self.height
        return xpos + ypos * 1j

    def execute_steps_to(self, deltasteps: complex, **kwargs):
        super().execute_steps_to(deltasteps)
        info = kwargs.get('info', False)
        pen_pos = self.xy_pos()
        new_pos = pen_pos + deltasteps

        if not self.ispenup: self.line_to(pen_pos, new_pos)
        if info:
            coordinates = self.pos_to_string(new_pos).split('_')
            print(f'info {coordinates}')
            self.update_info({
                'pos_percent': coordinates[0],
                'pos_distance': coordinates[1],
                'pos_steps': coordinates[2]
            })

    def line_to(self, pos1: complex, pos2: complex):
        display1 = self.pos_on_grid(pos1)
        display2 = self.pos_on_grid(pos2)
        #+print(f'canvas line from {pos1} | {display1} to {pos2} | {display2}')
        self.canvas.create_line(
            display1.real, display1.imag, 
            display2.real, display2.imag,
            fill=self.current_color, width=self.stroke_width
        )
    
        if pos2.imag > self.egg_y_steps or pos2.imag < 0:
            yadd = (1j if pos2.imag < 0 else -1j) * self.egg_y_steps
            self.line_to(pos1 + yadd, pos2 + yadd)
        
    def clear(self):
        self.canvas.create_rectangle(
            0, 0, 
            self.window_width, self.window_height, 
            fill=self.background
        )
        self.canvas.create_rectangle(
            (self.window_width - self.window_eggwidth)/2, 0, 
            (self.window_width + self.window_eggwidth)/2, self.window_height, 
            fill='#fff', width=0
        )
    
    def paint_all(self):
        self.clear_grid()
        self.paint_color()
        self.paint_info()
        
    def clear_grid(self):
        self.clear()
        
        for xrow in range(-5, 6):
            pos = xrow / 10 * self.egg_xborder_steps
            xpos = self.pos_on_grid(pos)
            self.canvas.create_line(
                xpos.real, 0, 
                xpos.real, self.window_height, 
                width=2 if xrow == 0 else 1, fill='#000'
            )
            self.canvas.create_text(
                xpos.real, 0, 
                text=f'  {xrow*10}% ', 
                fill=self.grid_fill, anchor='nw'
            )
            
        left_edge = self.pos_on_grid(-0.5 * self.egg_xborder_steps).real
        right_edge = self.pos_on_grid(0.5 * self.egg_xborder_steps).real
        
        for yrow in range(0, 11):
            ypos = self.pos_on_grid(yrow/10 * 1j * self.egg_y_steps)
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

    def update_info(self, info: dict):
        self.info.update(info)
        self.paint_info()
            
    def canvas_info_pos(self):
        string_pos = self.pos_to_string().split('_')
        return {
            'p1': string_pos[0],
            'p2': string_pos[1],
            'p3': string_pos[2]
        }

    def info_text(self, text):
        self.infotext = str(text)
        font_size = 13
        self.paint_text_box(
            text=self.infotext,
            fontsize=font_size, 
            x=self.window_width/2, 
            y=self.window_height/2,
            fill='#fff'
        )
            
    def paint_color(self):
        size = 30
        offset = 10
        
        for color in self.config['color_pos']:
            colorpos = self.config['color_pos'][color]
            if colorpos != None:
                i = len(self.config['color_pos']) - 1 - colorpos
                hex_color = em.color_to_hex(color)

                xpos = offset
                ypos = (offset + size) * i + offset

                size2 = size * ((0.75 if self.ispenup else 1) if self.current_color == color else 0.4)
                xpos2 = xpos + (size - size2)/2
                ypos2 = ypos + (size - size2)/2
                
                self.canvas.create_rectangle(
                    xpos, ypos, 
                    xpos + size, ypos + size,
                    fill='#fff',
                    width=0
                )
                self.canvas.create_rectangle(
                    xpos2, ypos2, 
                    xpos2 + size2, ypos2 + size2,
                    fill=hex_color,
                    width=0
                )
                
    def paint_text_box(self, **kwargs):
        padding = kwargs.get('padding', 20 + 20j)

        fontsize = kwargs.get('size', 12)
        lines = kwargs.get('text', 'Lorem\nipsum.').split('\n')

        spacing = kwargs.get('spacing', 8)
        font = tkinter.font.Font(size=fontsize, family="monospace")
        outline = kwargs.get('outline', '#000')
        
        boxw = 2*padding.real + max([font.measure(s) for s in lines])
        boxh = 2*padding.imag + (fontsize + spacing) * len(lines)
        
        boxx = kwargs.get('x', 5) - kwargs.get('w', 0.5) * boxw
        boxy = kwargs.get('y', 5) - kwargs.get('h', 0.5) * boxh
        
        self.canvas.create_rectangle(
            boxx, boxy,
            boxx + boxw, boxy + boxh,
            fill=kwargs.get('fill', self.background),
            outline= outline,
            width=1
        )
        
        for line in lines:
            self.canvas.create_text(
                boxx + padding.real, boxy + padding.imag,
                text=line,
                fill=kwargs.get('textcolor', '#000'),
                font=font,
                anchor='nw'
            )
            boxy += fontsize + spacing
            
        return (boxw, boxh)
            
    def paint_info(self):
        font_size = 10
        lines = self.info.values()
        
        try:
            self.canvas.create_rectangle(
                self.window_width - self.info_size[0],
                self.window_height - self.info_size[1],
                self.window_width, self.window_height,
                fill=self.background, width=0
            )
        except AttributeError: pass
                
        self.info_size = self.paint_text_box(
            text = '\n'.join(lines), 
            x=self.window_width, y=self.window_height,
            w=1, h=1, fontsize=font_size,
            outline=self.background
        )