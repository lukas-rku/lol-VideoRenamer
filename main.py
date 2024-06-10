from datetime import datetime
import os
import time
import threading
import requests
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, messagebox

# URLs for the League of Legends Live Client Data API
event_data_url = "https://127.0.0.1:2999/liveclientdata/eventdata"
all_game_data_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

# Configuration object to store user settings
config = {
    "video_folder": "",
    "sorted_folder": "",
    "riot_id_game_name": "",
}

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".mp4"):  # Adjust for your video file type
            print(f"New video file detected: {event.src_path}")
            sort_video(event.src_path, config)

def get_character_name(riot_id_game_name):
    try:
        print(f"Fetching all game data from {all_game_data_url}")
        response = requests.get(all_game_data_url, verify=False)
        response.raise_for_status()
        all_game_data = response.json()
        
        for player in all_game_data.get("allPlayers", []):
            if player.get("summonerName") == riot_id_game_name:
                character_name = player.get("championName")
                print(f"Found character name: {character_name}")
                return character_name
        
        print("Character name not found.")
    except requests.RequestException as e:
        print(f"Failed to fetch all game data: {e}")
    
    return None

def sort_video(file_path, config):
    try:
        # Get the character name
        character_name = get_character_name(config["riot_id_game_name"])
        if not character_name:
            print("Skipping file sorting due to missing character name.")
            return

        # Get the latest event data with SSL verification disabled
        print(f"Fetching event data from {event_data_url}")
        response = requests.get(event_data_url, verify=False)
        response.raise_for_status()
        events = response.json().get("Events", [])
        
        if events:
            latest_event = events[-1]["EventName"]
            print(f"Latest event: {latest_event}")
            
            # Create the event folder if it doesn't exist
            event_folder = os.path.join(config["sorted_folder"], latest_event)
            if not os.path.exists(event_folder):
                os.makedirs(event_folder, exist_ok=True)
                print(f"Created folder: {event_folder}")
            
            # Generate new file names with character name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file_name = f"{character_name}_{timestamp}.mp4"
            destination_path = os.path.join(event_folder, new_file_name)
            print(f"Moving file from {file_path} to {destination_path}")
            shutil.move(file_path, destination_path)
            print(f"Moved {file_path} to {destination_path}")

            # Check for corresponding .m4a file and move it if exists
            audio_file_path = file_path.replace(".mp4", ".m4a")
            if os.path.exists(audio_file_path):
                new_audio_file_name = f"{character_name}_{timestamp}.m4a"
                audio_destination_path = os.path.join(event_folder, new_audio_file_name)
                print(f"Moving audio file from {audio_file_path} to {audio_destination_path}")
                shutil.move(audio_file_path, audio_destination_path)
                print(f"Moved {audio_file_path} to {audio_destination_path}")
        else:
            print("No events found.")
    except requests.RequestException as e:
        print(f"Failed to fetch event data: {e}")
    except Exception as e:
        print(f"Failed to sort video: {e}")

def start_monitoring():
    global observer
    video_folder = config["video_folder"]
    sorted_folder = config["sorted_folder"]
    riot_id_game_name = config["riot_id_game_name"]

    if not os.path.exists(video_folder):
        messagebox.showerror("Error", "Video folder does not exist.")
        return
    if not os.path.exists(sorted_folder):
        messagebox.showerror("Error", "Sorted folder does not exist.")
        return
    if not riot_id_game_name:
        messagebox.showerror("Error", "Riot ID cannot be empty.")
        return

    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, video_folder, recursive=False)
    observer.start()
    
    print(f"Monitoring {video_folder} for new videos...")

    start_button.config(text="Stop Monitoring", command=stop_monitoring)

    while monitoring:
        time.sleep(1)

def stop_monitoring():
    global monitoring
    monitoring = False
    observer.stop()
    observer.join()
    start_button.config(text="Start Monitoring", command=initiate_monitoring)
    print("Stopped monitoring.")

def initiate_monitoring():
    global monitoring
    monitoring = True
    monitoring_thread = threading.Thread(target=start_monitoring)
    monitoring_thread.start()

def browse_video_folder():
    folder = filedialog.askdirectory()
    if folder:
        video_folder_entry.delete(0, tk.END)
        video_folder_entry.insert(0, folder)
        config["video_folder"] = folder

def browse_sorted_folder():
    folder = filedialog.askdirectory()
    if folder:
        sorted_folder_entry.delete(0, tk.END)
        sorted_folder_entry.insert(0, folder)
        config["sorted_folder"] = folder

def set_riot_id():
    riot_id = riot_id_entry.get()
    if riot_id:
        config["riot_id_game_name"] = riot_id
    else:
        messagebox.showerror("Error", "Riot ID cannot be empty.")

def on_closing():
    global monitoring
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        monitoring = False
        if observer:
            observer.stop()
            observer.join()
        root.destroy()

# Create the GUI
root = tk.Tk()
root.title("League of Legends Video Sorter")

tk.Label(root, text="Video Folder:").grid(row=0, column=0, padx=10, pady=5)
video_folder_entry = tk.Entry(root, width=50)
video_folder_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_video_folder).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Sorted Folder:").grid(row=1, column=0, padx=10, pady=5)
sorted_folder_entry = tk.Entry(root, width=50)
sorted_folder_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_sorted_folder).grid(row=1, column=2, padx=10, pady=5)

tk.Button(root, text="Set Riot ID", command=set_riot_id).grid(row=2, column=2, padx=10, pady=5)
riot_id_entry = tk.Entry(root, width=50)
riot_id_entry.grid(row=2, column=1, padx=10, pady=5)

start_button = tk.Button(root, text="Start Monitoring", command=initiate_monitoring)
start_button.grid(row=3, column=0, columnspan=3, pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()