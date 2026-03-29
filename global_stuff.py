
from tkinter import StringVar, IntVar, DoubleVar
A4_FREQUENCY = 440.0
SAMPLERATE = 44100
BLOCKSIZE = 2048
SAFETY_MARGIN = -BLOCKSIZE
def format_tuning(*args):
    try:
        val = float(tuning_setting.get())
        tuning_display.set(f"{val:.2f}")
    except ValueError:
        pass
    
tuning_setting = DoubleVar(value=0)
tuning_display = StringVar()
playing = False
group = None
groups = {}
snap_var_x = StringVar()
allowed_file_types = (".mp3", ".wav")
play_start_sample = None
dragged_item = None
pen_selected = False
bucket_selected = None
slicer_selected = False
files = {}
def minutes_samples(minutes):
        return minutes*SAMPLERATE*60    # sr = samples/sekunder, samples = sr*sekunder = sr*minuter*60
