import faiss
import numpy as np
import pandas as pd
import pickle
from typing import List, Dict

class VectorDatabase:
    """
    FAISS-based vector database for log embeddings
    
    Features:
    - Build searchable index from embeddings
    - Find k most similar logs to a query
    - Save/load index from disk
    """
    
    def __init__(self, dimension: int = 768):
        """
        Initialize vector database
        
        Args:
            dimension: Size of embedding vectors (768 for BERT)
        """
        self.dimension = dimension
        self.index = None
        self.log_texts = []
        self.log_metadata = []
    
    def build_index(self, embeddings: np.ndarray, log_df: pd.DataFrame):
        """
        Build searchable FAISS index
        
        Args:
            embeddings: numpy array of shape (N, 768)
            log_df: DataFrame with columns ['original', 'cleaned']
        """
        print(f"🏗️ Building FAISS index for {len(embeddings)} vectors...")
        
        # Create L2 distance index (measures similarity)
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Add all embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        # Store log texts for retrieval
        self.log_texts = log_df['cleaned'].tolist()
        self.log_metadata = log_df.to_dict('records')
        
        print(f"✅ Index built! Total vectors: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Find k most similar logs to query
        
        Args:
            query_embedding: Query vector of shape (768,)
            k: Number of results to return
            
        Returns:
            List of dicts with log_text, similarity_score, etc.
        """
        if self.index is None:
            raise ValueError("Index not built! Call build_index() first.")
        
        # Reshape query to (1, 768) for FAISS
        query = query_embedding.reshape(1, -1).astype('float32')
        
        # Search for k nearest neighbors
        distances, indices = self.index.search(query, k)
        
        # Format results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            results.append({
                'log_text': self.log_texts[idx],
                'original': self.log_metadata[idx]['original'],
                'similarity_score': float(1 / (1 + dist)),  # Convert distance to similarity
                'distance': float(dist)
            })
        
        return results
    
    def save(self, index_path: str, metadata_path: str):
        """
        Save index and metadata to disk
        
        Args:
            index_path: Path to save FAISS index (.faiss)
            metadata_path: Path to save metadata (.pkl)
        """
        print(f"💾 Saving index to {index_path}...")
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata (log texts, etc.)
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'log_texts': self.log_texts,
                'log_metadata': self.log_metadata
            }, f)
        
        print("✅ Saved successfully!")
    
    def load(self, index_path: str, metadata_path: str):
        """
        Load existing index from disk
        
        Args:
            index_path: Path to FAISS index
            metadata_path: Path to metadata
        """
        print(f"📖 Loading index from {index_path}...")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.log_texts = data['log_texts']
            self.log_metadata = data['log_metadata']
        
        print(f"✅ Loaded {self.index.ntotal} vectors!")


# === TEST THE DATABASE ===
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Vector Database")
    print("=" * 60)
    
    # Load embeddings and data
    print("\n1️⃣ Loading embeddings...")
    embeddings = np.load('data/embeddings/HDFS_embeddings.npy')
    df = pd.read_csv('data/processed_logs/HDFS_cleaned.csv')
    print(f"   Loaded {len(embeddings)} embeddings")
    
    # Build index
    print("\n2️⃣ Building index...")
    db = VectorDatabase()
    db.build_index(embeddings, df)
    
    # Test search
    print("\n3️⃣ Testing search...")
    query_emb = embeddings[0]  # Use first log as query
    results = db.search(query_emb, k=3)
    
    print("\n🔍 Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity Score: {result['similarity_score']:.3f}")
        print(f"   Log: {result['log_text'][:100]}...")
    
    # Save index
    print("\n4️⃣ Saving index...")
    db.save(
        'data/vector_db/HDFS_index.faiss',
        'data/vector_db/HDFS_metadata.pkl'
    )
    
    print("\n✅ Test complete!")