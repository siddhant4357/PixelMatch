# Oral Presentation / Viva Slide Deck Template

Follow this exact structure for your PowerPoint or Canva presentation! It directly addresses the grading criteria for Phase 6 (15% Weightage + 10% Viva).

**Slide 1: Title Slide**
- Project Title: PixelMatch End-to-End Face Recognition
- Your Names & Role
- Course Code

**Slide 2: The Core Problem**
- Brief explanation of the "Needle in a Haystack" problem at university events.
- Why existing solutions (like large Cloud APIs) aren't ideal (privacy, lack of offline support).

**Slide 3: Our Solution (The Proposal)**
- The Deep Learning Approach: "We utilized Transfer Learning, shifting from a complex Computer Vision problem to a mathematical Feature Embedding problem, allowing us to train a highly accurate classifier with only 20 images per person."

**Slide 4: The Dataset (Originality)**
- Display a tiny grid of 5-10 sample photos from your dataset.
- Prove to the faculty it is 100% original. 
- Mention the variations you captured: Expressions, Light, Pose.

**Slide 5: Explosive Data Splitting**
- Explain your dynamic split (70% Train, 15% Validation, 15% strict Test).
- Emphasize that your Testing code only loads data mapped inside a JSON log, ensuring ABSOLUTE segregation from the training variables.

**Slide 6: Architecture / Flowchart**
- Raw Image -> MTCNN Detection -> Face Crop -> FaceNet (Feature Extractor) -> 1024-d Vector -> Custom MLP.
- (Use graphics from your `PHASE_3_4_CONTENT.md`)

**Slide 7: Overcoming Overfitting (Crucial for Grade)**
- Display your `training_curves.png`.
- Explain how the dataset size made the model inherently prone to overfitting.
- Outline your dual-defense mitigation strategy: **Adam L2 Regularization (Weight Decay)** + **Dropout(0.3)**.

**Slide 8: Hyperparameter Tuning / Comparison**
- Briefly flash the two experiments from your Phase 5 log.
- "We experimented with Learning Rates (0.001 vs 0.01) to compare stability, selecting 0.001 due to smoother convergence along the 50 epochs."

**Slide 9: Error Analysis**
- Display your `confusion_matrix.png`.
- Highlight where the model succeeded.
- Point to exactly 1 error box in the matrix and physically explain why it failed (e.g. "Because of extreme side-profile bounding boxes, the FaceNet embeddings overlapped slightly with Class B"). 

**Slide 10: Conclusion & Demo**
- "Deep learning is not about models alone—it is about data, design, and decisions."
- Show screenshots or a live demo of the pipeline/web app working.
