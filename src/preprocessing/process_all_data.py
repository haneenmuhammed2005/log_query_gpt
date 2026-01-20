import sys
print("🚀 process_all_data.py started")

sys.path.append('src')

from preprocessing.clean_logs import LogCleaner
import pandas as pd
import os

def process_log_file(input_path: str, output_path: str):
    """
    Process one log file
    
    Args:
        input_path: Path to raw .log file
        output_path: Path to save cleaned CSV
    """
    print(f"\n{'=' * 60}")
    print(f"Processing: {input_path}")
    print('=' * 60)
    
    # Read raw logs
    print("📖 Reading raw logs...")
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        raw_logs = f.readlines()
    
    print(f"   Found {len(raw_logs)} raw logs")
    
    # Clean logs
    print("🧹 Cleaning logs...")
    cleaner = LogCleaner()
    cleaned_logs = cleaner.clean_batch(raw_logs)
    
    print(f"   Cleaned {len(cleaned_logs)} logs")
    
    # Save to CSV
    print(f"💾 Saving to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cleaner.save_to_csv(raw_logs, cleaned_logs, output_path)
    
    print(f"✅ Saved successfully!")


# === PROCESS ALL DATASETS ===
if __name__ == "__main__":
    print("=" * 60)
    print("Processing All Log Datasets")
    print("=" * 60)
    
    # Define all datasets to process
    datasets = [
        ('data/raw_logs/HDFS_2k.log', 'data/processed_logs/HDFS_cleaned.csv'),
        ('data/raw_logs/BGL_2k.log', 'data/processed_logs/BGL_cleaned.csv')
    ]
    
    # Process each dataset
    for input_file, output_file in datasets:
        try:
            process_log_file(input_file, output_file)
        except Exception as e:
            print(f"❌ Error processing {input_file}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("✅ All datasets processed!")
    print("=" * 60)
    
    # Verify outputs
    print("\n📊 Verification:")
    for _, output_file in datasets:
        if os.path.exists(output_file):
            df = pd.read_csv(output_file)
            print(f"✅ {output_file}: {len(df)} logs")
        else:
            print(f"❌ {output_file}: NOT FOUND")