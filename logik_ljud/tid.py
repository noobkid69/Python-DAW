import time
from tkinter import *
from tkinter import ttk
from assets import load_icons, root


class Timer():
  
  def __init__(self):
    self.icons = load_icons()
    self.var = StringVar(value="0:0.00")
    self.elapsed_time = 0
    self.time = 0

  def update_timer(self, seconds):
    timer.time = seconds
    self.var.set(f"{int(seconds)//60}:{(seconds%60):.2f}")
    

  def clear_timer(self, button = None):
    button.configure(image = self.icons["play"])
    self.start_time = 0
    self.elapsed_time = 0
    self.var.set("0:0.00")
timer = Timer()