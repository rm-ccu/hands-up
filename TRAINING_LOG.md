# Training Log

Terminal output from early data-collection/training iterations, kept as a
record of how the dataset came together (including a failed run caused by
class imbalance).

## Failed Run

**Capturing data:**
```
$ python3 capture_data.py
Recording 'empty'... press SPACE to stop.
Saved 11 frames for 'empty'. Total dataset size: 11

Recording 'rock'... press SPACE to stop.
Saved 33 frames for 'rock'. Total dataset size: 44

Recording 'paper'... press SPACE to stop.
Saved 38 frames for 'paper'. Total dataset size: 82

Recording 'rock'... press SPACE to stop.
Saved 27 frames for 'rock'. Total dataset size: 109

Recording 'paper'... press SPACE to stop.
Saved 38 frames for 'paper'. Total dataset size: 147

Recording 'empty'... press SPACE to stop.
Saved 11 frames for 'empty'. Total dataset size: 158

Recording 'scissors'... press SPACE to stop.
Saved 41 frames for 'scissors'. Total dataset size: 199

Recording 'scissors'... press SPACE to stop.
Saved 37 frames for 'scissors'. Total dataset size: 236

Dataset saved to gesture_dataset.json (236 frames total). Exiting.
```

**Training ("empty" underrepresented):**
```
$ python3 train_classifier.py
Classes: ['empty', 'paper', 'rock', 'scissors']
Total frames: 236
  empty: 22 frames
  paper: 76 frames
  rock: 60 frames
  scissors: 78 frames
Epoch   0: val acc = 23.4%
Epoch  10: val acc = 40.4%
Epoch  20: val acc = 48.9%
Epoch  30: val acc = 55.3%
Epoch  40: val acc = 55.3%
Epoch  50: val acc = 61.7%
Epoch  59: val acc = 66.0%

Saved model to gesture_model.pt
Next: run live_demo.py for the live recognition demo.
```

**Capturing more "empty":**
```
$ python3 capture_data.py
Recording 'empty'... press SPACE to stop.
Saved 31 frames for 'empty'. Total dataset size: 31

Dataset saved to gesture_dataset.json (31 frames total). Exiting.
```

**New training failure (dataset had been overwritten, not appended -- only "empty" left):**
```
$ python3 train_classifier.py
Classes: ['empty']
Total frames: 31
  empty: 31 frames
Epoch   0: val acc = 100.0%
Epoch  10: val acc = 100.0%
Epoch  20: val acc = 100.0%
Epoch  30: val acc = 100.0%
Epoch  40: val acc = 100.0%
Epoch  50: val acc = 100.0%
Epoch  59: val acc = 100.0%

Saved model to gesture_model.pt
Next: run live_demo.py for the live recognition demo.
```

## Proper Run

**Capturing empty data (to test):**
```
$ python3 capture_data.py
Recording 'empty'... press SPACE to stop.
Saved 31 frames for 'empty'. Total dataset size: 31

Dataset saved to gesture_dataset.json (31 frames total). Exiting.
```

**Capturing all data:**
```
$ python3 capture_data.py
Loaded 31 existing frames -- new recordings will be added to these.

Recording 'empty'... press SPACE to stop.
Saved 50 frames for 'empty'. Total dataset size: 81

Recording 'rock'... press SPACE to stop.
Saved 31 frames for 'rock'. Total dataset size: 112

Recording 'rock'... press SPACE to stop.
Saved 37 frames for 'rock'. Total dataset size: 149

Recording 'paper'... press SPACE to stop.
Saved 43 frames for 'paper'. Total dataset size: 192

Recording 'paper'... press SPACE to stop.
Saved 44 frames for 'paper'. Total dataset size: 236

Recording 'scissors'... press SPACE to stop.
Saved 51 frames for 'scissors'. Total dataset size: 287

Recording 'scissors'... press SPACE to stop.
Saved 45 frames for 'scissors'. Total dataset size: 332

Recording 'empty'... press SPACE to stop.
Saved 33 frames for 'empty'. Total dataset size: 365

Dataset saved to gesture_dataset.json (365 frames total). Exiting.
```

**Training:**
```
$ python3 train_classifier.py
Classes: ['empty', 'paper', 'rock', 'scissors']
Total frames: 365
  empty: 114 frames
  paper: 87 frames
  rock: 68 frames
  scissors: 96 frames
Epoch   0: val acc = 31.5%
Epoch  10: val acc = 46.6%
Epoch  20: val acc = 61.6%
Epoch  30: val acc = 71.2%
Epoch  40: val acc = 69.9%
Epoch  50: val acc = 69.9%
Epoch  60: val acc = 68.5%
Epoch  70: val acc = 67.1%
Epoch  80: val acc = 68.5%
Epoch  90: val acc = 68.5%
Epoch 100: val acc = 69.9%
Epoch 110: val acc = 72.6%
Epoch 120: val acc = 72.6%
Epoch 130: val acc = 74.0%
Epoch 140: val acc = 76.7%
Epoch 149: val acc = 72.6%

Saved model to gesture_model.pt
Next: run live_demo.py for the live recognition demo.
```

**Training, selecting the best epoch's checkpoint instead of the last:**
```
$ python3 train_classifier.py
Classes: ['empty', 'paper', 'rock', 'scissors']
Total frames: 365
  empty: 114 frames
  paper: 87 frames
  rock: 68 frames
  scissors: 96 frames
Epoch   0: val acc = 30.1% (new best)
Epoch  10: val acc = 58.9% (new best)
Epoch  20: val acc = 63.0%
Epoch  30: val acc = 67.1% (new best)
Epoch  40: val acc = 64.4%
Epoch  50: val acc = 65.8%
Epoch  60: val acc = 68.5%
Epoch  70: val acc = 67.1%
Epoch  80: val acc = 69.9% (new best)
Epoch  90: val acc = 71.2%
Epoch 100: val acc = 74.0%
Epoch 110: val acc = 72.6%
Epoch 120: val acc = 78.1% (new best)
Epoch 130: val acc = 76.7%
Epoch 140: val acc = 78.1%
Epoch 149: val acc = 76.7%

Saved BEST model (val acc = 80.8%) to gesture_model.pt
Next: run live_demo.py for the live recognition demo.
```
