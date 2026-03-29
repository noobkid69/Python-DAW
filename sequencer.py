from tkinter import *
from tkinter import ttk
class Sequencer:
  def __init__(self, root):
    self.sequencer = Toplevel(root)
    self.sequencer.protocol("WM_DELETE_WINDOW", self.sequencer.withdraw)
    self.sequencer.withdraw()
    
    self.sequencer.title("Sequencer")
    self.sequencer.geometry("400x300")
    self.sequencer.minsize(300, 150)
    self.sequencer.columnconfigure(0, weight=1)
    self.sequencer.rowconfigure(1, weight=1)
    self.tracks_area = Canvas(self.sequencer)
    self.tracks_area.grid(row=1, column=0, sticky="NSEW")
    
    
    self.tracks_frame = ttk.Frame(self.tracks_area)
    self.tracks_frame.grid(sticky = "NSEW")

    self.tracks_window = self.tracks_area.create_window((0,0), window=self.tracks_frame, anchor="nw")
   

    
    self.track_options_area = ttk.Frame(self.sequencer, borderwidth=2, relief="groove")
    self.track_options_area.grid(row= 2, column=0, sticky = "SEW")
    self.track_options_area.columnconfigure(1, weight=1)

    
    
    self.track_manager = self.Track(self)
    self.update_scroll_region()
    self.scroll_bar_x = ttk.Scrollbar(self.track_options_area, orient = HORIZONTAL, command = self.tracks_area.xview)
    self.tracks_area.configure(xscrollcommand=self.scroll_bar_x.set)
    self.scroll_bar_x.grid(row = 0, column=1, sticky = "EW")

    
    

    self.options_manager = self.Track_options(self)
  def show_window(self):
    self.sequencer.deiconify()
    print("window shown")
  def update_scroll_region(self):
    self.sequencer.update_idletasks()
    self.tracks_area.configure(scrollregion=self.tracks_frame.bbox("all"))
  def create_track(self):
    self.Track(self)
    self.update_scroll_region()
 
  class Track:
    tracks = 0
    def __init__(self, seq):
      self.root = seq.tracks_frame
      
      self.__class__.tracks +=1
      self.row = self.__class__.tracks
      self.track_frame = Frame(self.root, borderwidth=1, relief="solid")
      self.track_frame.grid(row = self.row, column=0, pady=2, sticky="EW")
      
      self.track_frame.columnconfigure(2, weight=1)  
      self.root.columnconfigure(0, weight=1)
      self.channel = IntVar()
      
      self.button = ttk.Button(self.track_frame, text="Ljud", command = lambda:print("klickad"))
      self.c_selector = ttk.Spinbox(self.track_frame, from_=1, to=100, textvariable=self.channel, width=4, command=lambda: self.channel.get()) # TA INTE BORT KOMMANDOT, INGET VET VARFÖR DET FUNKAR MEN DET GÖR DET.
      self.c_selector.grid(column = 0, row = 0)

      self.beat_frame = ttk.Frame(self.track_frame, height=self.button.winfo_height())
      self.beat_frame.grid(column=2, row = 0, sticky="NSEW")
      self.button.grid(column=1, row = 0)
      
      self.button_manager = self.Track_button(self)
    class Track_button():
      buttons = 0
      color_tracker = True
      def __init__(self, track):
        self.track = track
        self.button_frame = track.beat_frame
        self.create_buttons()
      def create_buttons(self):
        for i in range(4*4*8):
          self.create_button(i)
      def create_button(self, index):
        self.index = index
        if self.buttons % 4 == 0:
          self.color_tracker = not self.color_tracker
        if not self.color_tracker:
          self.color = "#778899"
        else: 
          self.color = "#808080"
        self.button_var = BooleanVar(value=False)
        self.button = Checkbutton(self.button_frame, background=self.color, variable=self.button_var, indicatoron=False, width=1) # ÄNDRA INTE TILL TTK WIDGET DEN KLARAR INTE AV INDICATORON!!!!
        self.button.grid(row=0, column=self.buttons)
        self.buttons += 1
  class Track_options:
    def __init__(self, seq):
      self.frame = seq.track_options_area
      self.add_track = ttk.Button(self.frame, text = "+", command=seq.create_track)
      self.add_track.grid(row =0, column=0)

if __name__ == "__main__":
  root = Tk()
  sequencer = Sequencer(root)
  ttk.Button(root, command =sequencer.show_window, text = "show sequencer").grid()
  sequencer.show_window()
  root.mainloop()
  
