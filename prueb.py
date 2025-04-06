import os
import requests
# URL of the image
url = "https://api.dicebear.com/7.x/bottts/svg?seed=banking-agent"

# Directory to save the image
image_dir = "Images"
os.makedirs(image_dir, exist_ok=True)  # Create Images directory if it doesn’t exist

# File path to save the image
image_path = os.path.join(image_dir, "bot_avatar.svg")

# Download the image
response = requests.get(url)
if response.status_code == 200:
    with open(image_path, "wb") as f:
        f.write(response.content)
    print(f"Image downloaded and saved as {image_path}")
else:
    print("Failed to download image")