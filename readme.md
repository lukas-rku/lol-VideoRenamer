# League of Legends Video Sorter

This is a Python script with a GUI that automatically sorts League of Legends gameplay videos based on the in-game events and champion played.

## Features
- Monitors a specified folder for new video files.
- Fetches information from the League of Legends client to determine the champion played and the latest in-game event.
- Creates folders based on the event type and sorts the videos within those folders.
- Optionally renames the video files with the champion name and timestamp.

## GUI
The script also includes a simple GUI that allows you to:
- Browse and set the video folder and sorted folder paths.
- Enter your League of Legends summoner name.
- Start and stop the video monitoring.

## Prerequisites
- Python 3
- Requests library (https://pypi.org/project/requests/)
- Watchdog library (https://python-watchdog.readthedocs.io/)
- tkinter library (included in most Python installations)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/league-of-legends-video-sorter.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage:
1. Run the script:
   ```bash
   python main.py
   ```
2. Set the following configurations in the GUI:
- Video Folder: The directory where your recorded videos are stored.
- Sorted Folder: The directory where you want your videos to be sorted.
- Riot ID: Your League of Legends in-game name (used for character identification).
3. Click "Start Monitoring" to begin monitoring the video folder for new videos.

## Note:
This script relies on the League of Legends Live Client Data API, which might be subject to changes in future updates.

## Disclaimer
This script is provided for educational purposes only and is not affiliated with Riot Games. Using this script may violate the League of Legends Terms of Service. Use it at your own risk.
