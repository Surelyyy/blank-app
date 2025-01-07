import streamlit as st
import requests
import cv2
import numpy as np

# Function to check if Misty II is connected
def check_connection(ip):
    url = f"http://{ip}/api/v2"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            st.error("Failed to connect to Misty II")
            return False
    except requests.exceptions.RequestException:
        st.error("Error connecting to Misty II")
        return False

# Function to get the camera feed from Misty II
def get_misty_camera_feed(ip):
    # Assuming the API provides the camera feed endpoint
    camera_url = f"http://{ip}/api/v2/camera/current"  # This URL may change depending on Misty's API
    while True:
        # Fetch image from the camera
        response = requests.get(camera_url)
        if response.status_code == 200:
            # Convert to OpenCV format (BGR)
            nparr = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                return img
        else:
            st.error("Error fetching camera feed")
            break

# Streamlit UI to input IP address
st.title("Misty II Camera Feed")

ip_address = st.text_input("Enter Misty II IP address:")

if ip_address:
    if check_connection(ip_address):
        st.write(f"Successfully connected to Misty II at {ip_address}")
        
        # Display the camera feed
        frame = get_misty_camera_feed(ip_address)
        if frame is not None:
            st.image(frame, channels="BGR")
        else:
            st.warning("No camera feed available")
    else:
        st.warning("Please enter a valid IP address.")
