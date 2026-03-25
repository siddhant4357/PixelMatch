import os
import shutil
import random
from pathlib import Path
from typing import List, Set

def split_dataset(train_dir="data/training_dataset", test_dir="data/test_dataset", split_ratio=0.8):
    train_path = Path(train_dir)
    test_path = Path(test_dir)
    
    if not train_path.exists():
        print(f"Error: {train_path} does not exist.")
        return
        
    # Create test directory
    test_path.mkdir(parents=True, exist_ok=True)
    
    # Process each person class
    for person_dir in train_path.iterdir():
        if not person_dir.is_dir():
            continue
            
        person_name = person_dir.name
        person_test_dir = test_path / person_name
        person_test_dir.mkdir(exist_ok=True)
        
        # Get all images
        images_set: Set[Path] = set()
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            images_set.update(person_dir.glob(ext))
        images: List[Path] = list(images_set)
            
        # Optional: ensure reproducible random split
        random.seed(42)
        images.sort() # Sort before shuffle to ensure consistency across runs when using set
        random.shuffle(images)
        
        split_idx = int(len(images) * split_ratio)
        test_images = [images[i] for i in range(split_idx, len(images))]
        
        print(f"[{person_name}]: Moving {len(test_images)} out of {len(images)} images to test set")
        
        # Move images linearly to test directory
        for img_path in test_images:
            shutil.move(str(img_path), str(person_test_dir / img_path.name))

if __name__ == "__main__":
    split_dataset()
