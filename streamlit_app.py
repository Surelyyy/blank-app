import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time
ngrok http 8501

# Misty II camera URL
CAMERA_URL = "http://192.168.0.149/api/cameras/rgb"

# Fetch the image from the Misty API
def fetch_camera_image():
    response = requests.get(CAMERA_URL)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None

# Streamlit interface
st.title("Misty II Camera Feed")

# Create a placeholder to update the image
image_placeholder = st.empty()

while True:
    image = fetch_camera_image()
    if image:
        image_placeholder.image(image, caption="Misty II Camera Feed", use_column_width=True)
    time.sleep(1)  # Wait for 1 second before fetching the next image
