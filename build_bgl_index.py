"""
Run this ONCE to build the BGL FAISS index.
Place this file in your project root and run:
    python build_bgl_index.py
"""

import sys
sys.path.insert(0, "src")

import numpy as np
import pandas as pd
import faiss
import pickle
from pathlib import Path

def build_bgl_index():
    print("=" * 50)
    print("Building BGL FAISS Index")
    print("=" * 50)

    embeddings_path = "data/embeddings/BGL_embeddings.npy"
    csv_path        = "data/processed_logs/BGL_cleaned.csv"
    index_out       = "data/vector_db/BGL_index.faiss"
    metadata_out    = "data/vector_db/BGL_metadata.pkl"

    # Check files exist
    if not Path(embeddings_path).exists():
        print(f"ERROR: {embeddings_path} not found!")
        print("Run embed_dataset.py for BGL first.")
        return

    if not Path(csv_path).exists():
        print(f"ERROR: {csv_path} not found!")
        print("Run preprocessing for BGL first.")
        return

    print(f"\n1. Loading embeddings from {embeddings_path}...")
    embeddings = np.load(embeddings_path)
    print(f"   Shape: {embeddings.shape}")

    print(f"\n2. Loading log data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   Rows: {len(df)}")

    print("\n3. Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    print(f"   Vectors added: {index.ntotal}")

    print(f"\n4. Saving index to {index_out}...")
    Path("data/vector_db").mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, index_out)

    print(f"\n5. Saving metadata to {metadata_out}...")
    with open(metadata_out, 'wb') as f:
        pickle.dump({
            'log_texts': df['cleaned'].tolist(),
            'log_metadata': df.to_dict('records')
        }, f)

    print("\n✅ BGL index built successfully!")
    print(f"   Index:    {index_out}")
    print(f"   Metadata: {metadata_out}")

if __name__ == "__main__":
    build_bgl_index()
