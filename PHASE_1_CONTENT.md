# Phase 1: Problem Identification & Proposal

## 1. Problem Statement
The efficient identification and retrieval of personal photographs from large collections remain a significant challenge in event management and smart campus environments. Traditional manual sorting of images is time-consuming, while existing automated solutions often require massive datasets for training or lack privacy-preserving features.

The problem addressed in this project is the development of an **End-to-End Face Recognition System** capable of accurately identifying individuals from a **custom, small-scale dataset**. The system must effectively handle real-world variations such as differing lighting conditions, facial angles, and expressions, while maintaining high classification accuracy with limited training samples (Few-Shot Learning).

## 2. Motivation and Relevance
### **Motivation**
-   **Automation Need:** In university events or large social gatherings, thousands of photos are clicked. Finding one's own photos is a "needle in a haystack" problem.
-   **Data Constraint Challenge:** Building deep learning models usually requires thousands of labeled images. There is a strong motivation to explore **Transfer Learning** techniques to build robust models using only 15-20 images per person, making the solution deployable for small groups without massive data bloat.
-   **Security & Privacy:** developing a custom local model ensures that sensitive biometric data does not need to be processed by third-party public APIs, ensuring better data sovereignty.

### **Relevance**

-   **Event Tech:** Real-time photo sharing platforms for convocations and fests.
-   **Generic Applicability:** The pipeline (Data Collection $\rightarrow$ Embedding Generation $\rightarrow$ Classification) is relevant to any domain requiring object recognition with limited data (e.g., identifying rare plant species).

## 3. Type of Data to be Collected
We will create a **Custom Face Dataset** specifically for this project, as standard datasets (like LFW or CelebA) do not reflect the specific constraints of our target environment.

-   **Classes:** 5 distinct classes (individuals/students).
-   **Volume:** Approximately **15-20 images per class**, totaling ~100 images.
-   **Variations:** The dataset will be curated to include:
    -   **Pose Variations:** Frontal, profile, and semi-profile views.
    -   **Lighting Conditions:** Natural daylight, artificial indoor lighting, and shadow handling.
    -   **Expressions:** Neutral, smiling, and random natural expressions.
    -   **Occlusions:** Partial occlusions (e.g., glasses) to test model robustness.
-   **Format:** High-resolution JPEG/PNG images, which will be preprocessed into standardized tensors.

## 4. Expected Deep Learning Approach
To address the challenge of limited training data, we will employ a **Transfer Learning** methodology rather than training a Convolutional Neural Network (CNN) from scratch.

### **Proposed Architecture:**
1.  **Face Detection:**
    -   We will use **Haar Cascades** or **MTCNN (Multi-task Cascaded Convolutional Networks)** to detect and crop faces from raw images, removing background noise.

2.  **Feature Extraction (Backbone):**
    -   We will utilize the **FaceNet (Inception-ResNet v1)** architecture, pre-trained on the VGGFace2 dataset.
    -   This pre-trained model will act as a feature extractor, converting each 160x160 aligned face image into a high-dimensional **1024-dimensional embedding vector**. This vector numerically represents facial features (jawline, eye distance, etc.).

3.  **Classification (Head):**
    -   A custom **Multi-Layer Perceptron (MLP)** will be attached to the output of the FaceNet backbone.
    -   **Input Layer:** 1024 neurons (matching the embedding size).
    -   **Hidden Layers:** Dense layers with **ReLU** activation and **Dropout** (to prevent overfitting on the small dataset).
    -   **Output Layer:** A **Softmax** layer to output probability distributions across the 5 target classes.

### **Training Strategy:**
-   **Loss Function:** Cross-Entropy Loss (standard for multi-class classification).
-   **Optimizer:** Adam Optimizer for adaptive learning rates.
-   **Validation:** Implementation of a Train-Validation split (80-20) to monitor generalization and avoid overfitting.
