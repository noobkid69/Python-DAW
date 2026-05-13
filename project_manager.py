import json
from tkinter import simpledialog
from pathlib import Path
import global_stuff
audioclips = []

current_sample_rate = 44100
current_project = None
empty_project = {"Folder":None, "Project_sample_rate": 44100, "Name":"untitled"}
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projekt"
print("BASE_DIR: ", BASE_DIR)

def load_project(root, name = None): # ska kunna acceptera både sträng med namn och rå data i form av dictionary.
    if name:
        root.title(f"Musicmakerpro | {name}")
    else: 
        root.title(f"Musicmakerpro | {empty_project['Name']}")
def save_project(träd, bpm_var):
    global current_project
    name = current_project
    if current_project is None:
        name = simpledialog.askstring("Inget projekt hittat. Spara projekt", "Ange projektnamn:")
        if not name:
            return
    
    current_project = name
    try:
        project_data = {

            "Name": name, 
            "Folder": träd.file_manager.folder_name, 
            "Project_sample_rate": current_sample_rate, 
            "bpm": bpm_var.get(),
            "snap": global_stuff.snap_var_x.get(),
            "clips": [ {
                "x": clip.x,
                "y": clip.y,
                "group": clip.group,
                "width": clip.width,
                "volume": clip.clip_options.volume.get(),
                "pan": clip.clip_options.pan.get()
            } for clip in audioclips] 
            }
    except Exception as e:
        print(f"Error gathering project data: {e}")
        return
    
    project_folder = PROJECTS_DIR / name
    project_folder.mkdir(parents=True, exist_ok=True)
    try:
        with open (f"{project_folder}/data.json", mode="w", encoding="utf-8") as file:
            json.dump(project_data, file)
    except Exception as e:
        print(f"Error saving project: {e}")
    print("saving project: ", name)