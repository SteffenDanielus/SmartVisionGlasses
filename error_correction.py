import os
import openai
from openai import OpenAI
import re

# Set your OpenAI API key

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define directories
summarizer_dir = "summarizer"
refined_dir = "refined"
os.makedirs(refined_dir, exist_ok=True)

def refine_text_with_openai(input_text):
    """
    Refine the text using OpenAI's GPT-3.5-Turbo to replace missing words,
    correct errors, and improve coherence while preserving the original length and meaning.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert text editor. Fill in missing words, correct grammar and spelling, and make the text as clear as possible. Give one output that is the most logical."
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            max_tokens=2048,
            temperature=0.7
        )
        refined_text = response.choices[0].message.content
        return refined_text
    except Exception as e:
        print(f"Error refining text: {e}")
        return input_text  # Return original text if refinement fails

def is_gibberish(text):
    """
    Simple heuristic to determine if the text is gibberish. 
    A text is considered gibberish if it contains a high proportion of non-alphabetic characters
    or lacks enough meaningful words.
    """
    # Remove non-alphabetic characters and check if too many remain
    non_alpha_ratio = len(re.findall(r'[^a-zA-Z\s]', text)) / len(text)
    
    # If non-alphabetic characters are too frequent, consider it gibberish
    if non_alpha_ratio > 0.5:  # Threshold can be adjusted based on testing
        return True
    
    # Optionally, check for words with regular expression (you can adjust the word criteria)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)  # Find words with at least 3 letters
    if len(words) / len(text.split()) < 0.2:  # Less than 20% of words are valid, consider gibberish
        return True

    return False

# Get the latest 3 .txt files from the summarizer directory
txt_files = [f for f in os.listdir(summarizer_dir) if f.endswith('.txt')]
txt_files.sort(key=lambda x: os.path.getmtime(os.path.join(summarizer_dir, x)), reverse=True)

# If there are fewer than 3 files, adjust the list
files_to_process = txt_files[:3]

if len(files_to_process) < 3:
    print(f"Warning: Less than 3 .txt files found. Using the available files.")

# Read the contents of the selected files
combined_text = ""
for filename in files_to_process:
    input_path = os.path.join(summarizer_dir, filename)

    with open(input_path, "r", encoding="utf-8") as file:
        input_text = file.read()

    # Check if the text is gibberish before sending it to OpenAI
    if is_gibberish(input_text):
        print(f"Skipping gibberish file: {filename}")
        continue  # Skip the file if it's gibberish
    
    print(f"Adding content of {filename} to prompt.")
    combined_text += f"\n\n---\n\n{input_text}  # Appending separator for clarity."

# If there is combined content, send it for refinement
if combined_text:
    print("Sending combined text to OpenAI for refinement...")
    
    # Refine the combined text
    refined_text = refine_text_with_openai(combined_text)
    
    # Save the refined text
    output_path = os.path.join(refined_dir, "refined_combined_text.txt")
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(refined_text)
    
    print(f"Refined text saved to: {output_path}")
else:
    print("No meaningful content to process.")