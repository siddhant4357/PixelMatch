# Phase 3: Data Preprocessing & Analysis
**Duration:** 16 Feb – 29 Feb 2026

## Activities & Implementations
*   **Data Cleaning:** We processed the raw dataset to remove invalid, heavily blurred, or improperly cropped face images. This ensures the models learn from high-quality, clear facial features.
*   **Normalization & Feature Extraction:** Face images were mathematically aligned and cropped. The pixel values were normalized (scaled) to ensure stable and fast convergence during the model training process.
*   **Train–Validation–Test Split:** The unified dataset folder was completely loaded into RAM and mathematically split using `sklearn` at a strict **70% Training / 15% Validation / 15% Test** ratio. The 15% testing paths are explicitly saved to JSON logs to ensure the final evaluation script only runs against strictly unseen data, preventing any data leakage.
*   **Exploratory Data Analysis (EDA):** We analyzed the distribution of images per identity, checked for class imbalances, and reviewed variations in lighting and posing across the dataset.

## Deliverables
*   **Preprocessed Dataset:** Cleaned, aligned, and normalized image batches ready for neural network consumption.
*   **Data Analysis Report:** Insights, distribution charts, and observations confirming data readiness.

---

# Phase 4: Model Design & Implementation
**Duration:** 01 Mar – 20 Mar 2026

This phase focuses on the core Deep Learning architecture. For facial recognition and matching, we selected Deep Convolutional Neural Networks (CNNs). Below are the foundational components and architecture designs evaluated for the project.

## 1. Core Building Blocks (Architecture Selection)
Our models rely on standard deep learning components to extract non-linear facial features from the preprocessed data.

### Convolutional Layer
The Convolutional Layer is the foundation of our CNN. It uses a sliding filter (kernel) over the input image matrix to perform dot products, effectively extracting critical spatial features—starting from simple edges and textures in early layers to complex facial structures in deeper layers.  

![Convolutional Layer](assets/convolution.png)

### Activation Function
To allow the network to learn complex representations of human faces, we apply an Activation Function (such as ReLU or PReLU) immediately after the convolutions. It acts as a mathematical gate, introducing necessary non-linearity into the network so it can model complex data boundaries.  

![Activation Function](assets/actibation_fun.png)

## 2. Architecture Diagrams (Deliverables)
We evaluated two prominent architectures for extracting face embeddings. These skeletons are critical for the face comparison pipeline.

### FaceNet Architecture Skeleton
FaceNet maps face images into a 128-dimensional Euclidean space. Its defining characteristic is the **Triplet Loss Function**, which explicitly minimizes the distance between an Anchor image and a Positive image (the same person) while maximizing the margin to a Negative image (a different person).  

![FaceNet Skeleton](assets/facenet_skeleton.png)

### ResNet / ArcFace Architecture Skeleton
ArcFace typically utilizes a deep CNN backbone like the **ResNet skeleton** (e.g., ResNet-50) to extract a highly robust 512-dimensional feature vector. It employs an **Additive Angular Margin Loss** instead of standard Softmax, which adds a strict angular penalty to the target class, forcing highly compact clusters for the same identity and wide margins between different identities.  

![ResNet/ArcFace Skeleton](assets/resnet_skeleton.png)

## 3. Training Strategy, Loss Function, and Optimizer
*   **Loss Functions:** Triplet Loss (for FaceNet) and Additive Angular Margin Loss (for ArcFace).
*   **Optimizer Selection:** Adam Optimizer enhanced with **L2 Regularization (Weight Decay: 1e-4)**. This mathematical penalty prevents the Custom MLP classifier from overfitting our deeply constrained 20-image-per-class dataset.
*   **Training Strategy:** Defined hyper-parameters including optimal Batch Size (to fit into GPU memory without causing erratic updates), the number of Epochs (to ensure the model converges without overfitting), and the Learning Rate (including step-decay scheduling).

## Deliverables Status
*   **Model Code:** Defined and implemented convolutions, activation functions, and custom forward passes.
*   **Architecture Diagrams:** Provided above.
*   **Training Logs:** Tracked loss reduction, accuracy improvements, and validation metrics across training epochs.
