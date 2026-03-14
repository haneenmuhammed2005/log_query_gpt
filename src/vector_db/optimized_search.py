import faiss
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import time

class OptimizedVectorDB:
    """High-performance vector search with metadata filtering"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = None
        self.metadata = None
        self.index_type = "IVFFlat"
    
    def build_index(self, embeddings: np.ndarray, 
                   metadata_df: pd.DataFrame,
                   use_gpu: bool = False):
        """
        Build optimized FAISS index
        
        Args:
            embeddings: numpy array of shape (n, dimension)
            metadata_df: DataFrame with log metadata
            use_gpu: Use GPU acceleration if available
        """
        print("🏗️ Building optimized vector index...")
        print(f"📊 Vectors: {len(embeddings):,}")
        print(f"📏 Dimension: {self.dimension}")
        
        n_vectors = len(embeddings)
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Choose index type based on dataset size
        if n_vectors < 10000:
            # Small dataset: use flat index (exact search)
            print("🔍 Using Flat index (exact search)")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index_type = "Flat"
            
        else:
            # Large dataset: use IVF for speed
            nlist = min(int(np.sqrt(n_vectors)), 100)  # Number of clusters
            print(f"🔍 Using IVF index with {nlist} clusters")
            
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index_type = "IVFFlat"
            
            # Train index
            print("📚 Training index...")
            start_time = time.time()
            self.index.train(embeddings)
            print(f"✅ Training completed in {time.time() - start_time:.2f}s")
            
            # Set search parameters
            self.index.nprobe = min(10, nlist)  # Number of clusters to search
        
        # Move to GPU if requested
        if use_gpu and faiss.get_num_gpus() > 0:
            print("🚀 Moving index to GPU...")
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
            print("✅ GPU acceleration enabled")
        
        # Add vectors
        print("➕ Adding vectors to index...")
        start_time = time.time()
        self.index.add(embeddings)
        add_time = time.time() - start_time
        
        self.metadata = metadata_df
        
        print(f"✅ Index built successfully!")
        print(f"   ├─ Vectors indexed: {self.index.ntotal:,}")
        print(f"   ├─ Index type: {self.index_type}")
        print(f"   └─ Build time: {add_time:.2f}s")
    
    def search_with_filter(self, 
                          query_emb: np.ndarray,
                          k: int = 5,
                          protocol_filter: Optional[str] = None,
                          severity_filter: Optional[str] = None,
                          min_score: float = 0.0) -> List[Dict]:
        """
        Search with optional filtering
        
        Args:
            query_emb: Query embedding vector
            k: Number of results to return
            protocol_filter: Filter by protocol (e.g., 'modbus')
            severity_filter: Filter by severity (e.g., 'critical')
            min_score: Minimum similarity score threshold
            
        Returns:
            List of matching log entries with metadata
        """
        # Get more results if filtering is needed
        search_k = k * 5 if (protocol_filter or severity_filter) else k
        
        # Prepare query
        query = query_emb.reshape(1, -1).astype('float32')
        
        # Search
        start_time = time.time()
        distances, indices = self.index.search(query, search_k)
        search_time = time.time() - start_time
        
        # Process results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
            
            log_data = self.metadata.iloc[idx]
            
            # Calculate similarity score (inverse of L2 distance)
            similarity = float(1 / (1 + dist))
            
            # Apply score threshold
            if similarity < min_score:
                continue
            
            # Apply protocol filter
            if protocol_filter:
                log_protocols = log_data['protocols'].split(',')
                if protocol_filter not in log_protocols:
                    continue
            
            # Apply severity filter
            if severity_filter:
                if log_data.get('severity', '') != severity_filter:
                    continue
            
            # Add to results
            results.append({
                'log_text': log_data['cleaned'],
                'original': log_data['original'],
                'protocols': log_data['protocols'],
                'severity': log_data.get('severity', 'unknown'),
                'similarity_score': similarity,
                'distance': float(dist),
                'embedding_idx': int(idx)
            })
            
            # Stop if we have enough results
            if len(results) >= k:
                break
        
        # Log search performance
        if len(results) > 0:
            avg_score = sum(r['similarity_score'] for r in results) / len(results)
            print(f"🔍 Search: {len(results)} results in {search_time*1000:.2f}ms "
                  f"(avg score: {avg_score:.3f})")
        
        return results
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'metadata_rows': len(self.metadata) if self.metadata is not None else 0
        }
    
    def save_index(self, filepath: str):
        """Save index to disk"""
        faiss.write_index(self.index, filepath)
        print(f"💾 Index saved to: {filepath}")
    
    def load_index(self, filepath: str):
        """Load index from disk"""
        self.index = faiss.read_index(filepath)
        print(f"📂 Index loaded from: {filepath}")

# Testing and demonstration
if __name__ == "__main__":
    # Load enhanced data
    print("Loading enhanced embeddings and metadata...")
    embeddings = np.load('data/embeddings/HDFS_enhanced.npy')
    metadata = pd.read_csv('data/processed_logs/HDFS_enhanced.csv')
    
    print(f"✅ Loaded {len(embeddings)} embeddings")
    print(f"✅ Loaded {len(metadata)} metadata entries")
    
    # Build index
    db = OptimizedVectorDB()
    db.build_index(embeddings, metadata)
    
    # Test searches
    print("\n" + "="*70)
    print("Testing Vector Search")
    print("="*70)
    
    # Test 1: Basic search
    print("\n1️⃣ Basic Search:")
    query = embeddings[0]
    results = db.search_with_filter(query, k=5)
    for i, r in enumerate(results, 1):
        print(f"   {i}. [{r['protocols']}] {r['log_text'][:60]}...")
        print(f"      Score: {r['similarity_score']:.3f}")
    
    # Test 2: Protocol filtered search
    print("\n2️⃣ Protocol Filtered Search (modbus):")
    results = db.search_with_filter(query, k=5, protocol_filter='modbus')
    for i, r in enumerate(results, 1):
        print(f"   {i}. [{r['protocols']}] {r['log_text'][:60]}...")
    
    # Test 3: Severity filtered search
    print("\n3️⃣ Severity Filtered Search (critical):")
    results = db.search_with_filter(query, k=5, severity_filter='critical')
    for i, r in enumerate(results, 1):
        print(f"   {i}. [{r['severity']}] {r['log_text'][:60]}...")
    
    # Save index
    print("\n💾 Saving index...")
    db.save_index('data/vector_db/HDFS_optimized.index')
    metadata.to_csv('data/vector_db/HDFS_optimized_metadata.csv', index=False)
    
    print("\n✅ Optimization complete!")