import pyttsx3
import sounddevice as sd
import numpy as np
import serial
import time

# Initialize pyttsx3
engine = pyttsx3.init()

# Talkimg Rate  
engine.setProperty('rate', 120) 
# Set volume 
engine.setProperty('volume', 1.0) 

# Using female voice 
voice_id = "com.apple.voice.compact.en-IE.Moira"
engine.setProperty('voice', voice_id) 

# Initialize serial communication with Arduino
ser = serial.Serial('/dev/tty.usbmodem1101', 9600)  # Update with your port name

# Constants for servo movement range
SERVO_MIN_ANGLE = -90
SERVO_MAX_ANGLE = 90
MOVING_AVERAGE_WINDOW = 15

# Map amplitude to servo position
def amplitude_to_servo(amplitude):
    # Scale amplitude to servo range
    scaled_amplitude = SERVO_MIN_ANGLE + (amplitude * (SERVO_MAX_ANGLE - SERVO_MIN_ANGLE))
    # Constrain within servo range
    servo_position = int(np.clip(scaled_amplitude, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE))
    return servo_position

# Buffer for smoothing
amplitude_buffer = []

# Process audio in real-time
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio callback status: {status}")
    try:
        # Convert audio data to numpy array
        audio_data = np.abs(indata[:, 0])  # Using only one channel (mono)
        # Calculate RMS (root mean square) amplitude
        rms_amplitude = np.sqrt(np.mean(audio_data ** 2))
        # New RMS amplitude to buffer
        amplitude_buffer.append(rms_amplitude)
        # Only last N amplitudes (moving average window)
        if len(amplitude_buffer) > MOVING_AVERAGE_WINDOW:
            amplitude_buffer.pop(0)
        # Moving average of amplitude
        smoothed_amplitude = np.mean(amplitude_buffer)
        # Normalize amplitude (scale to 0-1)
        normalized_amplitude = smoothed_amplitude / np.max(amplitude_buffer)
        # Map normalized amplitude to servo position
        servo_position = amplitude_to_servo(normalized_amplitude)
        # Printing
        print(f"RMS Amplitude: {rms_amplitude}, Smoothed: {smoothed_amplitude}, Servo Position: {servo_position}")
        # Servo position to Arduino
        ser.write(f"{servo_position}\n".encode())
    except Exception as e:
        print(f"Error in audio processing: {e}")

# Speak text and process audio simultaneously
def speak_text(text):
    # Start audio stream
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
        # Speak text
        engine.say(text)
        engine.runAndWait()

# Test 
speak_text("Introducing Veronica, your intelligent AI assistant. Equipped with advanced facial recognition and object detection capabilities, Veronica can seamlessly track human faces and identify various objects with precision. Additionally, she excels in engaging in natural, meaningful conversations, making her an invaluable partner in enhancing productivity, streamlining tasks, and providing insightful solutions. Whether you're managing complex workflows, analyzing data, or seeking creative inputs, Veronica is your reliable companion, dedicated to making your project a resounding success.")

# Close serial connection
ser.close()
