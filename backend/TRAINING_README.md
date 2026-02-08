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


## Running Evaluation

To generate the **Confusion Matrix** and detailed metrics:

```bash
python evaluate_model.py
```

This will create:
- `data/trained_models/confusion_matrix.png` (Visual heatmap of predictions)
- `data/trained_models/evaluation_report.json` (Precision/Recall numbers)

## For Your Project Report

The generated files satisfy these PBL requirements:
- ✅ **Model Code**: `custom_classifier.py` (PyTorch MLP)
- ✅ **Training Logs**: JSON file with all metrics
- ✅ **Training Curves**: PNG plots showing loss/accuracy
- ✅ **Evaluation Results**: Confusion Matrix & Classification Report
- ✅ **Own Dataset**: Your photos organized by person

