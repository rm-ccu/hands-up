"""
Live gesture recognition demo.

Reads live frames off the ESP32, runs them through the trained model, and prints
the predicted gesture + confidence in real time.

Install deps: pip install pyserial torch numpy
"""

import time

import numpy as np
import serial
import torch
import torch.nn as nn

PORT = "/"  
BAUD = 115200
GRID = 8
CLIP_MM = 3000.0

# Define the same model architecture used for training so we can load the weights
class GestureNet(nn.Module):
    def __init__(self, n_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, n_classes),
        )

    def forward(self, x):
        return self.net(x)

# Load the trained model and labels
checkpoint = torch.load("gesture_model.pt")
labels = checkpoint["labels"]
model = GestureNet(len(labels))
model.load_state_dict(checkpoint["model_state"])
model.eval()

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

# Read live frames from the ESP32 and make predictions
print("Live gesture recognition running -- Ctrl+C to stop\n")
try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line or line == "READY":
            continue
        try:
            values = [int(v) for v in line.split(",")]
        except ValueError:
            continue
        if len(values) != GRID * GRID:
            continue

        arr = np.array(values, dtype=np.float32).reshape(1, -1) / CLIP_MM
        with torch.no_grad():
            probs = torch.softmax(model(torch.tensor(arr)), dim=1)[0]
            pred_idx = probs.argmax().item()

        print(f"\r{labels[pred_idx]:10s} ({probs[pred_idx]:.0%})   ", end="", flush=True)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    ser.close()
