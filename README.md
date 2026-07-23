# hands-up

Rock/paper/scissors gesture recognition using an ESP32 + VL53L8CX time-of-flight
sensor (8x8 depth grid) and a small PyTorch classifier.

## Pipeline

1. **`capture_data.py`** -- live heatmap of the sensor feed with keyboard-driven
   labeled data collection. Records frames into `gesture_dataset.json`.
   ```
   pip install numpy matplotlib pyserial
   python3 capture_data.py
   ```
   Controls (click the plot window first so it has keyboard focus):
   - `r` / `p` / `s` / `e` -- start recording "rock" / "paper" / "scissors" / "empty"
   - `SPACE` -- stop recording
   - `q` -- save dataset and quit

2. **`train_classifier.py`** -- trains a small MLP on `gesture_dataset.json` and
   saves the best checkpoint to `gesture_model.pt`.
   ```
   pip install torch numpy
   python3 train_classifier.py
   ```

3. **`live_demo.py`** -- loads `gesture_model.pt` and prints live predictions +
   confidence as frames come in from the sensor.
   ```
   pip install pyserial torch numpy
   python3 live_demo.py
   ```

## Setup

Each script opens a serial connection to the ESP32 at 115200 baud. Edit the
`PORT` constant at the top of `capture_data.py` and `live_demo.py` to match
your device's serial port (e.g. `/dev/tty.usbserial-XXXX` on macOS, `COM3` on
Windows) before running.
