"""
Custom Face Classifier using PyTorch.
This is a simple Multi-Layer Perceptron (MLP) that takes face embeddings
from pre-trained models (ArcFace/FaceNet) and classifies them into person categories.
"""

import torch
import torch.nn as nn


class FaceClassifier(nn.Module):
    """
    Simple MLP for face classification.
    Takes 1024-dimensional embeddings from the Super-Ensemble and outputs class probabilities.
    """
    
    def __init__(self, input_dim=1024, hidden_dim=256, num_classes=5, dropout=0.3):
        """
        Initialize the classifier.
        
        Args:
            input_dim: Dimension of input embeddings (1024 for Super-Ensemble)
            hidden_dim: Hidden layer dimension
            num_classes: Number of people to classify
            dropout: Dropout rate for regularization
        """
        super(FaceClassifier, self).__init__()
        
        self.network = nn.Sequential(
            # First hidden layer
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            # Second hidden layer
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            # Output layer
            nn.Linear(hidden_dim // 2, num_classes)
        )
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Input embeddings (batch_size, input_dim)
            
        Returns:
            Class logits (batch_size, num_classes)
        """
        return self.network(x)
