# Dataset and Model Information

## 1. About the Data
Our dataset consists of embeddings generated for face classification across 5 distinct individuals.

- **Total Embeddings:** 473
- **Number of Classes:** 5
- **Classes / Label Mapping:** 
  - `0`: moksha
  - `1`: shubh
  - `2`: shweta
  - `3`: siddhant
  - `4`: tanish

### Data Split
The data was split into training, validation, and a reserved test set:
- **Train Samples:** 331
- **Validation Samples:** 71
- **Test Samples (reserved for evaluation):** 71

---

## 2. Training Details

### Model Architecture
The model uses a simple yet effective fully connected feed-forward network with Batch Normalization and Dropout layers to prevent overfitting.

```python
FaceClassifier(
  (network): Sequential(
    (0): Linear(in_features=1024, out_features=256, bias=True)
    (1): BatchNorm1d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (2): ReLU()
    (3): Dropout(p=0.3, inplace=False)
    (4): Linear(in_features=256, out_features=128, bias=True)
    (5): BatchNorm1d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (6): ReLU()
    (7): Dropout(p=0.3, inplace=False)
    (8): Linear(in_features=128, out_features=5, bias=True)
  )
)
```

### Training Highlights
The model was trained for 50 epochs.
- **Starting (Epoch 1):** Train Acc: 72.51% | Val Acc: 85.92%
- **Final (Epoch 50):** Train Acc: 97.58% | Val Acc: 91.55%
- **Best Validation Accuracy:** Reached ~92.96% during epochs 24, 37, 40, and 41.

### Training Curves
Below are the training curves showing loss and accuracy over the 50 epochs:

![Training Curves](backend/data/trained_models/training_curves.png)

---

## 3. Evaluation and Results
Evaluation was performed on the reserved 71 test samples using a Super-Ensemble of **ArcFace** and **Facenet512** for feature extraction (Feature Weighting: `[0.7, 0.3]`).

### Overall Results
- **Training Accuracy:** 97.58%
- **Validation Accuracy:** 91.55%
- **Test Accuracy:** 86.00%

### Classification Report

| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **moksha** | 0.74 | 0.88 | 0.80 | 16 |
| **shubh** | 1.00 | 0.93 | 0.97 | 15 |
| **shweta** | 0.81 | 0.81 | 0.81 | 16 |
| **siddhant** | 0.91 | 0.71 | 0.80 | 14 |
| **tanish** | 0.91 | 1.00 | 0.95 | 10 |
| **Accuracy** | - | - | **0.86** | **71** |
| **Macro Avg** | 0.87 | 0.87 | 0.87 | 71 |
| **Weighted Avg** | 0.87 | 0.86 | 0.86 | 71 |

### Confusion Matrix
The confusion matrix visualizes how the model is classifying the test samples and where it might be misclassifying.

![Confusion Matrix](backend/data/trained_models/confusion_matrix.png)

### Saved Artifacts
- **Model:** `face_classifier_20260401_143839.pth`
- **Training Log:** `training_log_20260401_143839.json`
- **Evaluation Report:** `evaluation_report.json`
