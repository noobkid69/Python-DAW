import json

current_sample_rate = 44100
current_project = "test"

empty_project = {"Folder":None, "Project_sample_rate": 44100, "Name":"untitled"}

def load_project(root, name = None): # ska kunna acceptera både sträng med namn och rå data i form av dictionary.
    if name:
        root.title(f"Musicmakerpro | {name}")
    else: 
        root.title(f"Musicmakerpro | {empty_project['Name']}")
def save_project(träd, name):
    project_data = {"Folder": träd.file_manager.folder_name, "Project_sample_rate": current_sample_rate, "channels": []}
    with open (f"./projekt/{name}/data.json", mode="w") as file:
        json.dump(project_data, file)