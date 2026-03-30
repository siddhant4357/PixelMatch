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
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "dataset"
MODEL_DIR = BASE_DIR / "data" / "trained_models"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def load_latest_model(model_dir):
    """Find and load the most recent model and its test split."""
    model_files = list(model_dir.glob("face_classifier_*.pth"))
    if not model_files:
        raise FileNotFoundError("No model files found!")
    
    # Sort by modification time (newest first)
    latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading model: {latest_model.name}")
    
    checkpoint = torch.load(latest_model, map_location=DEVICE)
    
    # Load corresponding log file to get test paths
    timestamp = latest_model.stem.replace('face_classifier_', '')
    log_file = model_dir / f"training_log_{timestamp}.json"
    
    test_paths = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            log_data = json.load(f)
            test_paths = log_data.get('test_image_paths', [])
            print(f"✓ Loaded {len(test_paths)} specific test image paths for this model")
    else:
        print(f"Warning: Log file not found {log_file.name}. Cannot find test split.")
        
    return checkpoint, test_paths


def evaluate():
    print(f"\n{'='*60}")
    print(f"MODEL EVALUATION")
    print(f"{'='*60}\n")

    # 1. Load Model
    try:
        checkpoint, test_image_paths = load_latest_model(MODEL_DIR)
        if not test_image_paths:
            print("❌ No test images found. Please run your new train_model.py first!")
            return
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
    print("\nProcessing the dynamic test split for evaluation...")
    embeddings = []
    y_true = []
    
    for img_path_str in test_image_paths:
        img_path = Path(img_path_str)
        person_name = img_path.parent.name
        
        # Look up true label index using the model's mapped dictionary
        label_idx = None
        for k, v in label_map.items():
            if v == person_name:
                label_idx = k
                break
                
        if label_idx is None:
            continue
            
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
