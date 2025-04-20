import pyaudio

# List available devices and print their indices
p = pyaudio.PyAudio()

# List all devices
for i in range(p.get_device_count()):
    dev_info = p.get_device_info_by_index(i)
    print(f"Device {i}: {dev_info['name']}")

import wave

# Open the audio file
with wave.open('oof.wav', 'rb') as wf:
    num_channels = wf.getnchannels()
    print(f"Number of channels: {num_channels}")

p.terminate()