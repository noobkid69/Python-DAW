import json
from tkinter import simpledialog, IntVar, DoubleVar, StringVar, BooleanVar
from pathlib import Path
from tokenize import group

from sympy import root
import global_stuff
audioclips = []

current_sample_rate = 44100
current_project = None
empty_project = {"Folder":None, "Project_sample_rate": 44100, "Name":"untitled"}
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projekt"
print("BASE_DIR: ", BASE_DIR)

def load_project(root, middle, name = None, mixer = None): # ska kunna acceptera både sträng med namn och rå data i form av dictionary.
    try:
        clear_project(root)
        if name is None:
            root.title(f"Musicmakerpro | {empty_project['Name']}")
            return
        root.title(f"Musicmakerpro | {name}")
        with open(PROJECTS_DIR/name/"data.json", mode="r", encoding="utf-8") as file:
            data = json.load(file)
        global_stuff.groups = {group_name: [[], group[1], DoubleVar(master= root, value=group[2]), StringVar(master = root, value=group[3]), StringVar(master = root, value=group[4]), BooleanVar(master = root, value=group[5])] for group_name, group in data["groups"].items()}

        for clip_data in data["clips"]:
            new_clip = middle.AudioClip(
                x=clip_data["x"],
                y=clip_data["y"],
                audio=clip_data["audio"],
                group=clip_data["group"],
                start_time=clip_data["start_time"],
                end_time=clip_data["end_time"],
                volume=clip_data["volume"] if "volume" in clip_data else 0.6,
                pan=clip_data["pan"] if "pan" in clip_data else 0.0,
                channel=clip_data["individual_channel"] if "individual_channel" in clip_data else "mstr"
            )
            print(new_clip.volume)
            for group_name, group in global_stuff.groups.items():

                channel_var = group[4]
                reverse_var = group[5]

                if group[0]:
                    first_clip = group[0][0]
                    channel_var.trace_add("write", first_clip.update_group_channels)
                    reverse_var.trace_add("write", lambda *args, g=group: first_clip.reverse_audio(g, *args))

        mixer_data = data.get("mixer", {})
        for channel_name, channel_data in mixer_data.items():

            if channel_name not in mixer.channels:
                continue
            
            channel = mixer.channels[channel_name]

            channel.volume.set(channel_data.get("volume", 0.7))

            effects = channel_data.get("effects", [])

            for effect_obj, effect_name in zip(channel.effects, effects):
                effect_obj.effect.set(effect_name)
                
        root.after(100, lambda: global_stuff.snap_var_x.set(data["snap"]))
        root.after(100, lambda: global_stuff.bpm_var.set(data["bpm"]))

    except Exception as e:
        print(f"Error loading project: {e}")

def clear_project(root):
    global_stuff.groups.clear()
    for clip in audioclips[:]:
        clip.delete_clip()
    root.title(f"Musicmakerpro | {empty_project['Name']}")

def save_project(träd, bpm_var, mixer):
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
            "bpm": global_stuff.bpm_var.get(),
            "snap": global_stuff.snap_var_x.get(),
            "groups": {group_name: [[], global_stuff.groups[group_name][1], global_stuff.groups[group_name][2].get(), global_stuff.groups[group_name][3].get(), global_stuff.groups[group_name][4].get(), global_stuff.groups[group_name][5].get()] for group_name, group in global_stuff.groups.items()},
             "mixer": {name: {"volume": channel.volume.get(),"effects": [effect.effect.get() for effect in channel.effects]} for name, channel in mixer.channels.items()},
            "clips": [ {
                "audio": clip.audio,
                "x": clip.x,
                "y": clip.y,
                "group": clip.group,
                "individual_channel": clip.clip_options.channel_var.get() if clip.group is None else None,
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