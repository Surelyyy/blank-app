import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Misty II camera URL (ensure this matches your actual endpoint)
CAMERA_URL = "http://192.168.0.149/api/cameras/rgb"

# Fetch the image from the Misty API
def fetch_camera_image():
    response = requests.get(CAMERA_URL)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        st.error("Failed to fetch the image from Misty II camera.")
        return None

# Streamlit interface
st.title("Misty II Camera Feed")

# Display the camera image
image = fetch_camera_image()
if image:
    st.image(image, caption="Misty II Camera Feed", use_column_width=True)

