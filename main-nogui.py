import os
import time
import requests
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to monitor
video_folder = "C:\Videos\League" # CHANGE TO YOUR VIDEO FOLDER
# Directory to store sorted videos
sorted_folder = "C:\Videos\League\sorted" # CHANGE TO YOUR DESTINATION FOLDER
# Riot ID Game Name
riot_id_game_name = "abc#abc"  # REPLACE WITH YOUR INGAME NAME

# URL for the League of Legends Live Client Data API
event_data_url = "https://127.0.0.1:2999/liveclientdata/eventdata"
all_game_data_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".mp4"):  # Adjust for your video file type
            print(f"New video file detected: {event.src_path}")
            sort_video(event.src_path)

def get_character_name():
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

def sort_video(file_path):
    try:
        # Get the character name
        character_name = get_character_name()
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
            event_folder = os.path.join(sorted_folder, latest_event)
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

if __name__ == "__main__":
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, video_folder, recursive=False)
    observer.start()
    
    print(f"Monitoring {video_folder} for new videos...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
