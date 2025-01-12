import cv2
import pytesseract
import time
import os
import shutil
from collections import deque
from transformers import T5ForConditionalGeneration, T5Tokenizer
import threading
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

# Replace with your DroidCam IP and port
droidcam_url = "http://192.168.1.233:4747/video"

# Initialize video capture
cap = cv2.VideoCapture(droidcam_url)

# Set the Tesseract executable path if needed (e.g., for Windows users)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
frames_dir = "frames"
output_dir = "output"
better_output_dir = "better_output"
summarizer_dir = "summarizer"
os.makedirs(frames_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(better_output_dir, exist_ok=True)
os.makedirs(summarizer_dir, exist_ok=True)  # Ensure summarizer directory exists

# Load T5 model and tokenizer for text comparison
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Time control variable
last_processed_time = 0
frame_interval = 3  # Process one frame every 3 seconds
recent_texts = deque(maxlen=5)

# For the video feed in another thread
frame = None
frame_lock = threading.Lock()

# Variables to detect if the frame has changed significantly
prev_frame = None
frame_change_threshold = 1000000  # Change threshold (adjust based on testing)

def get_text_embedding(text):
    """Generate an embedding for the text using the T5 model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model.encoder(input_ids=inputs["input_ids"]).last_hidden_state
    # Use the mean of the embeddings as the text representation
    embedding = outputs.mean(dim=1).squeeze().numpy()
    return embedding

def generate_coherence_score(text1, text2):
    """Generate a coherence score based on cosine similarity of embeddings."""
    embedding1 = get_text_embedding(text1)
    embedding2 = get_text_embedding(text2)
    
    # Compute cosine similarity between embeddings
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return similarity

def select_best_text():
    """Select the best text based on coherence using T5 embeddings."""
    # Get the last 5 files in the output folder
    output_files = sorted(os.listdir(output_dir), reverse=True)[:5]
    
    if len(output_files) < 2:
        return None  # Not enough files to compare

    best_score = -float('inf')
    best_text = None

    # Compare each file with each other to find the most coherent
    for i in range(len(output_files)):
        with open(os.path.join(output_dir, output_files[i]), "r", encoding="utf-8") as file1:
            text1 = file1.read()
            for j in range(i+1, len(output_files)):
                with open(os.path.join(output_dir, output_files[j]), "r", encoding="utf-8") as file2:
                    text2 = file2.read()
                    # Generate coherence score using cosine similarity
                    coherence_score = generate_coherence_score(text1, text2)
                    print(f"Coherence score between text {i} and text {j}: {coherence_score}")  # Debugging line
                    
                    # If similarity is higher, consider it the best
                    if coherence_score > best_score:
                        best_score = coherence_score
                        best_text = text1 if best_score == coherence_score else text2

    if best_text:
        print("Best text selected for summarization.")  # Debugging line
        return best_text
    return None

def capture_frames():
    """Capture frames from the video feed in a separate thread."""
    global frame, prev_frame
    while True:
        ret, captured_frame = cap.read()
        if not ret:
            print("Failed to retrieve frame.")
            break

        # Lock the frame to safely update it from the main thread
        with frame_lock:
            frame = captured_frame

            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Compute absolute difference between the current and previous frame
                frame_diff = cv2.absdiff(prev_frame, gray_frame)

                # Sum up the differences to calculate a score
                diff_sum = np.sum(frame_diff)

                # If the difference is smaller than the threshold, consider the frames as unchanged
                if diff_sum < frame_change_threshold:
                    print("No significant change detected in the frame.")
                    continue  # Skip processing this frame, no need to process further

            # Update the previous frame for the next iteration
            prev_frame = gray_frame

# Start the frame capture thread
capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

try:
    while True:
        # Wait for a frame to be captured
        with frame_lock:
            if frame is None:
                continue

            # Get current time
            current_time = time.time()

            # Save and process a frame every 3 seconds
            if current_time - last_processed_time >= frame_interval:
                last_processed_time = current_time

                # Save the frame to the frames directory
                frame_filename = f"frame_{int(current_time)}"
                frame_path = os.path.join(frames_dir, f"{frame_filename}.jpg")
                cv2.imwrite(frame_path, frame)

                # Convert frame to grayscale for better OCR performance
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Perform OCR using Tesseract
                text = pytesseract.image_to_string(gray_frame)

                # Print the detected text to the console
                if text.strip():
                    print(f"Detected Text from {frame_path}:\n{text}")

                    # Save the OCR result to a text file in the output directory
                    output_path = os.path.join(output_dir, f"{frame_filename}.txt")
                    with open(output_path, "w", encoding="utf-8") as text_file:
                        text_file.write(text)

                    # Add text to the recent texts deque
                    recent_texts.append(text)

                    # Check if we have 5 texts to evaluate
                    if len(recent_texts) == 5:
                        # Select the best text based on coherence
                        best_text = select_best_text()

                        if best_text:
                            # Save the best text to the summarizer directory
                            summary_filename = f"best_text_{int(time.time())}.txt"
                            best_text_path = os.path.join(summarizer_dir, summary_filename)
                            with open(best_text_path, "w", encoding="utf-8") as best_text_file:
                                best_text_file.write(best_text)
                            print(f"Best coherent text saved to {best_text_path}")

                            # Clear the deque after evaluation
                            recent_texts.clear()

            # Display the video feed
            cv2.imshow("DroidCam Feed", frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    # Clean up: delete the frames directory and its contents
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
        print("Deleted frames directory.")
