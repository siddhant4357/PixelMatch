"""
Dataset Analysis Script for PixelMatch
Generates statistical reports and visualizations for the training dataset.
Fulfills Phase 3 Requirement: "Data Analysis Report (charts + observations)"
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

def analyze_dataset():
    """Analyze the dataset structure and generate a report."""
    
    # Configuration
    dataset_path = Path("data/training_dataset")
    output_dir = Path("data/analysis_report")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"DATASET ANALYSIS STARTED")
    print(f"{'='*60}\n")
    
    if not dataset_path.exists():
        print(f"❌ Error: Dataset path not found: {dataset_path}")
        print("Please ensure you have organized your data into 'data/training_dataset/<person_name>/' folders.")
        return

    # 1. Collect Data Stats
    stats = []
    total_images = 0
    classes = []
    
    print("Scanning folders...")
    for person_folder in sorted(dataset_path.iterdir()):
        if person_folder.is_dir() and not person_folder.name.startswith('.'):
            # Count images
            images = list(person_folder.glob('*.[jJ][pP]*[gG]')) + list(person_folder.glob('*.png'))
            count = len(images)
            
            if count > 0:
                stats.append({
                    'Person': person_folder.name,
                    'Image Count': count
                })
                classes.append(person_folder.name)
                total_images += count
                print(f"  - {person_folder.name}: {count} images")
    
    if not stats:
        print("❌ No images found in dataset folders.")
        return

    df = pd.DataFrame(stats)
    
    # 2. Generate Visualizations
    print("\nGenerating charts...")
    sns.set_theme(style="whitegrid")
    
    # Plot 1: Class Distribution
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='Person', y='Image Count', data=df, palette='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.title('Dataset Distribution: Images per Person', fontsize=16, fontweight='bold')
    plt.xlabel('Person Name', fontsize=12)
    plt.ylabel('Number of Images', fontsize=12)
    plt.tight_layout()
    
    chart_path = output_dir / 'class_distribution.png'
    plt.savefig(chart_path, dpi=300)
    print(f"✓ Saved distribution chart to {chart_path}")
    plt.close()
    
    # Plot 2: Pie Chart (if < 10 classes) or just summary
    if len(classes) <= 10:
        plt.figure(figsize=(8, 8))
        plt.pie(df['Image Count'], labels=df['Person'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        plt.title('Dataset Composition', fontsize=16, fontweight='bold')
        plt.tight_layout()
        pie_path = output_dir / 'dataset_composition.png'
        plt.savefig(pie_path, dpi=300)
        print(f"✓ Saved composition chart to {pie_path}")
        plt.close()

    # 3. Generate Text Report
    report_content = f"""
# PixelMatch Dataset Analysis Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Dataset Summary
- **Total Images:** {total_images}
- **Total Classes (People):** {len(classes)}
- **Average Images per Class:** {total_images / len(classes):.1f}
- **Min Images:** {df['Image Count'].min()} ({df.loc[df['Image Count'].idxmin()]['Person']})
- **Max Images:** {df['Image Count'].max()} ({df.loc[df['Image Count'].idxmax()]['Person']})

## 2. Class Breakdown
| Person Name | Image Count | % of Total |
| :--- | :--- | :--- |
"""
    
    for _, row in df.iterrows():
        percentage = (row['Image Count'] / total_images) * 100
        report_content += f"| {row['Person']} | {row['Image Count']} | {percentage:.1f}% |\n"

    report_content += "\n## 3. Observations\n"
    
    # Auto-generate observations based on data
    imbalance = df['Image Count'].max() / df['Image Count'].min()
    if imbalance > 2.0:
        report_content += f"- **Class Imbalance:** The dataset shows significant imbalance (Max/Min ratio: {imbalance:.1f}). Techniques like augmentation or weighted loss function are recommended.\n"
    else:
        report_content += "- **Balance:** The dataset is relatively well-balanced across classes.\n"
        
    if total_images < 100:
        report_content += "- **Size:** The dataset is small (< 100 images). Transfer learning is highly recommended to avoid overfitting.\n"
    else:
        report_content += "- **Size:** The dataset size is adequate for fine-tuning pre-trained models.\n"

    report_path = output_dir / 'analysis_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✓ Saved text report to {report_path}")
    
    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"📂 Output Folder: {output_dir.absolute()}")
    print(f"✨ You can now include these charts in your 'Phase 3' report!")

if __name__ == "__main__":
    analyze_dataset()
