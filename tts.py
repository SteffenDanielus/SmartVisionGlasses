import os
import time
import pygame
from gtts import gTTS
from io import BytesIO

# Path to the folder containing received files
received_files_dir = "received_files"

# Function to get the most recent file from the received_files folder
def get_most_recent_file(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # If the directory is empty, return None
    if not files:
        return None

    # Get the full path for each file
    full_paths = [os.path.join(directory, file) for file in files]

    # Sort the files by their modification time (most recent first)
    latest_file = max(full_paths, key=os.path.getmtime)
    
    return latest_file

def text_to_speech(text):
    """Convert the text to speech and play it."""
    tts = gTTS(text)

    # Create a BytesIO object to store the audio
    mp3_fp = BytesIO()

    tts.write_to_fp(mp3_fp)

    mp3_fp.seek(0)  # Go to the beginning of the BytesIO stream
    with open("temp_audio.mp3", "wb") as f:
        f.write(mp3_fp.read())

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the mp3 file into pygame
    pygame.mixer.music.load("temp_audio.mp3")
    
    # Play the sound
    pygame.mixer.music.play()

    # Wait for the sound to finish before continuing
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def monitor_folder_and_convert_to_speech(directory):
    """Monitor the directory for new files and convert the most recent file to speech."""
    last_processed_file = None
    last_spoken_file = None  # To keep track of the last spoken file

    while True:
        # Get the most recent file in the directory
        recent_file = get_most_recent_file(directory)

        # If there is a new file that has not been processed yet
        if recent_file and recent_file != last_processed_file:
            last_processed_file = recent_file

            # Read the content of the new file
            with open(recent_file, "r", encoding="utf-8") as file:
                text = file.read()

            # Check if the new file is the same as the last spoken file
            if recent_file != last_spoken_file:
                # Convert the text to speech
                text_to_speech(text)
                print(f"Processed and spoke content of {recent_file}")

                # Update the last spoken file
                last_spoken_file = recent_file
            else:
                print(f"Skipping file {recent_file} because it has already been spoken.")

        # Sleep for a while before checking for new files
        time.sleep(1)

if __name__ == "__main__":
    monitor_folder_and_convert_to_speech(received_files_dir)
