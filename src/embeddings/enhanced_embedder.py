import sys
sys.path.append('src')

from embeddings.log_embedder import LogEmbedder
from preprocessing.protocol_detector import ProtocolDetector
import pandas as pd
import numpy as np
from datetime import datetime

class EnhancedEmbedder:
    """Create embeddings with protocol and metadata awareness"""
    
    def __init__(self):
        self.embedder = LogEmbedder()
        self.detector = ProtocolDetector()
    
    def embed_with_metadata(self, log_df: pd.DataFrame) -> tuple:
        """
        Create embeddings with enhanced metadata
        
        Args:
            log_df: DataFrame with 'original' and 'cleaned' columns
            
        Returns:
            (embeddings array, enhanced dataframe)
        """
        print("🚀 Creating enhanced embeddings with metadata...")
        print(f"📊 Processing {len(log_df)} logs")
        
        # Step 1: Add protocol detection
        log_df = self.detector.add_protocol_tags(log_df)
        
        # Step 2: Create embeddings for cleaned logs
        print("\n🔄 Generating BERT embeddings...")
        embeddings = self.embedder.embed_batch(
            log_df['cleaned'].tolist(),
            batch_size=32,
            show_progress=True
        )
        
        # Step 3: Add embedding indices for quick lookup
        log_df['embedding_idx'] = range(len(log_df))
        
        # Step 4: Add timestamp for tracking
        log_df['processed_at'] = datetime.now().isoformat()
        
        print(f"\n✅ Created {len(embeddings)} embeddings")
        print(f"✅ Embedding shape: {embeddings.shape}")
        
        return embeddings, log_df
    
    def process_dataset(self, dataset_name: str):
        """
        Process a complete dataset with enhanced embeddings
        
        Args:
            dataset_name: Name like 'HDFS', 'BGL', etc.
        """
        print(f"\n{'='*70}")
        print(f"Processing {dataset_name} Dataset")
        print(f"{'='*70}\n")
        
        # Load cleaned data
        input_file = f'data/processed_logs/{dataset_name}_cleaned.csv'
        print(f"📂 Loading: {input_file}")
        
        try:
            df = pd.read_csv(input_file)
        except FileNotFoundError:
            print(f"❌ File not found: {input_file}")
            print("   Run data preprocessing first!")
            return
        
        # Create enhanced embeddings
        embeddings, enhanced_df = self.embed_with_metadata(df)
        
        # Save embeddings
        emb_output = f'data/embeddings/{dataset_name}_enhanced.npy'
        np.save(emb_output, embeddings)
        print(f"\n💾 Saved embeddings: {emb_output}")
        
        # Save enhanced metadata
        meta_output = f'data/processed_logs/{dataset_name}_enhanced.csv'
        enhanced_df.to_csv(meta_output, index=False)
        print(f"💾 Saved metadata: {meta_output}")
        
        # Display statistics
        print(f"\n📊 Dataset Statistics:")
        print(f"  Total logs: {len(enhanced_df)}")
        print(f"  Embedding dimension: {embeddings.shape[1]}")
        print(f"  Protocols detected: {len(enhanced_df['protocols'].unique())}")
        print(f"  Severity levels: {enhanced_df['severity'].value_counts().to_dict()}")
        
        # Show sample
        print(f"\n📋 Sample Enhanced Logs:")
        print(enhanced_df[['cleaned', 'protocols', 'severity']].head(3))
        
        return embeddings, enhanced_df

# Main execution
if __name__ == "__main__":
    enhancer = EnhancedEmbedder()
    
    # Process all datasets
    datasets = ['HDFS']  # Add more: ['HDFS', 'BGL', 'Thunderbird']
    
    for dataset in datasets:
        embeddings, df = enhancer.process_dataset(dataset)
        print(f"\n{'='*70}\n")