import requests

# Function to save audio to memory
def save_audio_to_local_file(audio_url, audio_path):
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open(audio_path, "wb") as audio_file:
            audio_file.write(response.content)
    else:
        raise Exception("Failed to retrieve audio data.")
    
# Function to save image to memory
def save_image_to_local_file(image_url, image_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, "wb") as image_file:
            image_file.write(response.content)
    else:
        raise Exception("Failed to retrieve image data.")