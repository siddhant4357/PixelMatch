"""
Training Script for Custom Face Classifier.
This script implements the complete training pipeline:
1. Load images from training_dataset folders
2. Extract face embeddings using pre-trained models
3. Train a PyTorch MLP classifier
4. Save the trained model and generate training logs
"""

import os
import sys
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import json
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from models.face_detection import FaceDetector
from models.face_recognition import get_facenet_model
from models.custom_classifier import FaceClassifier
from utils.image_processing import load_image, crop_face, preprocess_face
import config


class FaceDataset(Dataset):
    """Custom dataset for face embeddings."""
    
    def __init__(self, embeddings, labels):
        self.embeddings = torch.FloatTensor(embeddings)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]


def load_training_data(dataset_path, face_detector, face_recognizer):
    """
    Load images from dataset folders and extract embeddings.
    
    Args:
        dataset_path: Path to training_dataset folder
        face_detector: Face detection model
        face_recognizer: Face recognition model (for embeddings)
    
    Returns:
        embeddings: List of face embeddings
        labels: List of corresponding labels
        label_map: Dict mapping label indices to person names
    """
    embeddings = []
    labels = []
    label_map = {}
    
    # Get all person folders
    person_folders = sorted([f for f in dataset_path.iterdir() if f.is_dir()])
    
    if not person_folders:
        raise ValueError(f"No person folders found in {dataset_path}")
    
    print(f"\n{'='*60}")
    print(f"LOADING TRAINING DATA")
    print(f"{'='*60}\n")
    
    for label_idx, person_folder in enumerate(person_folders):
        person_name = person_folder.name
        label_map[label_idx] = person_name
        
        # Get all images in this person's folder
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            image_files.extend(person_folder.glob(ext))
        
        if not image_files:
            print(f"⚠️  WARNING: No images found for {person_name}")
            continue
        
        print(f"📁 Processing {person_name}: {len(image_files)} images")
        
        person_embeddings = 0
        for img_path in tqdm(image_files, desc=f"  Extracting embeddings"):
            # Load image
            image = load_image(str(img_path))
            if image is None:
                continue
            
            # Detect faces
            faces = face_detector.detect_faces(image)
            if not faces:
                print(f"  ⚠️  No face detected in {img_path.name}")
                continue
            
            # Use the first (largest) face
            bbox, confidence = faces[0]
            face_img = crop_face(image, bbox)
            if face_img is None:
                continue
            
            # Preprocess and generate embedding
            preprocessed = preprocess_face(face_img, config.FACE_SIZE)
            embedding = face_recognizer.generate_embedding(preprocessed, enable_tta=True)
            
            if embedding is not None:
                embeddings.append(embedding)
                labels.append(label_idx)
                person_embeddings += 1
        
        print(f"  ✓ Extracted {person_embeddings} embeddings for {person_name}\n")
    
    if not embeddings:
        raise ValueError("No embeddings extracted! Please check your dataset.")
    
    print(f"{'='*60}")
    print(f"DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"Total embeddings: {len(embeddings)}")
    print(f"Number of classes: {len(label_map)}")
    print(f"Label mapping: {label_map}")
    print(f"{'='*60}\n")
    
    return np.array(embeddings), np.array(labels), label_map


def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs, device):
    """
    Train the classifier.
    
    Returns:
        train_losses: List of training losses per epoch
        val_losses: List of validation losses per epoch
        train_accs: List of training accuracies per epoch
        val_accs: List of validation accuracies per epoch
    """
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    
    print(f"\n{'='*60}")
    print(f"TRAINING STARTED")
    print(f"{'='*60}\n")
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for embeddings, labels in train_loader:
            embeddings, labels = embeddings.to(device), labels.to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(embeddings)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        
        # Validation phase
        model.eval()
        val_running_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for embeddings, labels in val_loader:
                embeddings, labels = embeddings.to(device), labels.to(device)
                outputs = model(embeddings)
                loss = criterion(outputs, labels)
                
                val_running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_loss = val_running_loss / len(val_loader)
        val_acc = 100 * val_correct / val_total
        val_losses.append(val_loss)
        val_accs.append(val_acc)
        
        # Print progress
        print(f"Epoch [{epoch+1}/{num_epochs}] | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
    
    print(f"\n{'='*60}")
    print(f"TRAINING COMPLETED")
    print(f"{'='*60}\n")
    
    return train_losses, val_losses, train_accs, val_accs


def save_training_plots(train_losses, val_losses, train_accs, val_accs, save_dir):
    """Generate and save training plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Loss plot
    epochs = range(1, len(train_losses) + 1)
    ax1.plot(epochs, train_losses, 'b-', label='Training Loss', linewidth=2)
    ax1.plot(epochs, val_losses, 'r-', label='Validation Loss', linewidth=2)
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy plot
    ax2.plot(epochs, train_accs, 'b-', label='Training Accuracy', linewidth=2)
    ax2.plot(epochs, val_accs, 'r-', label='Validation Accuracy', linewidth=2)
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Accuracy (%)', fontsize=12)
    ax2.set_title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = save_dir / 'training_curves.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved training curves to {plot_path}")
    plt.close()


def main():
    """Main training pipeline."""
    
    # Configuration
    DATASET_PATH = Path("data/training_dataset")
    OUTPUT_DIR = Path("data/trained_models")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    BATCH_SIZE = 16
    NUM_EPOCHS = 50
    LEARNING_RATE = 0.001
    TRAIN_SPLIT = 0.8
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🖥️  Using device: {device}\n")
    
    # Initialize models
    print("Loading pre-trained models...")
    face_detector = FaceDetector()
    face_recognizer = get_facenet_model()
    print("✓ Models loaded\n")
    
    # Load and process dataset
    embeddings, labels, label_map = load_training_data(
        DATASET_PATH, face_detector, face_recognizer
    )
    
    # Create dataset and split
    dataset = FaceDataset(embeddings, labels)
    train_size = int(TRAIN_SPLIT * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    print(f"Train samples: {train_size}")
    print(f"Validation samples: {val_size}\n")
    
    # Initialize classifier
    num_classes = len(label_map)
    model = FaceClassifier(input_dim=1024, num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"Model architecture:\n{model}\n")
    
    # Train
    train_losses, val_losses, train_accs, val_accs = train_model(
        model, train_loader, val_loader, criterion, optimizer, NUM_EPOCHS, device
    )
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = OUTPUT_DIR / f"face_classifier_{timestamp}.pth"
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'label_map': label_map,
        'num_classes': num_classes,
        'input_dim': 1024,
        'train_acc': train_accs[-1],
        'val_acc': val_accs[-1]
    }, model_path)
    
    print(f"✓ Saved model to {model_path}")
    
    # Save training plots
    save_training_plots(train_losses, val_losses, train_accs, val_accs, OUTPUT_DIR)
    
    # Save training log
    log_data = {
        'timestamp': timestamp,
        'num_epochs': NUM_EPOCHS,
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE,
        'train_samples': train_size,
        'val_samples': val_size,
        'num_classes': num_classes,
        'label_map': label_map,
        'final_train_acc': train_accs[-1],
        'final_val_acc': val_accs[-1],
        'final_train_loss': train_losses[-1],
        'final_val_loss': val_losses[-1]
    }
    
    log_path = OUTPUT_DIR / f"training_log_{timestamp}.json"
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"✓ Saved training log to {log_path}")
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Training Accuracy: {train_accs[-1]:.2f}%")
    print(f"Validation Accuracy: {val_accs[-1]:.2f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
