"""
Trains a small MLP to classify gestures from 8x8 VL53L8CX depth frames.

Run this AFTER capture_data.py has produced gesture_dataset.json with a reasonable
amount of data per class.

Install deps: pip install torch numpy
"""

import json

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split

CLIP_MM = 3000.0 # sensor max useful range ~4m -> clip to 3m for better color contrast

with open("gesture_dataset.json") as f:
    data = json.load(f)

if len(data) < 20:
    print(f"WARNING: only {len(data)} frames total. Collect more before trusting this model.")

# Create a dataset and dataloaders for training/validation
labels = sorted(set(d["label"] for d in data))
label_to_idx = {label: i for i, label in enumerate(labels)}
print("Classes:", labels)
print("Total frames:", len(data))
for label in labels:
    count = sum(1 for d in data if d["label"] == label)
    print(f"  {label}: {count} frames")

X = np.array([d["frame"] for d in data], dtype=np.float32).reshape(len(data), -1) / CLIP_MM
y = np.array([label_to_idx[d["label"]] for d in data], dtype=np.int64)

# Define a PyTorch Dataset and model architecture for training
class GestureDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X)
        self.y = torch.tensor(y)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

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

# Split the dataset into training and validation sets, create dataloaders, and train the model
full_ds = GestureDataset(X, y)
n_val = max(1, int(0.2 * len(full_ds)))
n_train = len(full_ds) - n_val
train_ds, val_ds = random_split(full_ds, [n_train, n_val])
train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=16)

model = GestureNet(len(labels))
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

EPOCHS = 150
best_val_acc = 0.0
best_state = None

# Train the model for a number of epochs, keeping track of the best validation accuracy and saving the best model state
for epoch in range(EPOCHS):
    model.train()
    for xb, yb in train_loader:
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        optimizer.step()

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for xb, yb in val_loader:
            preds = model(xb).argmax(dim=1)
            correct += (preds == yb).sum().item()
            total += yb.size(0)
    acc = correct / max(total, 1)

    if acc > best_val_acc:
        best_val_acc = acc
        best_state = {k: v.clone() for k, v in model.state_dict().items()}

    if epoch % 10 == 0 or epoch == EPOCHS - 1:
        print(f"Epoch {epoch:3d}: val acc = {acc:.1%}" + (" (new best)" if acc == best_val_acc else ""))

# Save the best model state and labels to a checkpoint file for later use in live_demo.py
torch.save({"model_state": best_state, "labels": labels}, "gesture_model.pt")
print(f"\nSaved BEST model (val acc = {best_val_acc:.1%}) to gesture_model.pt")
print("Next: run live_demo.py for the live recognition demo.")