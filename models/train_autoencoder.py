"""
HomeEdge - Autoencoder Training Script
Train anomaly detection model on collected sensor data
"""

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import matplotlib.pyplot as plt
import sqlite3
import time

# Configuration
DB_PATH = '../homedata.db'
EPOCHS = 100
BATCH_SIZE = 32
LEARNING_RATE = 0.001
BOTTLENECK_SIZE = 2
VALIDATION_SPLIT = 0.2

class Autoencoder(nn.Module):
    """Simple autoencoder for anomaly detection"""
    def __init__(self, input_dim=4, bottleneck_dim=2):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.ReLU(),
            nn.Linear(8, bottleneck_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, 8),
            nn.ReLU(),
            nn.Linear(8, input_dim)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def load_data_from_db(db_path, days=30):
    """Load sensor data from SQLite database"""
    print(f"Loading data from {db_path}...")
    
    conn = sqlite3.connect(db_path)
    
    # Get data from last N days
    cutoff_time = time.time() - (days * 86400)
    
    query = """
        SELECT timestamp, topic, value
        FROM sensor_data
        WHERE timestamp > ?
        ORDER BY timestamp
    """
    
    df = pd.read_sql_query(query, conn, params=(cutoff_time,))
    conn.close()
    
    print(f"Loaded {len(df)} records")
    
    # Pivot to wide format
    df_pivot = df.pivot(index='timestamp', columns='topic', values='value')
    
    # Keep only the features we want
    features = ['home/pico/temperature', 'home/pico/humidity', 
                'home/pico/pressure', 'home/pico/light_level']
    
    df_clean = df_pivot[features].copy()
    df_clean.columns = ['temperature', 'humidity', 'pressure', 'light_level']
    
    # Remove rows with missing values
    df_clean = df_clean.dropna()
    
    print(f"After cleaning: {len(df_clean)} samples")
    print("\nData statistics:")
    print(df_clean.describe())
    
    return df_clean

def train_model():
    """Main training function"""
    
    # Load data
    df = load_data_from_db(DB_PATH, days=30)
    
    if len(df) < 1000:
        print("\nWARNING: Less than 1000 samples. Recommend collecting more data.")
        print("Need at least 2-4 weeks of continuous operation for good results.")
    
    # Prepare data
    X = df.values
    
    # Normalize features
    print("\nNormalizing features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save scaler
    joblib.dump(scaler, 'scaler.pkl')
    print("Saved scaler to scaler.pkl")
    
    # Train/validation split
    X_train, X_val = train_test_split(X_scaled, test_size=VALIDATION_SPLIT, 
                                       shuffle=True, random_state=42)
    
    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train)
    X_val_tensor = torch.FloatTensor(X_val)
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    # Create model
    model = Autoencoder(input_dim=4, bottleneck_dim=BOTTLENECK_SIZE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # Training loop
    print(f"\nTraining for {EPOCHS} epochs...")
    train_losses = []
    val_losses = []
    
    for epoch in range(EPOCHS):
        # Training
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, X_train_tensor)
        loss.backward()
        optimizer.step()
        
        train_losses.append(loss.item())
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_loss = criterion(val_outputs, X_val_tensor)
            val_losses.append(val_loss.item())
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1}/{EPOCHS} - Train Loss: {loss.item():.6f}, Val Loss: {val_loss.item():.6f}')
    
    # Plot training history
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.title('Training History')
    plt.legend()
    plt.savefig('training_history.png')
    print("\nSaved training history plot to training_history.png")
    
    # Calculate threshold
    print("\nCalculating anomaly threshold...")
    model.eval()
    with torch.no_grad():
        reconstructed = model(X_val_tensor)
        errors = torch.mean((X_val_tensor - reconstructed)**2, dim=1)
    
    # Plot error distribution
    plt.figure(figsize=(10, 5))
    plt.hist(errors.numpy(), bins=50, alpha=0.7, edgecolor='black')
    plt.xlabel('Reconstruction Error')
    plt.ylabel('Frequency')
    plt.title('Validation Set Error Distribution')
    
    # Set threshold at 95th percentile
    threshold = torch.quantile(errors, 0.95).item()
    plt.axvline(threshold, color='r', linestyle='--', linewidth=2,
                label=f'95th Percentile: {threshold:.6f}')
    plt.legend()
    plt.savefig('error_distribution.png')
    print(f"Saved error distribution plot to error_distribution.png")
    
    print(f"\nAnomaly threshold (95th percentile): {threshold:.6f}")
    
    # Save threshold
    with open('threshold.txt', 'w') as f:
        f.write(str(threshold))
    print("Saved threshold to threshold.txt")
    
    # Save model
    torch.save(model.state_dict(), 'autoencoder.pth')
    print("Saved model to autoencoder.pth")
    
    # Final statistics
    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)
    print(f"Final training loss: {train_losses[-1]:.6f}")
    print(f"Final validation loss: {val_losses[-1]:.6f}")
    print(f"Anomaly threshold: {threshold:.6f}")
    print("\nFiles created:")
    print("  - autoencoder.pth (model weights)")
    print("  - scaler.pkl (feature scaler)")
    print("  - threshold.txt (anomaly threshold)")
    print("  - training_history.png (loss plot)")
    print("  - error_distribution.png (threshold plot)")
    print("\nNext steps:")
    print("  1. Copy these files to ~/HomeEdge/models/")
    print("  2. Run anomaly_detector.py to start real-time detection")

if __name__ == '__main__':
    train_model()
