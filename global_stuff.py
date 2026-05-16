
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
def init_tk_variables():
    global tuning_setting, tuning_display, snap_var_x, bpm_var
    tuning_setting = DoubleVar(value=0)
    tuning_display = StringVar()
    snap_var_x = StringVar()
    bpm_var = IntVar(value=140)
     
tuning_setting = None
tuning_display = None
snap_var_x = None
playing = False
group = None
groups = {}

allowed_file_types = (".mp3", ".wav")
play_start_sample = None
dragged_item = None
pen_selected = False
bucket_selected = None
slicer_selected = False
min_bpm, max_bpm = 40, 300
files = {}
def minutes_samples(minutes):
        return minutes*SAMPLERATE*60    # sr = samples/sekunder, samples = sr*sekunder = sr*minuter*60
