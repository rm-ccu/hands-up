"""
Live heatmap of the VL53L8CX feed + keyboard-driven labeled data collection.

Controls (click the plot window first so it has keyboard focus):
  r / p / s / e -> start recording "rock" / "paper" / "scissors" / "empty"
  SPACE -> stop recording
  q -> save dataset to gesture_dataset.json and quit

install deps: pip install numpy matplotlib pyserial
"""

import json
import time

import numpy as np
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

PORT = "/"  
BAUD = 115200
GRID = 8
CLIP_MM = 3000  # sensor max useful range ~4m -> clip to 3m for better color contrast

LABEL_KEYS = {
    "r": "rock",
    "p": "paper",
    "s": "scissors",
    "e": "empty",
}

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # let the ESP32 finish its reset after the serial port opens
ser.reset_input_buffer()

fig, ax = plt.subplots()
im = ax.imshow(np.zeros((GRID, GRID)), vmin=0, vmax=CLIP_MM, cmap="viridis")
plt.colorbar(im, label="Distance (mm)")
title = ax.set_title("Waiting for first frame...")

state = {"recording": False, "label": None, "buffer": [], "dataset": []}

# Load any existing dataset so this run ADDS to it instead of overwriting it
try:
    with open("gesture_dataset.json") as fh:
        state["dataset"] = json.load(fh)
    print(f"Loaded {len(state['dataset'])} existing frames -- new recordings will be added to these.")
except FileNotFoundError:
    print("No existing dataset found -- starting fresh.")

# Listen for keypresses to start/stop recording and save the dataset
def on_key(event):
    if event.key in LABEL_KEYS:
        state["label"] = LABEL_KEYS[event.key]
        state["recording"] = True
        state["buffer"] = []
        print(f"\nRecording '{state['label']}'... press SPACE to stop.")
    elif event.key == " " and state["recording"]:
        state["recording"] = False
        for frame in state["buffer"]:
            state["dataset"].append({"label": state["label"], "frame": frame.tolist()})
        print(f"Saved {len(state['buffer'])} frames for '{state['label']}'. "
              f"Total dataset size: {len(state['dataset'])}")
    elif event.key == "q":
        with open("gesture_dataset.json", "w") as fh:
            json.dump(state["dataset"], fh)
        print(f"\nDataset saved to gesture_dataset.json ({len(state['dataset'])} frames total). Exiting.")
        plt.close(fig)


fig.canvas.mpl_connect("key_press_event", on_key)

# Update the heatmap with the latest frame from the ESP32
def update(_frame_num):
    line = ser.readline().decode(errors="ignore").strip()
    if not line or line == "READY":
        return (im,)
    try:
        values = [int(v) for v in line.split(",")]
    except ValueError:
        return (im,)
    if len(values) != GRID * GRID:
        return (im,)

    arr = np.clip(np.array(values), 0, CLIP_MM).reshape(GRID, GRID)
    im.set_data(arr)

    if state["recording"]:
        state["buffer"].append(arr)
        title.set_text(f"RECORDING: {state['label']} ({len(state['buffer'])} frames) -- SPACE to stop")
    else:
        title.set_text("r/p/s/e = record, SPACE = stop, q = save+quit")

    return (im,)

# Animate the heatmap and start the GUI event loop
ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.show()

ser.close()