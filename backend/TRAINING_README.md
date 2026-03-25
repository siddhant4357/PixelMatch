# Fine-Tuning Instructions

## Dataset Setup

I have created 5 folders for you in `backend/data/training_dataset/`:
- `person_1/`
- `person_2/`
- `person_3/`
- `person_4/`
- `person_5/`

**What to do:**
1. Rename these folders to actual names (e.g., `Rahul`, `Priya`, etc.)
2. Add **15-20 single-person photos** (selfies/portraits) to each folder
3. Supported formats: `.jpg`, `.jpeg`, `.png`

## Running the Training

Once you've added your photos:

```bash
cd backend
python train_model.py
```

**What it does:**
1. Automatically detects faces in all photos
2. Generates embeddings using your pre-trained models
3. Trains a PyTorch neural network classifier
4. Saves:
   - `data/trained_models/face_classifier_TIMESTAMP.pth` (trained model)
   - `data/trained_models/training_curves.png` (loss/accuracy plots)
   - `data/trained_models/training_log_TIMESTAMP.json` (metrics)

## Expected Output

You will see:
- **Training progress** with loss and accuracy per epoch
- **Final accuracy** (should be >95% with 100 photos)
- **Training curves** saved as PNG (use this in your report!)


## 🧠 Model Configuration & Hyperparameters

During training (via both the script and the notebook), the following architecture and parameters are utilized:

- **Feature Extractor (Backbone):** Pre-trained FaceNet (Inception-ResNet v1) generating 1024-dimensional embeddings.
- **Classification Head (Head):** Custom Multi-Layer Perceptron (MLP).
- **Batch Size:** 16
- **Epochs:** 50
- **Learning Rate:** 0.001
- **Optimizer:** Adam
- **Loss Function:** Cross-Entropy Loss
- **Train/Validation Split:** 80% / 20%

## 📊 Running Evaluation (Phase 5 Deliverables)

To rigorously evaluate the model and fulfill your Phase 5 deliverables, we provide a unified Jupyter Notebook that handles training, visualization, and metric calculation all in one place.

### Using the Evaluation Notebook

1. Open `model_evaluation.ipynb` in your preferred Jupyter environment (VS Code, JupyterLab, etc.).
2. Run the cells sequentially.

**The Notebook will automatically run the logic to generate:**
- **Training Curves:** Plots of Training & Validation Loss and Accuracy across all 50 epochs, used to check for overfitting.
- **Classification Report:** Detailed metrics including:
  - **Accuracy:** Overall correctness across all predictions.
  - **Precision:** The accuracy of positive predictions per individual.
  - **Recall:** The ability of the model to correctly identify all photos of a specific individual.
  - **F1-Score:** The harmonic mean of Precision and Recall, proving the model's reliability even with a small dataset.
- **Confusion Matrix:** A color-coded visualization (heatmap) showing true labels vs predicted labels, explicitly highlighting where the model succeeded and where it confused one person for another.

### CLI Alternative

If you do not wish to use the Jupyter Notebook, you can still generate the raw metrics via command line:

```bash
python evaluate_model.py
```

This will create:
- `data/trained_models/confusion_matrix.png` (Visual heatmap of predictions)
- `data/trained_models/evaluation_report.json` (Precision/Recall numbers)

## 🎓 For Your Project Report

The generated files and the `model_evaluation.ipynb` notebook satisfy these PBL requirements:
- ✅ **Model Code & Architecture selection**: `custom_classifier.py` and Notebook execution
- ✅ **Training Strategy Highlights**: Batch Size=16, Epochs=50, LR=0.001
- ✅ **Model Evaluation metrics**: Accuracy, F1-Score, Precision, Recall
- ✅ **Visualizations**: Confusion Matrix & Training Loss/Accuracy Curves 
- ✅ **Own Dataset**: Your photos organized by person
