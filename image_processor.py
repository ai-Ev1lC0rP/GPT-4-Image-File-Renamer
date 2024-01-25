# Import necessary libraries
import os
import base64
import requests
import argparse
from PIL import Image
import tkinter as tk
from tkinter import ttk
import threading

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to communicate with the GPT-4 Vision API
def process_images(file_paths, progress_callback):
    api_key = os.getenv('OPENAI_API_KEY')  # Retrieve the API key from the environment variable
    if not api_key:
        raise ValueError("API key not found in environment variables.")
    processed_images = []

    for file_path in file_paths:
        # Getting the base64 string
        base64_image = encode_image(file_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Examine the provided image closely, and create a Windows-compatible file name that succinctly but accurately describes the image's content. Ensure that the file name adheres to Windows naming conventions by excluding special characters like < > : \" / \\ | ? *, and keep the length within 255 characters. The response should consist solely of this proposed file name, without any additional explanation or content."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Ensure the request was successful
        processed_images.append(response.json())  # Process the response to get the suggested name for the image

    progress_callback(processed_images)  # Call the callback function to update progress

# Function to rename the images based on the API's output
def rename_images(file_paths, processed_images):
    for file_path, processed_image in zip(file_paths, processed_images):
        # Parse the response to extract the suggested name for the image
        suggested_name = processed_image['choices'][0]['message']['content']
        # Extract only the suggested filename, including stripping text after the period . file extension
        suggested_name = suggested_name.split('\n')[-1].strip('"').split('.')[0]
        # Construct the new file path
        new_file_path = os.path.join(os.path.dirname(file_path), suggested_name + os.path.splitext(file_path)[1])
        # Rename the image file
        os.rename(file_path, new_file_path)

# Function to handle the progress of the image processing
def handle_progress(processed_images):
    rename_images(file_paths, processed_images)
    root.quit()  # Close the Tkinter window after processing is complete

# Main function to process images from command-line arguments
def main():
    global file_paths, root
    parser = argparse.ArgumentParser(description='Process images using GPT-4 Vision API.')
    parser.add_argument('file_paths', metavar='N', type=str, nargs='+',
                        help='an image file path to process')
    args = parser.parse_args()
    file_paths = args.file_paths

    if file_paths:
        # Create the Tkinter window and center it on the screen
        root = tk.Tk()
        root.title("Processing Images")
        root.geometry("300x100")
        root.eval('tk::PlaceWindow . center')
        ttk.Label(root, text="Renaming images with GPT-4 Vision, please wait...").pack(pady=10)
        progress = ttk.Progressbar(root, length=200, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()

        # Run the image processing in a separate thread
        processing_thread = threading.Thread(target=process_images, args=(file_paths, handle_progress))
        processing_thread.start()

        # Start the Tkinter loop
        root.mainloop()
    else:
        print("No images provided.")

if __name__ == "__main__":
    main()