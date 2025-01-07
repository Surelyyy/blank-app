import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import websocket
import json
import threading
import time
import requests
from datetime import datetime
import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import base64
import logging
import random
import tensorflow as tf
from openCV import cv2 
import numpy as np

import os
print(os.path.exists("model_unquant.tflite"))  # Should return True if the file exists

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Adjust the level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", 
)

# Replace with your Misty's IP address
misty_ip = "192.168.0.149"

round = 0
# Global variable to store bump sensor state
bump_sensor_state = {"frontLeft": False, "frontRight": False}


# Generate a unique filename
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"NumberImage.jpg"

# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path=r"C:\Users\rifqi\Downloads\Workshop 2\converted_tflite\model_unquant.tflite")
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Define emotion labels (adjust based on your model)
emotion_labels = ["Angry", "Disgusted", "Fearful", "Happy", "Neutral", "Sad", "Surprised"]

def recognize_emotion(image):
    # Preprocess the image for the model
    img = cv2.resize(image, (48, 48))  # Resize to model input size
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    img = img.astype(np.float32) / 255.0  # Normalize
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # Get the predicted emotion
    emotion_index = np.argmax(output_data[0])
    return emotion_labels[emotion_index]

def capture_and_process_image():
    # Existing code to capture image from Misty
    take_picture_url = f'http://{misty_ip}/api/cameras/rgb'
    take_picture_params = {
        "Base64": "false",
        "FileName": "captured_image.jpg",
        "Width": 2048,
        "Height": 1536,
        "DisplayOnScreen": "false",
        "OverwriteExisting": "true"
    }
    response = requests.get(take_picture_url, params=take_picture_params)
    if response.status_code == 200:
        with open("captured_image.jpg", "wb") as f:
            f.write(response.content)
        print("Image captured successfully.")
        
        # Load the captured image for emotion recognition
        image = cv2.imread("captured_image.jpg")
        
        # Recognize emotion
        detected_emotion = recognize_emotion(image)
        print(f"Detected emotion: {detected_emotion}")

        # React to the detected emotion
        react_to_emotion(detected_emotion)
    else:
        print("Failed to capture image:", response.text)

def react_to_emotion(emotion):
    if emotion == "Happy":
        make_misty_speak("I see you're happy! Let's continue!")
        change_misty_led(0, 255, 0)  # Green LED for happy
    elif emotion == "Sad":
        make_misty_speak("I see you're sad. Would you like to play a game to cheer up?")
        change_misty_led(255, 0, 0)  # Red LED for sad
    elif emotion == "Angry":
        make_misty_speak("I sense some anger. Let's take a deep breath together.")
        change_misty_led(255, 165, 0)  # Orange LED for angry
    elif emotion == "Surprise":
        make_misty_speak("Wow! You look surprised!")
        change_misty_led(255, 255, 0)  # Yellow LED for surprise
    elif emotion == "Fear":
        make_misty_speak("It's okay to feel scared sometimes. I'm here for you.")
        change_misty_led(128, 0, 128)  # Purple LED for fear
    elif emotion == "Neutral":
        make_misty_speak("You seem calm. Let's continue our activity.")
        change_misty_led(0, 0, 255)  # Blue LED for neutral
    else:
        make_misty_speak("I couldn't recognize your emotion.")

def make_misty_speak(text):
    url = f'http://{misty_ip}/api/tts/speak'

def capture_and_process_image():
    # Existing code to capture image from Misty
    take_picture_url = f'http://{misty_ip}/api/cameras/rgb'
    # ... (rest of the existing code)

    # Load the captured image for emotion recognition
    image = cv2.imread(file_name)
    
    # Recognize emotion
    detected_emotion = recognize_emotion(image)
    print(f"Detected emotion: {detected_emotion}")

    # Use the detected emotion in your interaction logic
    if detected_emotion == "Happy":
        make_misty_speak("I see you're happy! Let's continue!")
    elif detected_emotion == "Sad":
        make_misty_speak("I see you're sad. Would you like to play a game to cheer up?")
    # Add more conditions based on detected emotions

def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img = img.filter(ImageFilter.MedianFilter())  # Apply a median filter
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Enhance contrast
    img = ImageOps.invert(img)  # Invert colors
    img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Apply thresholding
    return img

# Specify the root folder containing the subfolders
root_folder = r"C:\Users\rifqi\Downloads\Workshop 2\number_dataset"  # <--- Update path here

# Output folder for processed images
processed_output_folder = "processed_images"
if not os.path.exists(processed_output_folder):
    os.makedirs(processed_output_folder)

# Check if the root folder exists
if not os.path.exists(root_folder):
    print(f"Root folder not found: {root_folder}")
else:
    # Loop through each subfolder in the root folder
    for subfolder_name in os.listdir(root_folder):
        subfolder_path = os.path.join(root_folder, subfolder_name)
        
        # Check if it's a folder
        if os.path.isdir(subfolder_path):
            print(f"Processing folder: {subfolder_path}")
            
            # Loop through each file in the subfolder
            for file_name in os.listdir(subfolder_path):
                # Check if the file is a supported image format
                if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):  # <--- Support more formats
                    image_path = os.path.join(subfolder_path, file_name)
                    print(f"Processing image: {image_path}")
                    
                    # Preprocess and save the processed image
                    try:
                        processed_image = preprocess_image(image_path)
                        # Save the processed image in the output folder
                        processed_image.save(os.path.join(processed_output_folder, f"{subfolder_name}_processed_{file_name}"))
                    except Exception as e:
                        print(f"Error processing {file_name}: {e}")

def detect_number(image_path):
    img = preprocess_image(image_path)
    print(img)
    custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text.strip()

def make_misty_speak(text):
    url = f'http://{misty_ip}/api/tts/speak'
    payload = {"text": text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Misty is speaking:", text)
    else:
        print("Failed to make Misty speak:", response.text)

def crop_center(image_path, crop_width, crop_height):
    img = Image.open(image_path)
    width, height = img.size
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = (width + crop_width) // 2
    bottom = (height + crop_height) // 2
    img = img.crop((left, top, right, bottom))
    img.save(image_path)
    print(f"Image cropped to center and saved: {image_path}")
    return image_path


def sharpen_image(image_path):
    img = Image.open(image_path)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)  # Increase sharpness
    img.save(image_path)
    print(f"Image sharpened and saved: {image_path}")
    return image_path

def display_capimage(image_name):
    endpoint = f"http://{misty_ip}/api/images/display"
    payload = {
        "FileName": image_name
    }
    response = requests.post(endpoint, json=payload)
    if response.status_code == 200:
        print(f"Image '{image_name}' displayed on Misty's screen.")
    else:
        print(f"Failed to display image '{image_name}': {response.text}")

def capture_and_process_image():
    take_picture_url = f'http://{misty_ip}/api/cameras/rgb'
    take_picture_params = {
        "Base64": "false",
        "FileName": file_name,
        "Width": 2048,
        "Height": 1536,
        "DisplayOnScreen": "false",
        "OverwriteExisting": "true"
    }
    response = requests.get(take_picture_url, params=take_picture_params)
    if response.status_code == 200:
        print(f"Image captured successfully and displayed on Misty's screen. Filename: '{file_name}'")
        try:
            result = response.json()
            if 'result' in result:
                print("Image details:", result['result'])
            else:
                print("Unexpected response format:", result)
        except requests.exceptions.JSONDecodeError:
            print("Received non-JSON response. This might be the image data.")
        with open(file_name, "wb") as f:
            f.write(response.content)
        print(f"Image '{file_name}' saved locally.")
    else:
        print("Failed to capture image:", response.text)
    if response.headers.get('Content-Type') != 'image/jpeg':
        print("Attempting to retrieve the image separately...")
        get_image_url = f'http://{misty_ip}/api/images'
        get_image_params = {
            'FileName': file_name,
            'Base64': 'false'
        }
        image_response = requests.get(get_image_url, params=get_image_params, stream=True)
        if image_response.status_code == 200:
            with open(file_name, "wb") as f:
                for chunk in image_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Image '{file_name}' retrieved and saved locally.")
        else:
            print("Failed to retrieve image from Misty:", image_response.text)


    # Define the crop dimensions for the center of the image
    crop_width, crop_height = 1000, 1000  # Adjust these values as needed
    cropped_image_path = crop_center(file_name, crop_width, crop_height)
    # Sharpen the cropped image
    sharpened_image_path = sharpen_image(cropped_image_path)
    detected_number = detect_number(sharpened_image_path)
    print(f"Detected number: {detected_number}")
    global round
    if round == 0 and detected_number == "1":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 2")
        capture_and_process_image()  # Proceed to the next round
    elif round == 1 and detected_number == "2":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 3")
        capture_and_process_image()  # Proceed to the next round
    elif round == 2 and detected_number == "3":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 4")
        capture_and_process_image()  # Proceed to the next round
    elif round == 3 and detected_number == "4":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 5")
        capture_and_process_image()  # Proceed to the next round
    elif round == 4 and detected_number == "5":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 6")
        capture_and_process_image()  # Proceed to the next round
        
    elif round == 5 and detected_number == "6":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 7")
        capture_and_process_image()  # Proceed to the next round
        
    elif round == 6 and detected_number == "7":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 8")
        capture_and_process_image()  # Proceed to the next round      
    elif round == 7 and detected_number == "8":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 9")
        capture_and_process_image()  # Proceed to the next round  
    elif round == 8 and detected_number == "9":
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("Excellent! You are correct")
        round += 1
        make_misty_speak("Let's continue with the next round")
        make_misty_speak("Can you show me number 10")
        capture_and_process_image()  # Proceed to the next round  
    elif round == 9 and detected_number == "10":
        make_misty_speak("Excellent! You are correct")
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav ")
        make_misty_speak("That was fun. Thank you for playing with me. Bye")
        change_misty_led(255, 0, 0)
        save_misty_audio("newvoice1.mp3", "https://www.dreamenglish.com/Dream%20English%20Traditional%20ABC01.mp3")
        play_misty_audio("newvoice1.mp3")
        time.sleep(1)  # Ensure the audio is saved before playing
        misty_dance("dance_music.mp3")
        
    else:
        display_image("e_EcstacyHilarious.jpg")
        display_audio("s_PhraseUhOh.wav")
        make_misty_speak("Please try again")
        capture_and_process_image()  # Recapture the image if the number is incorrect

def move_arm(arm, position, velocity):
    endpoint = f"http://{misty_ip}/api/arms"
    payload = {
        "Arm": arm,
        "Position": position,
        "Velocity": velocity
    }
    requests.post(endpoint, json=payload)

def display_audio(audio_name):
    endpoint = f"http://{misty_ip}/api/audio/play"
    payload = {
        "FileName": audio_name
    }
    requests.post(endpoint, json=payload)
    
def display_image(image_name):
    endpoint = f"http://{misty_ip}/api/images/display"
    payload = {
        "FileName": image_name
    }
    requests.post(endpoint, json=payload)

def move_head(pitch, roll, yaw, velocity):
    endpoint = f"http://{misty_ip}/api/head"
    payload = {
        "Pitch": pitch,
        "Roll": roll,
        "Yaw": yaw,
        "Velocity": velocity
    }
    requests.post(endpoint, json=payload)  
        
# WebSocket message handler
def on_message(ws, message):
    global bump_sensor_state
    print(f"WebSocket message received: {message}")  # Debugging statement
    data = json.loads(message)
    if "message" in data and "sensorId" in data["message"]:  # Check for sensorId instead of sensorName
        sensor_id = data["message"]["sensorId"]
        is_contacted = data["message"]["isContacted"]
        print(f"Received bump sensor event: {sensor_id} - Contacted: {is_contacted}")
        if sensor_id == "bfl":
            bump_sensor_state["frontLeft"] = is_contacted
        elif sensor_id == "bfr":
            bump_sensor_state["frontRight"] = is_contacted

# WebSocket error handler
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# WebSocket close handler
def on_close(ws):
    print("WebSocket connection closed")

# WebSocket open handler
def on_open(ws):
    print("WebSocket connection opened")
    subscribe_to_bump_sensors(ws)

def subscribe_to_bump_sensors(ws):
    message = {
        "Operation": "subscribe",
        "Type": "BumpSensor",
        "DebounceMs": 100,
        "EventName": "BumpSensor"
    }
    ws.send(json.dumps(message))
    print("Subscribed to bump sensors")

# Function to change Misty's LED color
def change_misty_led(r, g, b):
    url = f'http://{misty_ip}/api/led'
    payload = {"red": r, "green": g, "blue": b}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Misty LED color changed to: ({r}, {g}, {b})")
    else:
        print("Failed to change Misty LED color:", response.text)

# Function to save audio to Misty
def save_misty_audio(audio_name, audio_url):
    response = requests.get(audio_url)
    if response.status_code == 200:
        encoded = base64.b64encode(response.content).decode("utf8")
        url = f'http://{misty_ip}/api/audio'
        payload = {
            "FileName": audio_name,
            "Data": encoded,
            "ImmediatelyApply": False,
            "OverwriteExisting": True
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Audio {audio_name} saved to Misty")
        else:
            print("Failed to save audio to Misty:", response.text)
    else:
        print("Failed to download audio:", response.text)

# Function to play audio on Misty
def play_misty_audio(audio_name):
    url = f'http://{misty_ip}/api/audio/play'
    payload = {"FileName": audio_name}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Playing audio {audio_name} on Misty")
    else:
        print("Failed to play audio on Misty:", response.text)

def misty_dance(audio_name): 
    # Play the music
    play_misty_audio(audio_name)
    
    # Start dancing
    for _ in range(34):  # Repeat the dance moves 5 times
        #random led  
        change_misty_led(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        move_arm("left", -50, 100)  # Move left arm up
        move_arm("right", 50, 100)  # Move right arm down
        move_head(20, 0, 20, 50)    # Tilt head
        change_misty_led(255, 0, 0) # Change LED to red
        time.sleep(0.5)             # Pause for 0.5 seconds

        #random led  
        change_misty_led(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        move_arm("left", 50, 100)   # Move left arm down
        move_arm("right", -50, 100) # Move right arm up
        move_head(-20, 0, -20, 50)  # Tilt head
        change_misty_led(0, 0, 255) # Change LED to blue
        time.sleep(0.5)             # Pause for 0.5 seconds

    # Reset Misty's pose
    move_arm("left", 0, 90)
    move_arm("right", 0, 90)
    move_head(0, 0, 0, 50)
    change_misty_led(0, 255, 0)  # Set LED to green

    make_misty_speak("Woohoo! That was fun! Thank you for dancing with me! goodbye!")
    time.sleep(5.0)  
    display_audio("s_PhraseByeBye.wav")

# Function to wait for bump sensor input
def wait_for_bump_input():
    print("Waiting for bump sensor input...")
    while True:
        if bump_sensor_state["frontLeft"]:
            bump_sensor_state["frontLeft"] = False  # Reset state after detection
            return 'yes'
        elif bump_sensor_state["frontRight"]:
            bump_sensor_state["frontRight"] = False  # Reset state after detection
            return 'no'
        time.sleep(0.1)

# Function to handle user input
def handle_user_input():
    user_choice = wait_for_bump_input()
    if user_choice == 'yes':
        display_image("e_Joy.jpg")
        display_audio("s_Awe.wav")
        make_misty_speak("You pressed Yes. Let's start learning numbers!")
        make_misty_speak("Can you show me number 1")
        capture_and_process_image()
    elif user_choice == 'no':
        display_image("e_EcstacyHilarious.jpg")
        display_audio("s_Sadness2.wav")
        make_misty_speak("You pressed No. Maybe we can play later!")
        make_misty_speak("That was fun. Thank you for playing with me. Bye")
        display_image("e_Surprise.jpg")
        change_misty_led(255, 0, 0)
        save_misty_audio("newvoice1.mp3", "https://www.dreamenglish.com/Dream%20English%20Traditional%20ABC01.mp3")
        play_misty_audio("newvoice1.mp3")
        time.sleep(1)  # Ensure the audio is saved before playing
        misty_dance("dance_music.mp3")
    

# Initialize and start interaction
def initialize_interaction():
    make_misty_speak("Hello, My name is MISTY.")
    display_image("e_Joy.jpg") 
    # Wave hand and move head
    move_arm("right", -80, 50)  # Raise right arm
    move_head(-20, 0, 0, 50)  # Tilt head slightly down
    time.sleep(1)
    move_arm("right", 0, 50)   # Lower right arm
    move_arm("left", -50, 100)   # Lower right arm
    move_head(0, 0, 0, 50)  # Return head to center
    make_misty_speak("Are you ready to learn numbers? Press the front left bump sensor for Yes, or the front right bump sensor for No.")
    handle_user_input()

# Start WebSocket connection
def start_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://{misty_ip}/pubsub",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    try:
        logging.info("Starting WebSocket thread...")
        websocket_thread = threading.Thread(target=start_websocket, daemon=True)
        websocket_thread.start()

        time.sleep(2)  # Wait for WebSocket connection to stabilize
        logging.info("Initializing Misty interaction...")
        initialize_interaction()
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    finally:
        # Ensure WebSocket and other threads are cleaned up
        logging.info("Exiting program.")
