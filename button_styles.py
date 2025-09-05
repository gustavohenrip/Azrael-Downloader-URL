import tkinter as tk

class RoundedFrame(tk.Frame):
    def __init__(self, parent, bg_color, width=None, height=None, corner_radius=10):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self.width = width or 200
        self.height = height or 50
        
        self.canvas = tk.Canvas(self, width=self.width, height=self.height,
                               bg=parent.cget('bg'), highlightthickness=0, bd=0)
        self.canvas.pack()
        
        self.inner_frame = tk.Frame(self.canvas, bg=bg_color)
        self.canvas_frame = self.canvas.create_window(5, 5, window=self.inner_frame, anchor='nw')
        
        self.draw_rounded_bg()
    
    def draw_rounded_bg(self):
        self.canvas.delete('bg_rect')
        x1, y1, x2, y2 = 0, 0, self.width, self.height
        r = self.corner_radius
        
        self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, 
                              fill=self.bg_color, outline=self.bg_color, tags='bg_rect')
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, 
                              fill=self.bg_color, outline=self.bg_color, tags='bg_rect')
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, 
                              fill=self.bg_color, outline=self.bg_color, tags='bg_rect')
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, 
                              fill=self.bg_color, outline=self.bg_color, tags='bg_rect')
        
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=self.bg_color, outline=self.bg_color, tags='bg_rect')
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=self.bg_color, outline=self.bg_color, tags='bg_rect')

class ModernButton(tk.Frame):
    def __init__(self, parent, text='', command=None, bg_color='#0078d4', hover_color='#106ebe', 
                 text_color='white', width=120, height=40, font=('Segoe UI', 10, 'bold')):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
        self.width = width
        self.height = height
        
        self.canvas = tk.Canvas(self, width=width, height=height, 
                               highlightthickness=0, bd=0, bg=parent.cget('bg'))
        self.canvas.pack()
        
        self.text = text
        self.font = font
        
        self.canvas.bind('<Enter>', self.on_enter)
        self.canvas.bind('<Leave>', self.on_leave)
        self.canvas.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
        self.draw_button()
    
    def draw_button(self):
        self.canvas.delete('all')
        
        color = self.hover_color if self.is_hovered else self.bg_color
        x1, y1, x2, y2 = 2, 2, self.width-2, self.height-2
        r = 8
        
        shadow_x1, shadow_y1, shadow_x2, shadow_y2 = x1+2, y1+2, x2+2, y2+2
        self.canvas.create_arc(shadow_x1, shadow_y1, shadow_x1+2*r, shadow_y1+2*r, start=90, extent=90, 
                              fill='#404040', outline='#404040')
        self.canvas.create_arc(shadow_x2-2*r, shadow_y1, shadow_x2, shadow_y1+2*r, start=0, extent=90, 
                              fill='#404040', outline='#404040')
        self.canvas.create_arc(shadow_x2-2*r, shadow_y2-2*r, shadow_x2, shadow_y2, start=270, extent=90, 
                              fill='#404040', outline='#404040')
        self.canvas.create_arc(shadow_x1, shadow_y2-2*r, shadow_x1+2*r, shadow_y2, start=180, extent=90, 
                              fill='#404040', outline='#404040')
        self.canvas.create_rectangle(shadow_x1+r, shadow_y1, shadow_x2-r, shadow_y2, fill='#404040', outline='#404040')
        self.canvas.create_rectangle(shadow_x1, shadow_y1+r, shadow_x2, shadow_y2-r, fill='#404040', outline='#404040')
        
        self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, 
                              fill=color, outline=color)
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, 
                              fill=color, outline=color)
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, 
                              fill=color, outline=color)
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, 
                              fill=color, outline=color)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=color, outline=color)
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=color, outline=color)
        
        self.canvas.create_text(self.width//2, self.height//2, 
                               text=self.text, fill=self.text_color, 
                               font=self.font, anchor='center')
    
    def on_enter(self, event=None):
        self.is_hovered = True
        self.draw_button()
        self.config(cursor='hand2')
    
    def on_leave(self, event=None):
        self.is_hovered = False
        self.draw_button()
        self.config(cursor='')
    
    def on_click(self, event=None):
        if self.command:
            self.command()

class RoundedProgressBar(tk.Frame):
    def __init__(self, parent, width=400, height=20, bg_color='#2a2a2a', fill_color='#0078d4'):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.progress_value = 0
        
        self.canvas = tk.Canvas(self, width=width, height=height,
                               bg=parent.cget('bg'), highlightthickness=0, bd=0)
        self.canvas.pack()
        
        self.draw_progress()
    
    def draw_progress(self):
        self.canvas.delete('all')
        x1, y1, x2, y2 = 0, 0, self.width, self.height
        r = self.height // 2
        
        self.canvas.create_arc(x1, y1, x1+2*r, y2, start=90, extent=180, 
                              fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_arc(x2-2*r, y1, x2, y2, start=270, extent=180, 
                              fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=self.bg_color, outline=self.bg_color)
        
        if self.progress_value > 0:
            progress_width = (self.width - 2*r) * (self.progress_value / 100) + 2*r
            if progress_width > 2*r:
                self.canvas.create_arc(x1, y1, x1+2*r, y2, start=90, extent=180, 
                                      fill=self.fill_color, outline=self.fill_color)
                if progress_width < self.width - r:
                    self.canvas.create_rectangle(x1+r, y1, progress_width, y2, 
                                               fill=self.fill_color, outline=self.fill_color)
                else:
                    self.canvas.create_rectangle(x1+r, y1, x2-r, y2, 
                                               fill=self.fill_color, outline=self.fill_color)
                    self.canvas.create_arc(x2-2*r, y1, x2, y2, start=270, extent=180, 
                                          fill=self.fill_color, outline=self.fill_color)
    
    def set_progress(self, value):
        self.progress_value = max(0, min(100, value))
        self.draw_progress()

class RoundedCombobox(tk.Frame):
    def __init__(self, parent, values=[], bg_color='#2a2a2a', fg_color='white', width=150, height=36, font=('Segoe UI', 11)):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.values = values
        self.current_index = 0
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.width = width
        self.height = height
        self.font = font
        
        self.canvas = tk.Canvas(self, width=width, height=height,
                               bg=parent.cget('bg'), highlightthickness=0, bd=0)
        self.canvas.pack()
        
        self.var = tk.StringVar()
        if values:
            self.var.set(values[0])
        
        self.canvas.bind('<Button-1>', self.on_click)
        self.bind('<Button-1>', self.on_click)
        
        self.draw_combobox()
    
    def draw_combobox(self):
        self.canvas.delete('all')
        x1, y1, x2, y2 = 0, 0, self.width, self.height
        r = 8
        
        self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, 
                              fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, 
                              fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, 
                              fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, 
                              fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=self.bg_color, outline=self.bg_color)
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=self.bg_color, outline=self.bg_color)
        
        current_text = self.var.get()
        self.canvas.create_text(15, self.height//2, text=current_text, fill=self.fg_color,
                               font=self.font, anchor='w')
        
        arrow_x = self.width - 15
        arrow_y = self.height // 2
        self.canvas.create_polygon(arrow_x-5, arrow_y-3, arrow_x+5, arrow_y-3, arrow_x, arrow_y+3,
                                  fill=self.fg_color, outline=self.fg_color)
    
    def on_click(self, event=None):
        if not self.values:
            return
        
        menu = tk.Menu(self, tearoff=0, bg=self.bg_color, fg=self.fg_color,
                      activebackground='#0078d4', activeforeground='white',
                      bd=0, relief='flat')
        
        for value in self.values:
            menu.add_command(label=value, command=lambda v=value: self.select_value(v))
        
        try:
            menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.height)
        finally:
            menu.grab_release()
    
    def select_value(self, value):
        self.var.set(value)
        self.draw_combobox()
    
    def get(self):
        return self.var.get()
    
    def set(self, value):
        if value in self.values:
            self.var.set(value)
            self.draw_combobox()

class RoundedEntry(tk.Frame):
    def __init__(self, parent, bg_color='#2a2a2a', fg_color='white', width=200, height=40, font=('Segoe UI', 11)):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.bg_color = bg_color
        self.width = width
        self.height = height
        
        self.canvas = tk.Canvas(self, width=width, height=height,
                               bg=parent.cget('bg'), highlightthickness=0, bd=0)
        self.canvas.pack()
        
        x1, y1, x2, y2 = 0, 0, width, height
        r = 8
        
        self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, 
                              fill=bg_color, outline=bg_color)
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, 
                              fill=bg_color, outline=bg_color)
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, 
                              fill=bg_color, outline=bg_color)
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, 
                              fill=bg_color, outline=bg_color)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=bg_color, outline=bg_color)
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=bg_color, outline=bg_color)
        
        self.entry = tk.Entry(self, bg=bg_color, fg=fg_color, font=font, bd=0, 
                             insertbackground=fg_color, highlightthickness=0)
        self.canvas.create_window(10, height//2, window=self.entry, anchor='w', width=width-20)
    
    def get(self):
        return self.entry.get()
    
    def insert(self, index, string):
        return self.entry.insert(index, string)
    
    def delete(self, first, last=None):
        return self.entry.delete(first, last)
