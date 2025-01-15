import requests
import os
import time

server_url = "http://192.168.1.239:5000"

download_dir = "received_files"
os.makedirs(download_dir, exist_ok=True)
processing_flag = "processing.flag"

def process_files():
    while True:
        if os.path.exists(processing_flag):
            print("TTS is speaking. Pausing file processing.")
            while os.path.exists(processing_flag):  # Wait for TTS to finish
                time.sleep(1)
            print("Resuming file processing...")

        # Add your file processing logic here
        print("Processing files...")
        time.sleep(2)


def download_file(file_url):
    """Download a file from the provided URL."""
    filename = file_url.split("/")[-1]
    file_path = os.path.join(download_dir, filename)

    # Check if the file already exists before downloading
    if not os.path.exists(file_path):
        try:
            response = requests.get(file_url)
            response.raise_for_status()  # Raise an error for bad HTTP status codes

            # Save the file
            with open(file_path, 'wb') as file:
                file.write(response.content)

            print(f"File {filename} downloaded successfully!")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
    else:
        print(f"File {filename} already exists, skipping download.")

def get_next_file():
    """Get the next available file from the server if a new one is available."""
    while True:
        try:
            response = requests.get(f"{server_url}/get_next_summarizer_file")
            if response.status_code == 200:
                # File is available for download
                file_url = response.json().get('file_url')
                download_file(file_url)
            else:
                print("No new file available. Retrying...")
                time.sleep(5)  # Wait for 5 seconds before retrying
        except Exception as e:
            print(f"Error while trying to fetch a new file: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    get_next_file()
