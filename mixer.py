from tkinter import *
from tkinter import ttk
from assets import *
import global_stuff
from logik_ljud.tid import timer
import numpy as np
import sounddevice as sd
import soundfile as sf
import time
sd.default.samplerate = global_stuff.SAMPLERATE
sd.default.blocksize = global_stuff.BLOCKSIZE
sd.default.channels = 2

last_selected_channel = None

class Mixer:


  def __init__(self): 
    self.root = root
    self.mixer = Toplevel(root)
    self.mixer_canvas= Canvas(self.mixer, background=colors["grid_background"])
    self.mixer_canvas.grid(row=0, column=0, sticky="NSEW")
    self.mixer.columnconfigure(0, weight=1)
    self.mixer.rowconfigure(0, weight=1)
    

    self.mixer.title("mixer")
    self.mixer.geometry("500x500")
    self.mixer.protocol("WM_DELETE_WINDOW", self.mixer.withdraw) # lägg till ()
    
    
    self.mixer.withdraw()
    self.create_channels()
  def show_mixer(self):
    self.mixer.deiconify()
  
  def create_channels(self):
    self.channels = {}
    self.master = self.Master(self, "Master", 80)
    self.channels.update({"mstr": self.master})
    
    for i in range(5):
      self.channels.update({str(i+1): self.Channel(self, f"Channel {i+1}", 50, i+1)})
    print(self.channels)
  
  class Channel:
    last_selected_channel = None
    class Effect:
        
        effects = ("None", "distortion", "bitcrush(6)", "tremelo", "highpass", "gain")
        def __init__(self, channel):
          
          effect_count = channel.effect_count
          self.master = channel.effects_frame
          self.effect = StringVar(value = "None")
          self.effect_slot = ttk.Combobox(self.master, values = self.effects, textvariable=self.effect, state="readonly")
          self.effect_slot.grid(row = effect_count, column=0, sticky="NSE")
          self.effect_slot.bind("<<ComboboxSelected>>", None)
          channel.effect_count +=1
        def process(self, audio):
            if self.effect.get() == "distortion":
                return self.apply_distortion(audio)
            elif self.effect.get() == "reverb":
                return self.apply_reverb(audio)
            elif self.effect.get() == "bitcrush(6)":
                return self.apply_bitcrusher(audio)
            elif self.effect.get() == "tremelo":
                return self.apply_tremolo(audio)
            elif self.effect.get() == "highpass":
                return self.apply_highpass(audio)
            elif self.effect.get() == "gain":
                return self.apply_gain(audio)
            
            return audio
        def apply_gain(self, audio, gain=2):
           return audio*gain
        def apply_distortion(self, audio):
            gain = 10.0
            distorted = np.tanh(audio * gain)
            return distorted
        def apply_bitcrusher(self, audio, bit_depth=6):
          max = 2 ** (bit_depth - 1)
          crushed = np.round(audio * max) / max
          return np.clip(crushed, -1.0, 1.0)
        def apply_tremolo(self, audio, rate_hz=30, samplerate=global_stuff.SAMPLERATE):
          t = np.arange(len(audio)) / samplerate
          lfo = 0.5 * (1 + np.sin(2 * np.pi * rate_hz * t))
          return audio * lfo[:, np.newaxis]
        def apply_highpass(self, audio, alpha=0.995):
          output = np.zeros_like(audio)
          output[1:] = audio[1:] - audio[:-1] + alpha * output[:-1]
          return output*3

        def apply_reverb(self, audio): # kanske göra, förmodligen inte.
           return audio
             


    
    def __init__(self, mixer, name, channel_width, index, relief = "raised"):
      
      print(name)
      self.clips = []
      self.index = index
      self.effects_shown = False
      self.mixer = mixer
      self.channel_width = channel_width
      self.name = StringVar(value=name)
      self.font = ("Helvitca", 12)

      self.num_frame = ttk.Frame(self.mixer.mixer_canvas, style="Mixer_top.TFrame")
      self.num_frame.grid(row=0, column=index, sticky="EW")
      self.num_frame.columnconfigure(0, weight=1)
      self.label = index
      ttk.Label(self.num_frame, text=self.label, font = self.font, foreground="white", style="Mixer.TLabel").grid()
      

      self.channel_frame = ttk.Frame(self.mixer.mixer_canvas, borderwidth=1, relief=relief)
      self.channel_frame.rowconfigure(0, weight=1)
      self.channel_frame.grid(row = 1, column=index, sticky="NS")

      self.effects_frame = ttk.Frame(self.mixer.mixer, borderwidth=1, relief= "raised")
      self.effects_frame.grid(row =0, column=1, sticky = "NSE")
      self.effects_frame.grid_remove()
      self.effect_count = 0
      self.effects = [self.Effect(self) for effect in range(5)]

      
      self.volume = DoubleVar(value=0.7)
      self.pan = 0
      self.volume_scale = ttk.Scale(self.channel_frame, orient=VERTICAL, variable= self.volume, from_=1, to=0)
      self.volume_scale.grid(row=0, column=1, sticky="NS")
      self.text_canvas = Canvas(self.channel_frame, width=self.channel_width, background=colors["timeline_background"])
      self.text_canvas.grid(row=0, column=0, rowspan=2)
      self.text_canvas.create_text(10,125, fill = "white", text=self.name.get(), angle = 90, font=('Helvetica', 12))
      self.text_canvas.bind("<Button-1>", self.show_effects)
      print(index)
      
      

    def get_chunk(self, frames, global_sample_position):
      mixed = np.zeros((frames, 2), dtype=np.float32)
      for clip in self.clips:
          mixed += clip.get_chunk(frames, global_sample_position)

      for effect in self.effects:
          mixed = effect.process(mixed)

      volume = self.volume.get()
      left = mixed[:, 0] * volume * (1 - self.pan)
      right = mixed[:, 1] * volume * (1 + self.pan)
      return np.column_stack((left, right))

      
    def show_effects(self, event):
      global last_selected_channel
      
      if last_selected_channel and self != last_selected_channel:
          last_selected_channel.effects_shown = False
          last_selected_channel.channel_frame.configure(style="TFrame")
          last_selected_channel.effects_frame.grid_remove()
      last_selected_channel = self

      if not self.effects_shown:
        
        self.effects_frame.grid()
        print(self.clips)
        self.effects_shown = True
        self.channel_frame.configure(style="Selected.TFrame")
  class Master(Channel):
    def __init__(self, mixer, name, channel_width):
        
        super().__init__(mixer, name, channel_width, relief="ridge", index=0)
        self.update_marker_func = None
        self.stream = None
        self.start_time = None
        self.global_start = 0
        self.samples = global_stuff.SAFETY_MARGIN
        self.icons = load_icons()
    def audio_callback(self, outdata, frames, time, status):
    
      if self.start_time is None:
          self.start_time = self.stream.time

      if not global_stuff.playing:
          outdata[:] = np.zeros((frames, 2), dtype=np.float32)
          return

      current_time = self.stream.time - self.start_time
      self.samples+=frames
      global_sample_position = global_stuff.play_start_sample + self.samples

      chunk = self.get_mastered(frames, global_sample_position)
      outdata[:] = chunk
      
      tid = current_time + self.global_start
      timer.update_timer(tid)
      self.update_marker_func(tid)
    def get_mastered(self, frames, global_sample_position):
        mixed = np.zeros((frames, 2), dtype=np.float32)
        for name, channel in self.mixer.channels.items():
          mixed += channel.get_chunk(frames, global_sample_position)
        mixed = np.clip(mixed, -1.0, 1.0) 
        volume = self.volume.get()
        left = mixed[:, 0] * volume * (1 - self.pan)
        right = mixed[:, 1] * volume * (1 + self.pan)
        return np.column_stack((left, right))

      

    def play(self, knapp):
      self.samples = global_stuff.SAFETY_MARGIN

      try:
         
        self.global_start = timer.time
        global_stuff.play_start_sample = round(global_stuff.minutes_samples(timer.time/60))
        if self.stream is None:
          self.stream = sd.OutputStream(callback=self.audio_callback)
        
        if global_stuff.playing:
           knapp.configure(image = self.icons["play"])
           self.stream.stop()
           global_stuff.playing = False
           self.start_time = None

        elif not global_stuff.playing:
          knapp.configure(image = self.icons["playing"])
          self.stream.start()
          global_stuff.playing = True
        print("playing: ", global_stuff.playing)
      except Exception as e:
         print(e)
    
    def reset(self):
      pass
     
if __name__ == "__main__":
  root.title("manager")
  mixer = Mixer()
  ttk.Button(root, command = mixer.show_mixer).grid()
  root.mainloop()