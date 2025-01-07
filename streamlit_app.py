import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time

# Misty II camera URL
CAMERA_URL = "http://192.168.0.149/api/cameras/rgb"

# Fetch the image from the Misty API
def fetch_camera_image():
    try:
        response = requests.get(CAMERA_URL)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            st.error("Error fetching camera image: HTTP {}".format(response.status_code))
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Misty: {e}")
        return None

# Streamlit interface
st.title("Misty II Camera Feed")

# Create a placeholder to update the image
image_placeholder = st.empty()

# Fetch and display images continuously
while True:
    image = fetch_camera_image()
    if image:
        image_placeholder.image(image, caption="Misty II Camera Feed", use_column_width=True)
    time.sleep(1)  # Wait for 1 second before fetching the next image
    st.experimental_rerun()  # Refresh the Streamlit app to update the image
