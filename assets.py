from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import global_stuff
import traceback
colors = {"scroll_bar_background" : "#5e626e", "grid_background": "#547792", "timeline_background": "#213448", "marker_text": "#ECEFCA",
        "bar_lines": "black", "beat_lines": "#3B5A6E", "track_info_background": "#D3D3D3", "topbar_background": "#4A5D6F", "marker_color": "#138027", "top_bar_text":"white", "scale_handle":"#a2779f"}


root = Tk()

def report_callback_exception(exc, val, tb):
    traceback.print_exception(exc, val, tb)

root.report_callback_exception = report_callback_exception

global_stuff.init_tk_variables()
style = ttk.Style()
style.theme_use("clam")

style.layout("Vertical.TScrollbar", [
('Vertical.Scrollbar.trough', {
    'children': [
        ('Vertical.Scrollbar.thumb', {'unit': '1', 'sticky': 'nswe'})
    ],
    'sticky': 'ns'
})])
style.layout("Horizontal.TScrollbar", [
('Horizontal.Scrollbar.trough', {
    'children': [
        ('Horizontal.Scrollbar.thumb', {'unit': '1', 'sticky': 'nswe'})
    ],
    'sticky': 'we'    })])
style.configure("Top.TFrame", background=colors["topbar_background"])
style.configure("Middle.TFrame", background=colors["timeline_background"])
style.configure("TScrollbar", background=colors["scroll_bar_background"], troughcolor=colors["scroll_bar_background"], lightcolor = colors["scroll_bar_background"], gripcount = 0)
style.map("TScrollbar", lightcolor=[("active", colors["scroll_bar_background"])], background=[("active", colors["scroll_bar_background"])])

style.configure("Cool.Treeview",
                background="#2d2e3b",
                foreground="white",
                fieldbackground="#2d2e3b")
style.configure("TreeOptions.TFrame", background=colors["topbar_background"], borderwidth=0)

style.configure("TCheckbutton", padding=0, borderwidth=0, relief="")

# Normal knapp
style.configure("TButton", focuscolor="", borderwidth=0)
style.map("TButton", background=[("!active", colors["topbar_background"]), ("active", colors["beat_lines"])])

style.configure("Selected.TButton", focuscolor="")
style.map("Selected.TButton", background=[("!active", colors["scale_handle"]), ("active", colors["scale_handle"])])

style.configure("TLabel", foreground=colors["top_bar_text"], background="black")
style.configure("TRadiobutton", focuscolor="none", foreground = colors["top_bar_text"])
style.map("TRadiobutton", background=[("active", colors["topbar_background"]), ("!disabled", colors["topbar_background"])])

style.configure("Selected.TFrame", background ="red", borderwidth=0)
style.configure("Mixer.TLabel", background=colors["grid_background"])
style.configure("TFrame", borderwidth=0)

style.configure("TLabel", background="black")
style.configure("Mixer_top.TFrame", background=colors["grid_background"], borderwidth=0)

style.configure("Horizontal.TScale", lightcolor =colors["scale_handle"], darkcolor=colors["scale_handle"], troughcolor="dim gray", background=colors["scale_handle"])
style.configure("Vertical.TScale", lightcolor =colors["scale_handle"], darkcolor=colors["scale_handle"], troughcolor="dim gray", background=colors["scale_handle"])

style.map("Vertical.TScale", background = [("active", colors["scale_handle"])])
style.map("Horizontal.TScale", background = [("active", colors["scale_handle"]), ("!active", colors["scale_handle"])])
style.map("TMenubutton", background =[("!active", colors["topbar_background"]), ("active", colors["topbar_background"])], foreground=[("!active", "white"), ("active", "white")])
style.configure("TMenuButton", border=0)
style.configure("clipoptions.TFrame", background=colors["topbar_background"])



def knapp_img_create(path, size=(32,32)):
    bild = Image.open(path)
    if size == "image":
       return ImageTk.PhotoImage(bild)
    return ImageTk.PhotoImage(bild.resize(size))

def load_icons():
  return{
  "piano" : knapp_img_create("ikoner/piano.png"),
  "mixer" : knapp_img_create("ikoner/mixer.png"),
  "sequencer": knapp_img_create("ikoner/sequencer.png"),
  "play" :knapp_img_create("ikoner/play.png"),
  "playing":knapp_img_create("ikoner/playing.png"),
  "stop" :knapp_img_create("ikoner/stop_playback.png"),
  "file": knapp_img_create("ikoner/file.png", (16,16)),
  "pen":knapp_img_create("ikoner/pen.png", (16,16)),
  "bucket":knapp_img_create("ikoner/bucket.png", (16,16)),
  "marker": knapp_img_create("ikoner/marker.png", "image"),
  "slicer":knapp_img_create("ikoner/slicer.png", (16,16)),
  "hover_cursor": "hand2"
}

if __name__ == "__main__":
   root = Tk()
   icons = load_icons()
   button = Button(root, image = icons["piano"])
   button.pack()
   root.mainloop()