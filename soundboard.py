import tkinter as tk
import pyaudio
import wave
import threading
import keyboard

# Manually set the device indices for output (headphones)
HEADPHONES_DEVICE_INDEX = 5  # Set the index of your headphones (or speakers) here
VIRTUAL_MIC_DEVICE_INDEX = 6  # Set the index of your virtual mic (VB-Cable, VoiceMeeter, etc.)

# Global volume level
volume_level = 1  # Default full volume

# Automatically detect the microphone (input device)
def get_microphone_device_index():
    p = pyaudio.PyAudio()
    
    # Try to find a device with input channels (microphone)
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info["maxInputChannels"] > 0:  # This means the device is a microphone
            p.terminate()
            return i
    
    p.terminate()
    return None  # Return None if no microphone is found

# Function to play sound through headphones (output) and virtual mic
def play_sound_through_devices(sound_file):
    global volume_level
    chunk = 1024  # Buffer size
    p = pyaudio.PyAudio()

    # Automatically detect the microphone
    mic_device_index = get_microphone_device_index()
    if mic_device_index is None:
        print("Microphone not found!")
        return

    # Open WAV file
    wf = wave.open(sound_file, 'rb')

    try:
        # Open audio stream for headphones (output)
        stream_speakers = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=HEADPHONES_DEVICE_INDEX
        )
    except OSError as e:
        print(f"Error opening headphones stream: {e}")
        p.terminate()
        return

    try:
        # Open audio stream for virtual microphone (VB-Cable or VoiceMeeter)
        stream_virtual_mic = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=VIRTUAL_MIC_DEVICE_INDEX  # Set the virtual mic device here
        )
    except OSError as e:
        print(f"Error opening virtual microphone stream: {e}")
        stream_speakers.close()
        p.terminate()
        return

    # Read and play audio data with volume control
    data = wf.readframes(chunk)
    while data:
        adjusted_data = bytearray(data)  # Convert data to mutable array
        for i in range(0, len(adjusted_data), 2):  # Adjust volume (16-bit audio)
            sample = int.from_bytes(adjusted_data[i:i+2], 'little', signed=True)
            sample = int(sample * volume_level)  # Apply volume scaling
            sample = max(min(sample, 32767), -32768)  # Prevent clipping
            adjusted_data[i:i+2] = sample.to_bytes(2, 'little', signed=True)
        
        # Play sound through both headphones and virtual microphone
        stream_speakers.write(bytes(adjusted_data))
        stream_virtual_mic.write(bytes(adjusted_data))
        
        data = wf.readframes(chunk)

    # Clean up
    stream_speakers.stop_stream()
    stream_virtual_mic.stop_stream()
    stream_speakers.close()
    stream_virtual_mic.close()
    p.terminate()

# Function to stop sound
def stop_sound():
    print("Stopping sound is not directly supported in PyAudio with wave playback.")

# Function to adjust volume (with a minimum value to avoid zero volume)
def set_volume(value):
    global volume_level
    volume_level = max(float(value), 0.1)  # Ensure volume is never zero (minimum 0.1)

# Function to play sound in a separate thread (so GUI doesn't freeze)
def play_sound(sound_file):
    threading.Thread(target=play_sound_through_devices, args=(sound_file,)).start()

# Create GUI window
root = tk.Tk()
root.title("Soundboard (Plays Through Mic and Speakers)")
root.geometry("500x700")

# Define sound files (update with your paths)
sounds = {
    "bob": ("bobponja.wav", "1"),
    "oof": ("oof.wav", "2"),
    "codz": ("codzombie.wav", "3"),
    "getout": ("getout.wav", "4"),
    "goku": ("gokuprowler.wav", "5"),
    "STFU": ("shutthefuckup.wav", "6"),
    "yummers": ("yummers.wav", "7"),
    "coming": ("coming.wav", "8"),
    "yipee": ("yipee.wav", "9"),
    "albion": ("albion.wav", "0"),
    "Gwa": ("Gwa.wav", "ñ"),
    "Chad": ("gigachad.wav", "-"),
    "yao": ("yao.wav", "."),
    "chavo": ("chavo.wav", ","),
    "cronica": ("cronica.wav", ","),
}

# Create buttons for each sound
for sound_name, (file, key) in sounds.items():
    btn = tk.Button(root, text=f"{sound_name} (Key: {key})", command=lambda f=file: play_sound(f), height=2, width=15)
    btn.pack(pady=9)
    root.bind(key, lambda event, f=file: play_sound(f))  # Bind keys

# Stop Button
stop_btn = tk.Button(root, text="STOP", command=stop_sound, height=2, width=15, bg="red", fg="white")
stop_btn.pack(pady=9)

# Volume Control Slider
volume_label = tk.Label(root, text="Volume")
volume_label.pack()
volume_slider = tk.Scale(root, from_=0, to=1, resolution=0.1, orient="horizontal", command=set_volume)
volume_slider.set(0.2)  # Default volume at max
volume_slider.pack()

# Function to listen for global key presses
def listen_for_keys():
    for sound_name, (file, key) in sounds.items():
        # Listen for the keypress globally
        keyboard.add_hotkey(key, play_sound, args=(file,))

# Start the key listener in a separate thread
threading.Thread(target=listen_for_keys, daemon=True).start()

# Run the GUI
root.mainloop()