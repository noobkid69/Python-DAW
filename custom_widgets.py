from tkinter import *
from tkinter import ttk
import math
import pyautogui
from assets import colors
original_cursors = {}
def set_cursor_for_all(widget, cursor_style):
    if widget not in original_cursors:
        original_cursors[widget] = widget['cursor']
    widget.configure(cursor=cursor_style)

    for child in widget.winfo_children():
        set_cursor_for_all(child, cursor_style)

def reset_all_cursors():
    for widget, original_cursor in original_cursors.items():
        try:
            widget.configure(cursor=original_cursor)
        except TclError:
            print("Widgeten har förstörts")
    original_cursors.clear()

class EditableText: # Använder canvas text medan bpm selector använder labels, annars hade jag använt inheritance.
        
        def __init__(self, canvas, x, y, text, wrap_length = 70):
            self.canvas = canvas
            self.x = x
            self.y = y
            self.text_id = canvas.create_text(x, y, text=text, tags=("editable", "scaleable"), fill="black", font=("Arial", 10), anchor="n", width = wrap_length)
            self.entry = None
            canvas.tag_bind(self.text_id, "<Double-1>", self.edit_text)

        def edit_text(self, event):
            text = self.canvas.itemcget(self.text_id, "text")
            self.entry = ttk.Entry(self.canvas)
            self.entry.insert(0, text)

            x, y = self.canvas.coords(self.text_id)
            self.entry_window = self.canvas.create_window(x, y, window=self.entry, anchor="nw")
            self.entry.focus()
            self.entry.bind("<Return>", self.save_text)
            self.entry.bind("<FocusOut>", self.save_text)

        def save_text(self, event):
            new_text = event.widget.get()
            if new_text:
                self.canvas.itemconfigure(self.text_id, text=new_text)
            self.canvas.delete(self.entry_window)
            self.entry = None
            self.canvas.focus_set()

class DragSelector(ttk.Frame):
    def __init__(self, root, min_bpm, max_bpm, global_root, bg = "black", fg="white", empty="", start=None, linked_var = None, font_size = 10, *kwargs):
        super().__init__(master=root, *kwargs)
        self.empty = empty
        self.current_bpm = start
        if linked_var:
            self.text_var = linked_var
        else:
            self.text_var = StringVar(value=str(self.current_bpm) if self.current_bpm is not None else self.empty)
        
        

        
        self.vcmd = global_root.register(self.validate_number), "%P"
        self.global_root = global_root
        self.min_bpm, self.max_bpm = min_bpm, max_bpm
        self.bpm_selector = ttk.Label(self, textvariable=self.text_var, width=5, anchor="center", cursor="double_arrow", background=bg, foreground=fg, font=("Helvetica", font_size))
        self.bpm_selector.grid()
        self.sensitivity = 0.05
        self.startig_bpm = self.text_var.get()
        self.entry = None
        self.drag_start_y = None
        self.bpm_selector.bind("<Button-1>", self.start_drag)
        self.bpm_selector.bind("<B1-Motion>", self.on_drag)
        self.bpm_selector.bind("<ButtonRelease-1>", self.end_drag)
        self.bpm_selector.bind("<Double-1>", self.edit_text)

        

        pyautogui.FAILSAFE = False
    def update_var(self, new_var):
        self.text_var = new_var
        self.bpm_selector.configure(textvariable=new_var)
    def start_drag(self, event):
        
        self.dragged = False
        try:
            self.startig_bpm = float(self.text_var.get())
        except ValueError:
            self.startig_bpm = float(self.min_bpm if self.empty else 0)
        self.drag_start_y = event.y_root

        
        print("fufuf")
    def on_drag(self, event):
        if not self.dragged:
            set_cursor_for_all(self.global_root, "none")
        self.dragged = True
        current_y = event.y_root
        dy = current_y - self.drag_start_y
        new_bpm = self.startig_bpm - dy * self.sensitivity
        new_bpm = min(new_bpm, self.max_bpm)
        if not self.empty:
            new_bpm = max(new_bpm, self.min_bpm)
        else:
            if new_bpm < self.min_bpm:
                self.current_bpm = None
                self.text_var.set(self.empty)
                return
        new_bpm = int(new_bpm)
        self.current_bpm = new_bpm
        self.text_var.set(str(new_bpm))

        global_x = event.x_root
        global_y = event.y_root
        screen_width, screen_height = pyautogui.size()
        min_distance = 20 # 20 funkar bra
        if global_y <= min_distance or global_y >= screen_height - min_distance:
            window_top = self.global_root.winfo_rooty()
            center_y = window_top + screen_height // 2
            pyautogui.moveTo(event.x_root, center_y)
            self.drag_start_y = center_y  
            self.startig_bpm = float(self.current_bpm if self.current_bpm is not None else self.min_bpm)


    def end_drag(self, event):
        if self.dragged:
            self.drag_start_y = None
            x, y = event.widget.winfo_rootx()+ event.widget.winfo_width()/2, event.widget.winfo_rooty() + event.widget.winfo_height()/2
            print(x, y)
            pyautogui.moveTo(x, y)
            reset_all_cursors()
        
    def edit_text(self, event):
        self.bpm_selector.grid_remove()
        
        self.entry = ttk.Entry(self, width=5, validate="key", validatecommand=self.vcmd)
        self.entry.focus()
        self.entry.insert(0, self.text_var.get())
        self.entry.bind("<Return>", self.save_text)
        self.entry.bind("<FocusOut>", self.save_text)
        self.entry.grid(row=1, column=0)
    def save_text(self, e):
        try:
            new_bpm = int(self.entry.get())
            new_bpm = max(min(new_bpm, self.max_bpm), self.min_bpm)
            self.current_bpm = new_bpm
            self.text_var.set(str(new_bpm))
        except ValueError:
            if self.empty:
                self.current_bpm = None
                self.text_var.set(self.empty)

        self.entry.destroy()
        self.bpm_selector.grid()
    def validate_number(self, value_if_allowed):
        return value_if_allowed.isdigit() or value_if_allowed == ""

class Knob(Canvas):
    def __init__(self, master = None, width = 200, height=200, padding=20, sensitivity = 50, start_value = 270, knob_background = "lightgray",
                label_size = 0, suffix="%", style = ("regular", 0, 1, 100), linked_var = None, linked_text = None, *kwargs): # style tar i formatet (style, min, max, multiplier))
        super().__init__(master, width=width, height=height, background=colors["topbar_background"], border=None, *kwargs)
        self.width = width 
        self.height = height
        self.sensitivity = sensitivity # i grader
        self.suffix = suffix
        self.style, self.min, self.max, self.mult = style
        self.padding = padding
        
        self.background_circle = self.create_oval(
            padding, padding, width - padding, height - padding,
            fill=knob_background, outline=""
        )
        origin = (width/2)-padding, (height/2)-padding
        self.value = start_value/360

        self.value_arc = self.create_arc(padding,padding, width-padding, height-padding, style="arc", width=3, outline="blue", start=90, extent=-start_value)
        
        if label_size:
            self.volume_label = Label(self, text=f"{self.value * self.mult:.2f}{self.suffix}",
                                         font=("Arial", label_size), bg=knob_background)
            self.volume_label.place(x=self.width/2, y=self.height/2, anchor="center")
        self.linked_var = linked_var
        self.linked_text = linked_text
        if linked_var: 
            self.volume_label["textvariable"] = self.linked_text
            self.value = linked_var.get()
            extent = self.value if not 1 else 0.999
            self.itemconfig(self.value_arc, extent=-extent*360)
        self.bind("<Button-1>", self.grab_knob)
        self.bind("<B1-Motion>", self.change_knob)

    def update_linked_vars(self, new_volume, new_text):
        self.linked_var = new_volume
        self.linked_text = new_text
        self.volume_label["textvariable"] = new_text
    def grab_knob(self, event):
        self.last_degree = -float(self.itemcget(self.value_arc, "extent"))

    def change_knob(self, event):
        x = event.x - self.padding - (self.width/2-self.padding)
        y = (self.height/2-self.padding)-(event.y - self.padding)
        try:
            
            radians = math.atan2(y,x)
            degrees = (90-math.degrees(radians))%360
            
            if (self.last_degree >350 and degrees<self.sensitivity):
                self.itemconfig(self.value_arc, extent=359.9)
                self.value = self.max
                print("full volume")
            elif self.last_degree<10 and degrees>360-self.sensitivity:
                self.itemconfig(self.value_arc, extent=360)
                self.value = self.min
            else:
                self.value = degrees/360
                self.itemconfig(self.value_arc, extent=-degrees)
                self.last_degree = degrees
            if self.linked_var:
                self.linked_var.set(self.value)
                self.linked_text.set(f"{self.value*100:.2f}%")
            elif hasattr(self, "volume_label"):
                self.volume_label.config(text=f"{self.value * self.mult:.2f}{self.suffix}")
        except Exception as e:
            print(f"Fel: {e}")

if __name__ == "__main__":
    root = Tk()
    volume_knob = Knob(root, 100, 100, 20, label_size=10)
    pan = Knob(root, 100, 100, 20, label_size=10)
    pan.grid(column=1, row=0)
    volume_knob.grid(column=0, row=0)
    text = IntVar(value=120)
    bpm = DragSelector(root, 60, 140, root, empty="-")
    
    bpm.grid()
    root.mainloop()