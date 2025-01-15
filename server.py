from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__)

# Path to the summarizer folder on the laptop
summarizer_dir = "refined"

# Set to keep track of already sent files
sent_files = set()

# Function to get the list of files in the summarizer folder
def get_summarizer_files():
    return os.listdir(summarizer_dir)

# Endpoint to get the next file
@app.route('/get_next_summarizer_file', methods=['GET'])
def get_next_summarizer_file():
    # Get the current files in the summarizer folder
    files = get_summarizer_files()

    if files:
        # Filter out files that have already been sent
        new_files = [file for file in files if file not in sent_files]

        if new_files:
            # Get the first unsent file in the directory
            file_path = os.path.join(summarizer_dir, new_files[0])

            # Send the full URL to the Raspberry Pi (including scheme and host)
            file_url = f"http://{request.host}/download/{new_files[0]}"  # Modify the URL to point to the /download endpoint

            # Mark this file as sent
            sent_files.add(new_files[0])

            return jsonify({'file_url': file_url}), 200
        else:
            # If no new files are available, return a "no new file" response
            return jsonify({'message': 'No new file available'}), 404
    else:
        # If no files exist in the folder, return a "no new file" response
        return jsonify({'message': 'No files in the folder'}), 404

# Endpoint to serve files from the summarizer folder
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Make sure the file exists in the summarizer folder
    if os.path.exists(os.path.join(summarizer_dir, filename)):
        return send_from_directory(summarizer_dir, filename)
    else:
        return jsonify({'message': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
