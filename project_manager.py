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

def load_project(root, middle, name = None): # ska kunna acceptera både sträng med namn och rå data i form av dictionary.
    try:
        clear_project(root)
        if name is None:
            root.title(f"Musicmakerpro | {empty_project['Name']}")
            return
        root.title(f"Musicmakerpro | {name}")
        with open(PROJECTS_DIR/name/"data.json", mode="r", encoding="utf-8") as file:
            print(name)
            data = json.load(file)
        print(data)
        for clip_data in data["clips"]:
            new_clip = middle.AudioClip(
                x=clip_data["x"],
                y=clip_data["y"],
                audio=clip_data["audio"],
                group=clip_data["group"],
                start_time=clip_data["start_time"],
                end_time=clip_data["end_time"],
                volume=clip_data.get("volume", 60),
                pan=clip_data.get("pan", 0.0)
            )
            audioclips.append(new_clip)
    except Exception as e:
        print(f"Error loading project: {e}")

def clear_project(root):
    print(audioclips)
    for clip in audioclips[:]:
        clip.delete_clip()
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
                "audio": clip.audio,
                "x": clip.x,
                "y": clip.y,
                "group": clip.group,
                "width": clip.width,
                "volume": clip.clip_options.volume.get(),
                "pan": clip.clip_options.pan.get(),
                "start_time": clip.start_time,
                "end_time": clip.end_time
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