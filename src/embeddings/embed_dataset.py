from log_embedder import LogEmbedder
import pandas as pd
import numpy as np
import os

def embed_full_dataset(input_csv: str, output_npy: str):
    """
    Process entire log dataset and create embeddings
    
    Args:
        input_csv: Path to cleaned CSV (from Week 1)
        output_npy: Path to save embeddings
    """
    print(f"📖 Reading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # Get cleaned logs
    logs = df['cleaned'].tolist()
    print(f"Found {len(logs)} logs to embed")
    
    # Initialize embedder (from Week 1)
    print("🔄 Loading BERT model...")
    embedder = LogEmbedder()
    
    # Create embeddings in batches
    print("🚀 Creating embeddings...")
    embeddings = embedder.embed_batch(logs, batch_size=32)
    
    # Save to disk
    os.makedirs(os.path.dirname(output_npy), exist_ok=True)
    embedder.save_embeddings(embeddings, output_npy)
    
    print(f"✅ Complete! Shape: {embeddings.shape}")
    print(f"   Saved to: {output_npy}")
    return embeddings

if __name__ == "__main__":
    # Process HDFS dataset
    print("=" * 60)
    print("Processing HDFS Dataset")
    print("=" * 60)
    
    embed_full_dataset(
        input_csv='data/processed_logs/HDFS_cleaned.csv',
        output_npy='data/embeddings/HDFS_embeddings.npy'
    )
    
    # Process BGL dataset
    print("\n" + "=" * 60)
    print("Processing BGL Dataset")
    print("=" * 60)
    
    embed_full_dataset(
        input_csv='data/processed_logs/BGL_cleaned.csv',
        output_npy='data/embeddings/BGL_embeddings.npy'
    )