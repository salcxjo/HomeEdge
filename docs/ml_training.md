# HomeEdge ML Training Guide

Guide for training and deploying the PyTorch autoencoder for anomaly detection.

## Table of Contents
1. [Data Collection](#data-collection)
2. [Training the Autoencoder](#training-the-autoencoder)
3. [Model Evaluation](#model-evaluation)
4. [Deployment](#deployment)
5. [Hyperparameter Tuning](#hyperparameter-tuning)

---

## Data Collection

### Minimum Requirements
- **Duration:** 2-4 weeks of continuous operation
- **Conditions:** Normal household patterns (not during vacation, construction, etc.)
- **Quality:** Minimize sensor dropouts and errors

### Export Training Data

```bash
cd ~/HomeEdge/models
python3 export_training_data.py
```

This script:
1. Connects to SQLite database
2. Extracts sensor readings from specified time range
3. Pivots data to wide format (one row per timestamp)
4. Cleans missing values and outliers
5. Saves to `sensor_training_data.csv`

**Output Format:**
```csv
timestamp,temperature,humidity,pressure,light_level
1710000000,22.4,58.2,1013.25,45
1710000600,22.3,58.5,1013.20,44
...
```

### Data Quality Checks

```python
import pandas as pd

df = pd.read_csv('sensor_training_data.csv')

# Check for missing values
print(df.isnull().sum())

# Check for outliers
print(df.describe())

# Visualize distributions
import matplotlib.pyplot as plt
df.hist(bins=50, figsize=(12,8))
plt.tight_layout()
plt.savefig('data_distributions.png')
```

**Remove outliers if needed:**
```python
# Example: Remove temperature readings below 0°C or above 40°C
df = df[(df['temperature'] > 0) & (df['temperature'] < 40)]
```

---

## Training the Autoencoder

### Architecture Overview

```
Input Layer (4 features)
    ↓
Dense(4 → 8) + ReLU
    ↓
Dense(8 → 2)  [Bottleneck]
    ↓
Dense(2 → 8) + ReLU
    ↓
Dense(8 → 4)  [Reconstruction]
```

**Why this works:**
- Bottleneck forces compression of normal patterns
- Model learns to reconstruct normal data with low error
- Anomalies can't be compressed well → high reconstruction error

### Training Script

```bash
python3 train_autoencoder.py
```

**Key sections explained:**

#### 1. Data Preprocessing
```python
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv('sensor_training_data.csv')
X = df[['temperature', 'humidity', 'pressure', 'light_level']].values

# Normalize (critical for neural networks)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save scaler for deployment
import joblib
joblib.dump(scaler, 'scaler.pkl')
```

**Why normalize?**
- Features have different scales (temp: 15-30, pressure: 900-1100)
- Neural networks work best with zero-mean, unit-variance data
- Must use same scaler at inference time

#### 2. Train/Validation Split
```python
from sklearn.model_selection import train_test_split

X_train, X_val = train_test_split(X_scaled, test_size=0.2, shuffle=True)
```

**Note:** We shuffle here because we're learning overall patterns, not temporal sequences. For time-series forecasting, would use temporal split.

#### 3. Model Definition
```python
import torch.nn as nn

class Autoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 2)  # Bottleneck
        )
        self.decoder = nn.Sequential(
            nn.Linear(2, 8),
            nn.ReLU(),
            nn.Linear(8, 4)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
```

#### 4. Training Loop
```python
model = Autoencoder()
criterion = nn.MSELoss()  # Mean Squared Error
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 100
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    
    outputs = model(X_train_tensor)
    loss = criterion(outputs, X_train_tensor)
    
    loss.backward()
    optimizer.step()
    
    # Validation
    if (epoch + 1) % 10 == 0:
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_loss = criterion(val_outputs, X_val_tensor)
        
        print(f'Epoch {epoch+1}/{epochs}')
        print(f'  Train Loss: {loss.item():.6f}')
        print(f'  Val Loss: {val_loss.item():.6f}')
```

**Watch for:**
- Training loss should decrease steadily
- Validation loss should track training loss
- If val loss >> train loss → overfitting (reduce epochs or add regularization)

---

## Model Evaluation

### Reconstruction Error Distribution

After training, analyze reconstruction error on validation set:

```python
model.eval()
with torch.no_grad():
    reconstructed = model(X_val_tensor)
    errors = torch.mean((X_val_tensor - reconstructed)**2, dim=1)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.hist(errors.numpy(), bins=50, alpha=0.7, edgecolor='black')
plt.xlabel('Reconstruction Error (MSE)')
plt.ylabel('Frequency')
plt.title('Error Distribution on Validation Set')
plt.axvline(errors.quantile(0.95).item(), color='r', linestyle='--', 
            label='95th Percentile Threshold')
plt.legend()
plt.savefig('error_distribution.png')
plt.show()
```

### Setting the Anomaly Threshold

**Method 1: Percentile-based (Recommended)**
```python
threshold = errors.quantile(0.95).item()
print(f'95th percentile threshold: {threshold:.6f}')
```

**Interpretation:** 95% of normal data will reconstruct below this error. 5% false positive rate expected.

**Method 2: Standard Deviations**
```python
mean_error = errors.mean().item()
std_error = errors.std().item()
threshold = mean_error + 2 * std_error  # 2-sigma threshold
```

**Method 3: Manual Tuning**
Inject known anomalies (e.g., simulate heater turning on) and adjust threshold to catch them while minimizing false positives.

### Feature Importance

Which features contribute most to reconstruction error?

```python
# Per-feature reconstruction error
with torch.no_grad():
    reconstructed = model(X_val_tensor)
    feature_errors = torch.abs(X_val_tensor - reconstructed)

feature_names = ['temperature', 'humidity', 'pressure', 'light_level']
avg_errors = feature_errors.mean(dim=0).numpy()

plt.bar(feature_names, avg_errors)
plt.ylabel('Average Reconstruction Error')
plt.title('Feature-wise Reconstruction Error')
plt.savefig('feature_importance.png')
plt.show()
```

---

## Deployment

### Save the Model

```python
# Save model weights
torch.save(model.state_dict(), 'autoencoder.pth')

# Save threshold
with open('threshold.txt', 'w') as f:
    f.write(str(threshold))

# Scaler already saved during preprocessing
```

### Load Model for Inference

```python
import torch
import joblib

# Load architecture (must match training)
model = Autoencoder()
model.load_state_dict(torch.load('autoencoder.pth'))
model.eval()

# Load scaler
scaler = joblib.load('scaler.pkl')

# Load threshold
with open('threshold.txt', 'r') as f:
    threshold = float(f.read().strip())
```

### Real-Time Inference

```python
def detect_anomaly(sensor_data):
    """
    sensor_data: dict with keys 'temperature', 'humidity', 'pressure', 'light_level'
    returns: (is_anomaly, error_value)
    """
    # Prepare input
    x = np.array([[
        sensor_data['temperature'],
        sensor_data['humidity'],
        sensor_data['pressure'],
        sensor_data['light_level']
    ]])
    
    # Normalize
    x_scaled = scaler.transform(x)
    x_tensor = torch.FloatTensor(x_scaled)
    
    # Inference
    with torch.no_grad():
        reconstructed = model(x_tensor)
        error = torch.mean((x_tensor - reconstructed)**2).item()
    
    is_anomaly = error > threshold
    
    return is_anomaly, error
```

### Integration with MQTT

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    
    # Collect latest readings
    if 'temperature' in data:
        sensor_buffer['temperature'] = data['temperature']
    # ... similar for other sensors
    
    # Check if we have all readings
    if all(k in sensor_buffer for k in ['temperature', 'humidity', 'pressure', 'light_level']):
        is_anomaly, error = detect_anomaly(sensor_buffer)
        
        if is_anomaly:
            print(f'🚨 ANOMALY DETECTED! Error: {error:.6f}')
            # Publish alert
            client.publish('home/pi/anomaly', json.dumps({
                'error': error,
                'threshold': threshold,
                'readings': sensor_buffer
            }))
```

---

## Hyperparameter Tuning

### Key Hyperparameters

| Parameter | Default | Typical Range | Effect |
|-----------|---------|---------------|--------|
| Bottleneck size | 2 | 2-4 | Smaller = more compression, harder to reconstruct anomalies |
| Learning rate | 0.001 | 0.0001-0.01 | Higher = faster but less stable training |
| Epochs | 100 | 50-200 | More epochs = better fit, risk overfitting |
| Hidden layer size | 8 | 4-16 | Larger = more capacity, slower training |
| Threshold percentile | 95 | 90-99 | Higher = fewer false positives, may miss anomalies |

### Tuning Workflow

1. **Start with defaults**
2. **Train for 100 epochs**
3. **Check validation loss curve:**
   - Still decreasing? → Increase epochs
   - Plateaued early? → Decrease learning rate or increase model capacity
   - Diverging? → Decrease learning rate
4. **Evaluate on known anomalies:**
   - Missed real anomalies? → Decrease threshold percentile or increase bottleneck size
   - Too many false positives? → Increase threshold percentile or collect more diverse training data

### Advanced: Grid Search

```python
from sklearn.model_selection import ParameterGrid

param_grid = {
    'bottleneck_size': [2, 3, 4],
    'hidden_size': [8, 12, 16],
    'lr': [0.0001, 0.001, 0.01]
}

results = []
for params in ParameterGrid(param_grid):
    model = Autoencoder(
        bottleneck_size=params['bottleneck_size'],
        hidden_size=params['hidden_size']
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=params['lr'])
    
    # Train model...
    val_loss = train_model(model, optimizer)
    
    results.append({
        'params': params,
        'val_loss': val_loss
    })

# Find best configuration
best = min(results, key=lambda x: x['val_loss'])
print(f'Best params: {best["params"]}')
```

---

## Troubleshooting

### Training Loss Not Decreasing
- **Learning rate too high** → Reduce by 10x
- **Bad initialization** → Try different random seed or use Xavier initialization
- **Data not normalized** → Check scaler was applied

### Validation Loss Much Higher Than Training Loss
- **Overfitting** → Reduce epochs, add dropout, or collect more data
- **Data leakage** → Ensure no overlap between train/val sets

### All Predictions Are "Normal" (No Anomalies Ever Detected)
- **Threshold too high** → Lower percentile (try 90th or 85th)
- **Model too expressive** → Reduce bottleneck size to force compression
- **Not enough training data diversity** → Collect data over longer period

### Too Many False Positives
- **Threshold too low** → Increase percentile (try 97th or 99th)
- **Training data not representative** → Include more edge cases in training set
- **Seasonal/daily patterns** → Add time-of-day as feature or train separate models for day/night

---

## Future Improvements

### Phase 8 Extensions

**1. Time-Series Forecasting**
- Use LSTM autoencoder instead of dense layers
- Predict next hour's sensor values
- Flag when actual differs significantly from prediction

**2. Multi-Modal Anomaly Detection**
- Combine reconstruction error with statistical tests
- Isolation Forest for outlier detection
- Ensemble of multiple models

**3. Explainable Anomalies**
- SHAP values for feature contribution
- "Temperature anomaly detected: 8°C above expected"
- Auto-generate natural language explanations

**4. Adaptive Thresholds**
- Update threshold based on recent data
- Separate thresholds for day/night/weekend
- Learn seasonal patterns

---

For more help, see other documentation files or open an issue on GitHub.
