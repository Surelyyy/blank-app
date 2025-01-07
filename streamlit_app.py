import streamlit as st
import requests
import cv2
import numpy as np
import io

# Function to check if Misty II is connected
def check_connection(ip):
    url = f"http://{ip}/api/v2"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to connect to Misty II: Status Code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Misty II: {e}")
        return False

# Function to get the camera feed from Misty II
def get_misty_camera_feed(ip):
    camera_url = f"http://{ip}/api/v2/camera/current"  # Check if this is the correct endpoint for a snapshot
    try:
        response = requests.get(camera_url, timeout=5)
        if response.status_code == 200:
            # Convert byte content to image format
            image_data = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            if img is not None:
                return img
            else:
                st.error("Failed to decode image")
                return None
        else:
            st.error(f"Failed to fetch camera feed, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching camera feed: {e}")
        return None

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
