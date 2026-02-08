"""
Evaluation Script for Face Classifier.
Generates:
1. Confusion Matrix Plot
2. Classification Report (Precision, Recall, F1-Score)
3. Test Set Accuracy
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from models.custom_classifier import FaceClassifier
from models.face_detection import FaceDetector
from models.face_recognition import get_facenet_model
from utils.image_processing import load_image, crop_face, preprocess_face
import config

# Configuration
DATASET_PATH = Path("data/training_dataset")
MODEL_DIR = Path("data/trained_models")
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def load_latest_model(model_dir):
    """Find and load the most recent model file."""
    model_files = list(model_dir.glob("face_classifier_*.pth"))
    if not model_files:
        raise FileNotFoundError("No model files found!")
    
    # Sort by modification time (newest first)
    latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading model: {latest_model.name}")
    
    checkpoint = torch.load(latest_model, map_location=DEVICE)
    return checkpoint


def evaluate():
    print(f"\n{'='*60}")
    print(f"MODEL EVALUATION")
    print(f"{'='*60}\n")

    # 1. Load Model
    try:
        checkpoint = load_latest_model(MODEL_DIR)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Initialize Model architecture
    num_classes = checkpoint['num_classes']
    input_dim = checkpoint['input_dim']
    label_map = checkpoint['label_map']
    # Convert string keys to int if necessary (JSON saves keys as strings)
    label_map = {int(k): v for k, v in label_map.items()}
    
    model = FaceClassifier(input_dim=input_dim, num_classes=num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(DEVICE)
    model.eval()

    # 2. Load Models for Preprocessing
    print("Loading AI models for feature extraction...")
    face_detector = FaceDetector()
    face_recognizer = get_facenet_model()

    # 3. Process Dataset (Same logic as training to ensure consistency)
    # real-world: you might want a separate 'test_dataset' folder
    print("\nProcessing dataset for evaluation...")
    embeddings = []
    y_true = []
    
    person_folders = sorted([f for f in DATASET_PATH.iterdir() if f.is_dir()])
    
    for label_idx, person_folder in enumerate(person_folders):
        person_name = person_folder.name
        # Verify this folder matches the label_map from training
        # Note: This assumes folders haven't changed since training!
        if label_idx not in label_map or label_map[label_idx] != person_name:
             print(f"Warning: Folder {person_name} might not match training label {label_idx}")
        
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            image_files.extend(person_folder.glob(ext))
            
        print(f"  Evaluating {person_name}...")
        
        for img_path in image_files:
            try:
                # Extract embedding
                image = load_image(str(img_path))
                if image is None: continue
                
                faces = face_detector.detect_faces(image)
                if not faces: continue
                
                bbox, _ = faces[0]
                face_img = crop_face(image, bbox)
                if face_img is None: continue
                
                preprocessed = preprocess_face(face_img, config.FACE_SIZE)
                emb = face_recognizer.generate_embedding(preprocessed, enable_tta=True)
                
                if emb is not None:
                    embeddings.append(emb)
                    y_true.append(label_idx)
            except Exception as e:
                print(f"Error processing {img_path.name}: {e}")

    # 4. Predict
    X = torch.FloatTensor(np.array(embeddings)).to(DEVICE)
    with torch.no_grad():
        outputs = model(X)
        _, y_pred = torch.max(outputs, 1)
    
    y_pred = y_pred.cpu().numpy()
    y_true = np.array(y_true)

    # 5. Generate Metrics
    # Filter class_names to only include those present in y_true
    unique_labels = sorted(list(set(y_true)))
    target_names = [label_map[i] for i in unique_labels]
    
    print(f"\n{'='*60}")
    print(f"CLASSIFICATION REPORT")
    print(f"{'='*60}")
    
    # Use labels parameter to specify which classes to include
    print(classification_report(y_true, y_pred, labels=unique_labels, target_names=target_names))
    
    # 6. Confusion Matrix Plot
    cm = confusion_matrix(y_true, y_pred, labels=unique_labels)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=target_names, yticklabels=target_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    
    save_path = MODEL_DIR / 'confusion_matrix.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved Confusion Matrix to {save_path}")
    
    # Save text report
    report = classification_report(y_true, y_pred, labels=unique_labels, target_names=target_names, output_dict=True)
    with open(MODEL_DIR / 'evaluation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Saved Evaluation Report to {MODEL_DIR / 'evaluation_report.json'}")

if __name__ == "__main__":
    evaluate()
