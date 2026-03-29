from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
import random

import os
from sequencer import Sequencer
from mixer import Mixer
from logik_ljud.tid import timer

from project_manager import *
from assets import *
import global_stuff

import custom_widgets

import math
import soundfile as sf
import sounddevice as sd
import threading
import samplerate
import numpy as np

sd.default.samplerate = global_stuff.SAMPLERATE
sd.default.blocksize = global_stuff.BLOCKSIZE
sd.default.channels = 2

lock = threading.Lock()


mixer = Mixer()

def str_to_float(s): # Det fanns visst en Fractions modul som gör exakt samma sak.
    if '/' in s:
        numerator, denominator = s.split('/')
        return float(numerator) / float(denominator)
    else:
        return float(s)
def clip_change_width_all(*args):
    for clip in audioclips:
        clip.change_width_bpm()
        print("sus")

class Meny:
    def __init__(self, träd):
        
        self.meny = Menu(root)

        Arkiv = Menu(self.meny)
        self.Öppna = Menu(Arkiv)
        
        Arkiv.add_cascade(menu=self.Öppna, label="Öppna")
        for _, folders, _ in os.walk("projekt"):
            for folder in folders:
                self.Öppna.add_command(label=folder, command= lambda: load_project(root, folder))
                print(folder)
        
        Arkiv.add_command(label = "Nytt project", command = lambda: load_project(root))
        Arkiv.add_command(label="Spara", command=lambda: save_project(träd, current_project), accelerator="Ctrl+S")
        Arkiv.add_command(label="Inställningar", command=None)
        Arkiv.add_command(label="Stäng", command=root.quit, accelerator="Alt+F4")
        self.meny.add_cascade(label="Arkiv", menu=Arkiv)

        Edit = Menu(self.meny, tearoff=0)
        Edit.add_command(label="Hej", command=None)
        self.meny.add_cascade(label="Edit", menu=Edit)

        root.config(menu=self.meny)

class Träd:
    
    def __init__(self, root, options_root):
        
        self.icons = load_icons()
        self.check_val = BooleanVar(value=0)
        self.tree_scrollbar = ttk.Scrollbar(root)
        self.tree_scrollbar.grid(row=0, column=0, sticky="NWES")
        self.träd = ttk.Treeview(root, yscrollcommand=self.tree_scrollbar.set, style="Cool.Treeview")
        self.tree_scrollbar.config(command=self.träd.yview)
        self.träd.bind("<<TreeviewSelect>>", self.select_item)
        self.träd.bind("<B1-Motion>", self.drag_item)

        self.träd.bind_all("<ButtonRelease-1>", self.release_item)

        
        
        
        self.träd["show"] = "tree"
        self.träd.grid(column=1, row=0, sticky="NWSE")
        
        self.allowed_files_checkbutton = ttk.Checkbutton(options_root, variable=self.check_val)
        self.allowed_files_checkbutton["state"] = "disabled" # Kan tekniskt sett tas bort ☝️🤓

        self.file_manager = self.File(self)
        self.file_button = ttk.Button(options_root, image=self.icons["file"], command = self.file_manager.selected_file, cursor=load_icons()["hover_cursor"])
        self.file_button.grid(row = 0, column = 0, sticky = "NW")
        self.allowed_files_checkbutton.configure(command=self.file_manager.check_button)
        
        self.allowed_files_checkbutton.grid(column=1, row=0)
        

    def select_item(self, event):
        if not os.path.isdir(self.träd.focus()):
            # print(self.träd.focus(), self.träd.selection())
            global_stuff.dragged_item = self.träd.focus()
    def drag_item(self, event):
        pass # Finns i AudioClip så ska nog inte göra något här. Kan visa preview men känns lite onödigt.
    def release_item(self, event): # Funkar bara om mappen inte är öppen från början (förmodligen) så skriv om vid fel.
        
        if global_stuff.dragged_item:
            canvas_width = middle.canvas.winfo_width()
            canvas_height = middle.canvas.winfo_height()
            
            canvas_absx = middle.canvas.winfo_rootx()
            canvas_absy = middle.canvas.winfo_rooty()

            x_root = event.x_root
            y_root = event.y_root
            
            x_relativeto_canvas = x_root-canvas_absx
            y_relativeto_canvas = y_root-canvas_absy

            mouse_in_canvas = (canvas_absx <= x_root <= canvas_absx + canvas_width and
                canvas_absy <= y_root <= canvas_absy + canvas_height)
            if mouse_in_canvas:
                try:
                    data = global_stuff.files[global_stuff.dragged_item] if global_stuff.dragged_item in global_stuff.files.keys() else None
                    audioclips.append(middle.AudioClip(x=x_relativeto_canvas, y=y_relativeto_canvas, audio=global_stuff.dragged_item, group=global_stuff.group, data=data))
                except ValueError:
                    print("brrbrrpatapim")
            if not global_stuff.pen_selected:
                global_stuff.dragged_item= None
        
    class File:
        
        def __init__(self, parent):
            self.träd_objekt = parent
            self.folder_name = None
            self.folders = set()
            self.files = set()

            sounds_path = os.path.join(os.path.abspath(os.getcwd()), "stock_sounds")
            self.import_folder(sounds_path)
        
        def clear_items(self):
            self.träd_objekt.träd.delete(*self.träd_objekt.träd.get_children(), * (d for d in self.files)) #ÄNTLIGEN FIXAD!!😁
            self.files.clear()
            self.folders.clear()
        
        def insert_folder(self, location, path):
            folder_name = os.path.basename(path)
            new_folder = self.träd_objekt.träd.insert(location, "end", text = folder_name, image = self.träd_objekt.icons["file"], iid=path)
            self.folders.add(new_folder)
        
        def insert_file(self, path):
            file_name = os.path.basename(path)
            file = self.träd_objekt.träd.insert(os.path.dirname(path), END, text = file_name, iid=path) # Kanske ska addas i en lista. Förmodligen inte.
            self.files.add(file)
        
        def selected_file(self): # sämst namn på funktionen asså
            print(global_stuff.playing)
            if global_stuff.playing:
                return
            self.folder_name = fd.askdirectory()
            if not self.folder_name: 
               return
            self.import_folder(self.folder_name)
        def import_folder(self, folder):
            self.clear_items()
            self.träd_objekt.check_val.set(0)
            self.träd_objekt.allowed_files_checkbutton["state"] = "active"

            for dirpath, _, filenames in os.walk(folder):
                parent = os.path.split(dirpath)[0] # Delar sökvägen i tuple där första argumentet är föräldren (vilket jag vill ha). Det fixar också formatteringen
                if parent not in self.folders:
                    self.insert_folder("", dirpath)
                elif parent in self.folders:
                    self.insert_folder(parent, dirpath)
                else:
                    print("Något importerades inte korrekt. Kolla selected_file funktionen.")
            for dirpath, _, filenames in os.walk(folder):
                for file in filenames:
                    self.insert_file(os.path.join(dirpath, file)) # Var tvungen att skapa en till loop för att få filerna sist.
            print(f"files: {len(self.files)}, folders: {len(self.folders)}")
            

        def check_button(self):
            if self.träd_objekt.check_val.get():
                for file in self.files:
                    if not file.endswith((global_stuff.allowed_file_types)):
                        self.träd_objekt.träd.detach(file)
            else:
                for file in self.files:
                    if not file.endswith((global_stuff.allowed_file_types)):
                        self.träd_objekt.träd.move(file, os.path.dirname(file), "end")

class Top:
    def __init__(self, root, global_root = None):
        self.icons = load_icons()
        

        # self.piano_roll_knapp = ttk.Button(root, image=self.icons["piano"], command=lambda:print("Piano roll"), cursor=load_icons()["hover_cursor"])
        # self.piano_roll_knapp.grid(row = 0, column=1, padx=10)
        
        
        self.mixer_knapp = ttk.Button(root, image=self.icons["mixer"], command=mixer.show_mixer, cursor=load_icons()["hover_cursor"])
        

        # self.sequencer = Sequencer(root)
        # self.sequencer_knapp = ttk.Button(root, image=self.icons["sequencer"], command= self.sequencer.show_window, cursor=load_icons()["hover_cursor"])
        # self.sequencer_knapp.grid(row = 0, column=0)
        
        self.play_knapp = ttk.Button(root, command= lambda: mixer.master.play(self.play_knapp), image=self.icons["play"], cursor=load_icons()["hover_cursor"])
        

        # self.stop_play_knapp = ttk.Button(root, command=lambda: timer.clear_timer(self.play_knapp), image = self.icons["stop"], cursor=load_icons()["hover_cursor"])
        # self.stop_play_knapp.grid(column=5, row=0)
        self.time_label = ttk.Label(root, textvariable=timer.var)
        
        
        
        # self.play_mode = StringVar(value="Pattern")
        # self.pattern = ttk.Radiobutton(root, text="Pat", value="Pattern")
        # self.song = ttk.Radiobutton(root, text="song", value="Song")
        # self.pattern.grid(row=0, column=3)
        # self.song.grid(row=1, column=3)
        
        self.pen = ttk.Button(root, image = self.icons["pen"], command=self.pen_click)
        
        self.slicer = ttk.Button(root,image=self.icons["slicer"], command = self.slicer_click)

        self.bucket = Menubutton(root, image=self.icons["bucket"], indicatoron=False, background=colors["topbar_background"], activebackground=colors["beat_lines"])
        
        self.bucket_label = Label(root, text="▼", fg="black", background=colors["topbar_background"])
        
        self.bucket_menu = Menu(self.bucket, tearoff=0)
        self.bucket.configure(menu=self.bucket_menu)
        self.bucket_menu.add_command(label="None", background=colors["grid_background"], foreground="black", command=self.reset_bucket)
        
        self.bpmselector = custom_widgets.DragSelector(root, min_bpm=40, max_bpm=200, global_root=global_root, linked_var=bpm_var, font_size=10)
        
        
        options = ["1", "1/2", "1/4", "1/8", "1/16"]
        self.snap_select = ttk.OptionMenu(root, global_stuff.snap_var_x, options[2], *options)

        menu = self.snap_select["menu"]
        menu.config(
        background=colors["topbar_background"],
        foreground="white",
        activebackground=colors["beat_lines"],
        activeborderwidth=0,
        relief="flat")

        self.bpmselector.grid(row = 0, column=0)
        self.pen.grid(row= 0, column=1)
        self.slicer.grid(row=0, column=2)
        self.bucket.grid(row=0, column=3)
        self.bucket_label.grid(row=0, column=4)
        self.mixer_knapp.grid(row = 0, column=5, padx=10)
        self.play_knapp.grid(column=6, row=0)
        self.time_label.grid(row=0, column=7)
        
        
        self.snap_select.grid(row=0, column=8, padx=5)

        global_stuff.pen_selected = False
    def slicer_click(self):
        global_stuff.slicer_selected = not global_stuff.slicer_selected
        if global_stuff.slicer_selected:
            self.slicer.configure(style="Selected.TButton")
            self.reset_bucket()
            self.reset_pen()
            return
        self.reset_slicer()
    def pen_click(self):
        global_stuff.pen_selected = not global_stuff.pen_selected
        if global_stuff.pen_selected:
            self.pen.configure(style = "Selected.TButton")
            if global_stuff.bucket_selected:
                global_stuff.group = global_stuff.bucket_selected
            else:
                global_stuff.group = f"group {len(global_stuff.groups)}"

            global_stuff.dragged_item = Träd_instance.träd.focus()
            self.reset_slicer()
            print("hej")
            return
        self.reset_pen()
        
    def select_bucket(self,group, color):
        print(color)
        self.bucket_label.configure(foreground=color) 
        self.bucket.configure(background=colors["scale_handle"])
        self.reset_pen()
        global_stuff.bucket_selected = group
        self.reset_slicer()
    def reset_slicer(self):
        global_stuff.slicer_selected=None
        self.slicer.configure(style="TButton")
    def reset_pen(self):
        global_stuff.pen_selected = False
        global_stuff.group = None
        self.pen.configure(style = "TButton")
    def reset_bucket(self):
        self.bucket_label.configure(foreground="black")
        global_stuff.bucket_selected = None
        self.bucket.configure(background=colors["topbar_background"])
        
class Middle:
    def __init__(self, root):

        self.beats_in_a_bar = 4 # kanske använd dessa om man vill kunna bya taktakt. Dock finns prioriteringar.
        self.beat_note = 1/4 # kanske använd dessa om man vill kunna byta taktakt. Dock finns prioriteringar.
        self.lines_per_bar = 16

        self.zoom_in, self.zoom_out = 1.1, 0.9
        self.max_zoom_y, self.min_zoom_y = 2, 0.5
        self.max_zoom_x, self.min_zoom_x = 16, 1
        self.zoom_x = 1
        self.zoom_y = 1
        self.cell_width = 100
        self.cell_height = 100
        self.timeline_height = 30
        self.track_info_width = 80
        
        self.origin_x = 0
        self.origin_y = 0

        self.beats = 1000 # Ska egentligen vara middle.bars men orkar inte ändra
        self.rows = 500

        self.ctrl_pressed = False
        self.alt_pressed = False
        
        root.rowconfigure(0, minsize=self.timeline_height)
        root.rowconfigure(1, weight=1)

        root.columnconfigure(1, weight=1)
        
        self.marker_canvas = Canvas(root, highlightthickness=0, height=self.timeline_height, cursor = load_icons()["hover_cursor"])
        self.canvas = Canvas(root, highlightthickness=0, bg=colors["grid_background"])
        self.track_info_canvas = Canvas(root, highlightthickness=0, width = self.track_info_width, bg=colors["track_info_background"])
        
        self.marker_canvas.grid(row = 0, column=1,sticky="EW", columnspan=1)
        self.canvas.grid(row = 1, column=1,sticky="NSEW")
        self.track_info_canvas.grid(row = 1, column=0, sticky="NSW")

        self.horizontal_scrollbar = ttk.Scrollbar(root, orient=HORIZONTAL, command=self.horizontal_scroll)
        self.vertical_scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=self.vertical_scroll)

        self.horizontal_scrollbar.grid(row=2, column=0, sticky="sew", columnspan=2)
        self.vertical_scrollbar.grid(row=1, column=2, sticky="NSE")

        self.canvas.bind("<Enter>", lambda e: self.focus_canvas)
        self.canvas.bind("<MouseWheel>", self.rescale_canvas)
        
        self.canvas.bind_all("<Control_L>", self.ctrl_down)
        self.canvas.bind_all("<KeyRelease-Control_L>", self.ctrl_up)
        self.canvas.bind_all("<Alt_L>", self.alt_down)
        self.canvas.bind_all("<KeyRelease-Alt_L>", self.alt_up)

        self.canvas.bind("<ButtonRelease-1>", self.button_release)

        self.canvas.configure(xscrollcommand=self.horizontal_scrollbar.set, yscrollcommand=self.vertical_scrollbar.set)
        root.after(100, lambda: self.draw_canvas(rows=self.rows, beats=self.beats))
        
    def button_release(self, e):
        print(global_stuff.dragged_item)

    class Marker:
        def __init__(self, playlist, head_canvas, grid_canvas, tid_var=None):
            mixer.master.update_marker_func = self.move_seconds
            self.playlist = playlist
            self.tid_var = tid_var
            self.head_canvas = head_canvas
            self.grid_canvas = grid_canvas
            self.marker_icon = load_icons()["marker"]
            self.head_canvas.bind("<B1-Motion>", lambda e: self.move(e.x))

            self.marker = head_canvas.create_image(0, 0, image=self.marker_icon, tags="timeline", anchor="w")
            y = self.bbox_coords(grid_canvas)[3]
            x0, y0, x1, y1 = map(int, self.grid_canvas["scrollregion"].split())

            self.line = grid_canvas.create_line(self.line_points(0, y1), fill=colors["marker_color"], tags="scaleable", width=2)
            print(grid_canvas.cget("scrollregion"))
            
        def move(self, x): 

            canvas_width = self.head_canvas.winfo_width() # Fixar nån gång, ska i.af inta vara i denna funktionen.
            scroll_margin = 5
            scroll_speed = 2
            if x<scroll_margin: 
                self.playlist.canvas.xview_scroll(-scroll_speed, "units")
                self.playlist.marker_canvas.xview_scroll(-scroll_speed, "units")
            if x>canvas_width-scroll_margin:
                self.playlist.canvas.xview_scroll(scroll_speed, "units")
                self.playlist.marker_canvas.xview_scroll(scroll_speed, "units")
            x_coord = self.head_canvas.canvasx(x)
            real_x = middle.canvasx_real_x(x_coord)
            if  real_x<0 or real_x> middle.cell_width*middle.beats or global_stuff.playing:
                return
            x0, y0, bx,by = self.bbox_coords(self.grid_canvas) 
            self.head_canvas.coords(self.marker, x_coord,0)
            self.grid_canvas.coords(self.line, self.line_points(x_coord, by))
            bars_passed = (real_x)/self.playlist.cell_width
            minutes = (bars_passed*4)/bpm_var.get()
            total_seconds = (minutes*60)
            minutes = int(total_seconds//60)
            seconds = (total_seconds%60)
            # bpm = b/m m = b/bpm
            timer.update_timer(total_seconds)

        def move_seconds(self,t):
            x = (bpm_var.get() * t / 240) * middle.cell_width
            x_canvas = middle.real_x_canvasx(x)
            x0, y0, bx,by = self.bbox_coords(self.grid_canvas) 
            self.head_canvas.coords(self.marker, x_canvas,0)
            self.grid_canvas.coords(self.line, self.line_points(x_canvas, by))
            
        @staticmethod
        def line_points(x, line_length):
            
            return (x, 0, x, line_length)
        @staticmethod
        def bbox_coords(canvas):
            try: 
                x0, y0, x1, y1 = map(float, canvas["scrollregion"].split())
                return x0, y0, x1, y1
            except Exception as e:
                print(e)

    class AudioClip:
        def __init__(self, x, y, audio, group, data=None):
            self.clip_color = "orange"
            self.group = group
            if group:
                if group not in global_stuff.groups.keys():
                    color = f"#{random.randrange(0, 2**24):06x}"
                    global_stuff.groups[group] = [[], color, DoubleVar(value=1.0), StringVar(value="100%"), StringVar(value="mstr"), BooleanVar()]
                    global_stuff.groups[group][4].trace_add("write", self.update_group_channels)
                    global_stuff.groups[group][5].trace_add("write", lambda *args: self.reverse_audio(global_stuff.groups[group], *args))
                    top_bar.bucket_menu.add_command(label=group, foreground=color, background=colors["grid_background"], activebackground=colors["grid_background"], command=lambda: top_bar.select_bucket(group, color))
                global_stuff.groups[group][0].append(self)
                self.clip_color = global_stuff.groups[group][1]
                self.group_volume = global_stuff.groups[group][2]
                self.group_text = global_stuff.groups[group][3]
                self.group_channel = global_stuff.groups[group][4]
                self.group_reverse = global_stuff.groups[group][5]
                
            else:
                self.group_volume = None
                self.group_channel = None
                self.group_reverse = None
            self.audio = audio
            self.file_name = os.path.basename(audio)

            if not audio.endswith((global_stuff.allowed_file_types)):
                messagebox.showerror(title="Meow", message="Filen måste vara format .mp3 eller .wav")
                raise ValueError
            self.canvas = middle.canvas

            self.width = middle.cell_width
            self.height = middle.cell_height
            # self.x och y är logiska
            self.x = middle.canvasx_real_x(self.round_x(self.canvas.canvasx(x)))
            self.y = middle.canvasy_real_y(self.round_y(self.canvas.canvasy(y)))

            self.start_tid = None # gör när du orkar

            self.x2 = self.get_x2(self.x,width=self.width)
            self.y2 = self.y+self.height
            self.row = None

            try:
                x, y = middle.real_x_canvasx(self.x), middle.real_y_canvasy(self.y)
                x2, y2 = self.get_x2(x), self.get_y2(y)
                self.box = self.canvas.create_rectangle(x, y, x2, y2, tags=("scaleable", "audioclip"), fill=self.clip_color)
                self.text = self.canvas.create_text(x+(self.width/2)*middle.zoom_x, y+(self.height/2)*middle.zoom_y, text=self.file_name, tags=("scaleable", "audioclip"), font=("Helvetica", 7), fill="white", width=self.width)

                self.canvas.tag_bind(self.box, "<Button-1>", self.start_drag)
                self.canvas.tag_bind(self.box, "<B1-Motion>", self.on_drag)
                self.canvas.tag_bind(self.text, "<Button-1>", self.start_drag)
                self.canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)
                self.canvas.tag_bind(self.box, "<ButtonRelease-1>", self.mouse_up)
                try: 
                    self.clip_options = self.ClipOptions(self)
                except Exception as e:
                    print(e)
              
                self.canvas.tag_bind(self.box, "<Double-1>", self.clip_options.show_options)
                self.canvas.tag_bind(self.text, "<Double-1>", self.clip_options.show_options)

                self.canvas.tag_bind(self.box, "<Button-3>", self.delete_clip)
                self.canvas.tag_bind(self.text, "<Button-3>", self.delete_clip)

                threading.Thread(target=self.load_audio, args=(audio,data)).start()
                
            except TclError as e:
                print(e)
                messagebox.showerror(title="Sämst lol", message="En av klippets koordinater är utanför spellistan. HUR LÅNG LÅT GÖR DU!?")
        def reverse_audio(self, group, *args):
                for clip in group[0]:
                    clip.data = clip.data[::-1]
                
        def update_group_channels(self, *args):
            new_channel = global_stuff.groups[self.group][4].get()
            for clip in global_stuff.groups[self.group][0]:
                try:
                    if clip.clip_options.last_channel == new_channel:
                        continue

                    if clip in mixer.channels[clip.clip_options.last_channel].clips:
                        mixer.channels[clip.clip_options.last_channel].clips.remove(clip)

                    if clip not in mixer.channels[new_channel].clips:
                        mixer.channels[new_channel].clips.append(clip)

                    clip.clip_options.last_channel = new_channel
                    clip.clip_options.channel_var.set(new_channel)
                except Exception as e:
                    print(f"Eror vid gruppändring av kanaler: {e}")

        def load_audio(self, audio, data):
            with lock:
                if data is None:
                    self.data, sr = sf.read(audio) 
                    self.data = samplerate.resample(self.data, global_stuff.SAMPLERATE / sr, 'sinc_best') 
                    global_stuff.files[self.audio] = self.data
                else: 
                    self.data = data
                if self.group:
                    if self.group_reverse.get():
                        self.data = data[::-1]
                duration_samples = len(self.data)
                duration_minutes = duration_samples / (global_stuff.SAMPLERATE * 60)
                logical_width = (duration_minutes * middle.cell_width * bpm_var.get()) / 4

                self.width = logical_width
                self.x2 = self.x + logical_width
                self.start_position = int(global_stuff.minutes_samples(middle.real_x_minutes(self.x)))
                audioclips.append(self)
                mixer.channels[self.clip_options.channel_var.get()].clips.append(self)
                print(len(self.data), self.data.shape)
                
                try:
                    x0, x2, y0, y2 = middle.real_x_canvasx(self.x), middle.real_x_canvasx(self.x2), middle.real_y_canvasy(self.y), middle.real_y_canvasy(self.y2)
                    self.canvas.coords(self.box, x0, y0, x2, y2)
                    self.canvas.coords(self.text, (x0 + self.width * middle.zoom_x / 2), (y0 + self.height * middle.zoom_y / 2))
                    self.canvas.itemconfigure(self.text, width =logical_width+20)
                except Exception as e:
                    print(e)


        def mouse_up(self,e ):
            selected_group = global_stuff.bucket_selected
            slicer_selected = global_stuff.slicer_selected
            if selected_group and not global_stuff.pen_selected:
                group_color = global_stuff.groups[selected_group][1]
                self.canvas.itemconfigure(self.box, fill=group_color)
                if self.group and self in global_stuff.groups[self.group][0]:
                    global_stuff.groups[self.group][0].remove(self)
                self.group = selected_group
                group = " ┃ " + self.group if self.group else ""
                self.clip_options.options.title(self.file_name + group)
                if self not in global_stuff.groups[selected_group][0]:
                    global_stuff.groups[selected_group][0].append(self)
                self.clip_color = group_color
                self.group_volume = global_stuff.groups[selected_group][2]
                self.group_text = global_stuff.groups[selected_group][3]
                self.group_channel = global_stuff.groups[selected_group][4]
                self.group_reverse = global_stuff.groups[selected_group][5]

                self.clip_options.reversed_var = self.group_reverse
                self.clip_options.reverse_check_button.config(variable=self.group_reverse)
                self.clip_options.channel_var = self.group_channel
                self.clip_options.channel_selector.update_var(self.group_channel)


                if hasattr(self, 'clip_options') and self.clip_options:
                    new_channel = self.group_channel.get()
                    self.clip_options.channel_var.set(new_channel)
                    self.clip_options.last_channel = new_channel
                    if self.group_volume and not hasattr(self.clip_options, "shared_volume_knob"):
                        self.clip_options.shared_volume_label = ttk.Label(self.clip_options.options_frame, text="Group Volume:")
                        self.clip_options.shared_volume_knob = custom_widgets.Knob( self.clip_options.options_frame, linked_var=self.group_volume, 
                                                                                   linked_text=self.group_text, width=100, height=100, label_size=8)
                        self.clip_options.shared_volume_label.grid(row=3, column=1)
                        self.clip_options.shared_volume_knob.grid(row=3, column=2)
                    elif hasattr(self.clip_options, "shared_volume_knob"):
                        self.clip_options.shared_volume_knob.update_linked_vars(self.group_volume, self.group_text)
                        
            elif slicer_selected:
                canvasx = self.canvas.canvasx(e.x)
                clip_x = middle.real_x_canvasx(self.x)
                clip_y = middle.real_y_canvasy(self.y)
                clip_y2 = self.get_y2(clip_y)

                new_width = middle.canvasx_real_x(canvasx) - self.x
                self.width = new_width
               # nice hur jag blandar middle.canvas och self.canvas
                
                bars = self.width / middle.cell_width # m = b/bpm
                minutes = 4*bars / bpm_var.get()
                samples = int(global_stuff.minutes_samples(minutes))
                
                self.data = self.data[:samples]

                self.x2 = middle.canvasx_real_x(clip_x)
                self.canvas.coords(self.box, clip_x, clip_y, canvasx, clip_y2)
                self.canvas.coords(self.text, (clip_x+self.width*middle.zoom_x/2), (clip_y+self.height*middle.zoom_y/2))
                
                print(f"{canvasx} : {clip_x}")
        def start_drag(self, e):
            
            self.start_drag_x = self.canvas.canvasx(e.x) -middle.real_x_canvasx(self.x)
            self.start_drag_y = self.canvas.canvasy(e.y) - middle.real_y_canvasy(self.y)
            print(self.start_drag_x)
        def on_drag(self, e): # e.x är i relation till canvas kanten (viewport into canvasx)
            current_x = self.canvas.canvasx(e.x)
            current_y = self.canvas.canvasy(e.y)
            try:
                x, y = self.round_x( current_x - self.start_drag_x), self.round_y(current_y)
                x2, y2 = self.get_x2(x), self.get_y2(y)
                self.x = middle.canvasx_real_x(x)
                self.y = middle.canvasy_real_y(y) # Tror detta är mer satisfying för y
                self.x2 = self.x+self.width
                self.y2 = self.y+self.height
                self.canvas.coords(self.box, x, y, x2, y2)
                self.canvas.coords(self.text, (x+self.width*middle.zoom_x/2), (y+self.height*middle.zoom_y/2))
                self.start_position = int(global_stuff.minutes_samples(middle.real_x_minutes(self.x)))
                print(self.start_position)
            except (TypeError, TclError) as e:
                print(e)
                print("Utanför tillåtna gränser")
        def change_width_bpm(self):
            
            duration_minutes = len(self.data)/(global_stuff.SAMPLERATE*60)
            self.width = (duration_minutes * middle.cell_width * bpm_var.get()) / 4
            self.x2 = self.x+self.width
            x = middle.real_x_canvasx(self.x)
            x2 = middle.real_x_canvasx(self.x2)
            y0, y2 = middle.real_y_canvasy(self.y), middle.real_y_canvasy(self.y2)
            self.start_position = int(global_stuff.minutes_samples(middle.real_x_minutes(self.x)))
            
            try:
                self.canvas.coords(self.box, x, y0, x2, y2)
                self.canvas.coords(self.text, x + self.width * middle.zoom_x / 2, y0 + self.height * middle.zoom_y / 2)
                self.canvas.itemconfigure(self.text, width=self.width + 20)
            except Exception as e:
                print(f"🦘🦘🦘🦘:{e}")

        def get_x2(self, x, width = None): # tar canvasx utan zoom. Fixa så det funka om den redan finns + så den anpasses till längden av klippet.
            try:
                if not width: # behöbs egentligen inte
                    width = self.width
                return width*middle.zoom_x + x
            except TypeError:
                pass
        def get_y2(self,y, height=None):
            if not height:
                height = self.height
            return y+height*middle.zoom_y
        def round_x(self, x):
            logical_x = middle.canvasx_real_x(x)
            floated_snap = str_to_float(global_stuff.snap_var_x.get())

            if middle.alt_pressed:
                if logical_x < 0:
                    logical_x = 0
                elif logical_x + self.width > middle.cell_width * middle.beats:
                    logical_x = middle.cell_width * middle.beats - self.width
                return middle.real_x_canvasx(logical_x)

            snapped_logical_x = round(logical_x / (middle.cell_width * floated_snap)) * (middle.cell_width * floated_snap)
            if snapped_logical_x < 0 or snapped_logical_x + self.width > middle.cell_width * middle.beats:
                return None

            return middle.real_x_canvasx(snapped_logical_x)

        def round_y(self, y):
            logical_y = middle.canvasy_real_y(y)
            snapped_logical_y = math.floor(logical_y/middle.cell_height)*middle.cell_height
            if snapped_logical_y<0 or self.get_y2(snapped_logical_y)>middle.cell_height*middle.rows:
                return
            return middle.real_y_canvasy(snapped_logical_y)
        def delete_clip(self, event):
            audioclips.remove(self)
            self.canvas.delete(self.box)
            self.canvas.delete(self.text)
            if self.clip_options and self.clip_options.options.winfo_exists():
                self.clip_options.options.destroy()
            if self.group: 
                global_stuff.groups[self.group][0].remove(self)
            mixer.channels[self.clip_options.channel_var.get()].clips.remove(self)
        def get_chunk(self, frames, global_sample_position):
            clip_start = self.start_position # int
            clip_end = clip_start + len(self.data)
            chunk_start = global_sample_position
            chunk_end = global_sample_position + frames

            if chunk_end <= clip_start or chunk_start >= clip_end:
                return np.zeros((frames, 2), dtype=np.float32)
            
            data_start = max(0, chunk_start - clip_start)
            data_end = min(len(self.data), chunk_end - clip_start)
            chunk = self.data[data_start:data_end]

            if chunk.ndim == 1:
                chunk = np.column_stack((chunk, chunk))
            elif chunk.shape[1] == 1:
                chunk = np.tile(chunk, (1, 2))
            elif chunk.shape[1] < 2:
                chunk = np.column_stack((chunk, chunk))
            gv = 1 if not self.group_volume else self.group_volume.get()
            volume = self.clip_options.volume_knob.value*gv
            pan = self.clip_options.pan.get()
            left = chunk[:, 0] * volume * (1 - pan)
            right = chunk[:, 1] * volume * (1 + pan)
            processed = np.column_stack((left, right))
            pad_before = int(max(0, clip_start - chunk_start))
            pad_after = int(max(0, chunk_end - clip_end))
            if pad_before > 0:
                processed = np.vstack([np.zeros((pad_before, 2), dtype=np.float32), processed])
            if pad_after > 0:
                processed = np.vstack([processed, np.zeros((pad_after, 2), dtype=np.float32)])


            return processed
            
        class ClipOptions:
            def __init__(self, clip):
                self.clip = clip
                self.volume = IntVar(value=60)
                self.pan = DoubleVar(value=0)
                
                self.options = Toplevel(root)
                self.options.rowconfigure(0, weight=1)
                self.options.columnconfigure(0, weight=1)
                self.options_frame = ttk.Frame(self.options, style="clipoptions.TFrame")
                self.options_frame.grid(row=0, column=0, sticky="NSEW")

                self.options.geometry("300x150")
                self.options.maxsize(300,300)
                if clip.group_channel:
                    self.channel_var = clip.group_channel
                else:
                    self.channel_var = StringVar(value="mstr")

                if clip.group_reverse:
                    self.reversed_var = clip.group_reverse
                    
                else:
                    self.reversed_var = BooleanVar()
                    self.reversed_var.trace_add("write", lambda *args: self.clip.reverse_audio([[self.clip]], *args))

                self.channel_selector = custom_widgets.DragSelector(self.options_frame, 1, 10, root, empty="mstr", linked_var=self.channel_var)
                
                
                reverse_label = ttk.Label(self.options_frame, text="Reverse:")
                self.reverse_check_button = ttk.Checkbutton(self.options_frame, variable=self.reversed_var)
                self.volume_knob = custom_widgets.Knob(master=self.options_frame, width=80, height=80, padding=10, sensitivity=100, label_size=8)
                pan_text = ttk.Label(self.options_frame, text="Pan:")
                pan_slider = ttk.Scale(self.options_frame, orient=HORIZONTAL, from_=-1, to=1, variable=self.pan, command=self.change_slider)
                try: 
                    if clip.group_volume:
                        self.shared_volume_label = ttk.Label(self.options_frame, text="Group Volume:")
                        self.shared_volume_knob =custom_widgets.Knob(self.options_frame, linked_var=clip.group_volume, linked_text= clip.group_text, width=100, height=100, label_size=8)
                        self.shared_volume_label.grid(row=3, column=1)
                        self.shared_volume_knob.grid(row=3, column=2)
                except Exception as e:
                    print("e")
                group = " ┃ " + clip.group if clip.group else ""
                self.options.title(clip.file_name + group)

                
                if not clip.group:
                    self.channel_var.trace_add("write", self.update_channel)

                self.channel_selector.grid(row=0, column=2)
                self.volume_knob.grid(row=3, column=0)
                reverse_label.grid(row= 0, column=0)
                self.reverse_check_button.grid(row=0, column=1)
                pan_text.grid(row=1, column=0)
                pan_slider.grid(row=1, column=1)
                self.last_channel = self.channel_var.get()
                self.options.protocol("WM_DELETE_WINDOW", self.options.withdraw)

                self.options.withdraw()
            def change_slider(self, e):
                print(self.pan.get())
            
            
            def show_options(self, e):
                self.options.deiconify()
                print(self.clip.file_name)
            
            def update_channel(self, var_name, index, mode):
                try:
                    new_channel = self.channel_var.get()

                    if new_channel != self.last_channel:
                        if self.clip in mixer.channels[self.last_channel].clips:
                            mixer.channels[self.last_channel].clips.remove(self.clip)
                        if self.clip not in mixer.channels[new_channel].clips:
                            mixer.channels[new_channel].clips.append(self.clip)
                        print(new_channel)
                        self.last_channel = new_channel
                except Exception as e:
                    print("Det finns inte så många kanaler")


    def canvasx_real_x(self, x):
        return (x-self.origin_x)/self.zoom_x
    def real_x_canvasx(self,x): # x = (canvasx-self.origin_x)/self.zoom_x -> self.zoom_x * x + self.origin_x = canvasx
        return self.zoom_x*x+self.origin_x
    def canvasy_real_y(self,y):

        return (y-self.origin_y)/self.zoom_y
    def real_y_canvasy(self,y):
        return self.zoom_y*y+self.origin_y
    def real_x_minutes(self,x):
        return 4*x/(middle.cell_width)/bpm_var.get()
    

    def horizontal_scroll(self,*args):
        self.canvas.xview(*args)
        self.marker_canvas.xview(*args)

    def vertical_scroll(self, *args):
        self.canvas.yview(*args)
        self.track_info_canvas.yview(*args)

    def update_scrollregion(self):
        x0,y0,x1,y1 = self.real_x_canvasx(0), self.real_y_canvasy(0), self.real_x_canvasx(self.beats*self.cell_width), self.real_y_canvasy(self.cell_height*self.rows)

        self.canvas.configure(scrollregion=(x0,y0,x1,y1))
        self.marker_canvas.configure(scrollregion=(x0, 0, x1, self.timeline_height))
        self.track_info_canvas.configure(scrollregion=(0, y0, self.track_info_width, y1)) # Denna tog mig 1000 år av lidande och smärta, ändra ALDRIG!
        
    def ctrl_down(self, event):
        self.ctrl_pressed = True

    def ctrl_up(self, event):
        self.ctrl_pressed = False

    def alt_down(self, event):
        self.alt_pressed = True

    def alt_up(self, event):
        self.alt_pressed = False
    def draw_timeline(self):
        loop = range(0, self.beats)
        self.marker_canvas.delete("timeline")
        self.timeline_background = self.marker_canvas.create_rectangle(0, 0, self.cell_width*self.beats, self.timeline_height, fill=colors["timeline_background"], tags=("timeline", "bbox"))
        
        for i in loop:
            xpos = i*self.cell_width
            self.marker_canvas.create_text(xpos+1, 7, text=i+1, fill=colors["marker_text"], font=("Helvetica", 8), tags=("timeline", "bbox"), anchor="w")

    def draw_grid(self):
        grid_line_thickness = 1
        self.canvas.delete("grid", "background")

        line_height = self.cell_height*self.rows
        line_width = self.cell_width*self.beats
        
        # self.grid_background = self.canvas.create_rectangle(0, 0, line_width, line_height, fill="#547792",tags=("background", "scaleable"))
        for i in range(0, self.rows+1):
            y_pos = i*self.cell_height
            self.canvas.create_line(0, y_pos, line_width, y_pos, fill=colors["bar_lines"], tags=("grid", "scaleable", "bbox"), width=grid_line_thickness)

            self.track_info_canvas.create_line(0, y_pos, self.track_info_width, y_pos, fill=colors["bar_lines"], tags=("scaleable", "bbox"), width=grid_line_thickness)
            if i!= self.rows:
                custom_widgets.EditableText(canvas=  self.track_info_canvas, text=i+1, x=self.track_info_width/2, y=y_pos, wrap_length=70)
            
        for i in range(self.beats+1):
            x_pos=i*self.cell_width
            self.canvas.create_line(x_pos, 0, x_pos, line_height, fill=colors["bar_lines"], tags=("grid", "scaleable", "bbox"), width=grid_line_thickness)
        
        for i in range(self.beats):
            for e in range(1, self.lines_per_bar):
                x_pos =  i*self.cell_width+(self.cell_width*(e/self.lines_per_bar))
                self.canvas.create_line(x_pos, 0, x_pos, line_height, fill=colors["beat_lines"], tags=("grid", "scaleable", "bbox"), width=grid_line_thickness)
        self.update_scrollregion()

        self.marker = self.Marker(playlist=self, head_canvas=self.marker_canvas, grid_canvas=self.canvas, tid_var=timer.var)
        self.canvas.tag_raise(self.marker.line, "grid")
                      
    def draw_canvas(self, rows = None, beats = None):
        self.draw_timeline()
        self.draw_grid()

    def focus_canvas(self, event):
        self.canvas.focus_set()
        self.canvas.lift()

    def rescale_canvas(self, e=None):
        self.canvas.focus_set()

        if self.ctrl_pressed:
            if e.delta > 0:
                zoom = min(self.zoom_in, self.max_zoom_x/self.zoom_x)
            else:
                zoom = max(self.zoom_out, self.min_zoom_x/self.zoom_x)
            
            self.zoom_x *= zoom

            self.mouse = self.canvas.canvasx(e.x)

            self.origin_x = ((self.origin_x - self.mouse) * zoom + self.mouse) # Tog mig tussssen år att lösa för tänkte inte på att man kunde använda matte.  

            self.canvas.scale("scaleable", self.mouse, 0, zoom, 1)
            self.marker_canvas.scale("timeline", self.mouse, 0, zoom, 1)
   
        elif self.alt_pressed:
            if e.delta > 0:
                zoom = min(self.zoom_in, self.max_zoom_y/self.zoom_y)
            else:
                zoom = max(self.zoom_out, self.min_zoom_y/self.zoom_y)
            self.zoom_y *= zoom

            scaling_point = self.canvas.canvasy(0)
            self.origin_y = (self.origin_y-scaling_point)*zoom + scaling_point
            self.canvas.scale("scaleable", 0, scaling_point, 1, zoom)
            self.track_info_canvas.scale("scaleable",0,scaling_point,1,zoom)
        
        self.update_scrollregion()
    
if __name__ == "__main__":
    
    root.option_add('*tearOff', False)
    root.title("Musicmakerpro")
    root.minsize(600, 600)
    bpm_var = IntVar(value=140)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    topframe = ttk.Frame(root, style="Top.TFrame")
    side_tree_frame = ttk.Frame(root)
    side_options_frame = ttk.Frame(root, style="TreeOptions.TFrame")
    middle_frame = ttk.Frame(root, style="Middle.TFrame")
    
    topframe.grid(row = 0, column=1, sticky="new")
    side_options_frame.grid(row=0, column=0, sticky = "NSEW")
    middle_frame.grid(row=1, column=1, sticky="NSEW")
    side_tree_frame.grid(row=1, column=0, sticky = "NSEW")
    
    side_tree_frame.rowconfigure(0, weight=1)

    Träd_instance = Träd(side_tree_frame, side_options_frame)
    meny = Meny(Träd_instance)
    top_bar = Top(topframe, global_root=root)
    middle = Middle(middle_frame)

    bpm_var.trace_add("write", lambda *args: clip_change_width_all())
    print(style.layout("Vertical.TScale"))
    root.mainloop()