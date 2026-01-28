"""
Optimized batch processing for large datasets with GPU/CPU support
Fixes: Import paths, error handling, checkpoint recovery
"""

import torch
import numpy as np
from typing import List, Tuple, Optional
from tqdm import tqdm
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from embeddings.log_embedder import LogEmbedder
except ImportError:
    print("⚠️ Could not import LogEmbedder. Make sure Week 1 is complete.")
    print("Expected path: src/embeddings/log_embedder.py")
    sys.exit(1)


class BatchProcessor:
    """Optimized batch processing for large datasets with checkpointing"""
    
    def __init__(self, use_gpu: bool = False, checkpoint_dir: str = 'data/checkpoints'):
        """
        Initialize batch processor
        
        Args:
            use_gpu: Whether to attempt GPU usage
            checkpoint_dir: Directory to save checkpoints
        """
        self.embedder = LogEmbedder()
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # GPU setup with proper error handling
        self.use_gpu = False
        if use_gpu:
            if torch.cuda.is_available():
                try:
                    self.embedder.model = self.embedder.model.cuda()
                    self.use_gpu = True
                    print("✅ Using GPU acceleration")
                    print(f"   Device: {torch.cuda.get_device_name(0)}")
                except Exception as e:
                    print(f"⚠️ GPU initialization failed: {e}")
                    print("   Falling back to CPU")
                    self.use_gpu = False
            else:
                print("ℹ️ GPU requested but not available. Using CPU")
        else:
            print("ℹ️ Using CPU")
    
    def process_large_dataset(
        self, 
        log_list: List[str], 
        batch_size: int = 64,
        save_interval: int = 1000,
        resume_from_checkpoint: bool = True
    ) -> np.ndarray:
        """
        Process large datasets with progress saving
        
        Args:
            log_list: List of log strings to embed
            batch_size: Number of logs to process at once
            save_interval: Save checkpoint every N logs
            resume_from_checkpoint: Try to resume from last checkpoint
        
        Returns:
            numpy array of embeddings (num_logs, embedding_dim)
        """
        
        total_logs = len(log_list)
        all_embeddings = []
        start_idx = 0
        
        # Try to resume from checkpoint
        if resume_from_checkpoint:
            checkpoint_file, last_idx = self._find_latest_checkpoint()
            if checkpoint_file:
                print(f"📂 Found checkpoint: {checkpoint_file}")
                response = input(f"Resume from log {last_idx}? (y/n): ")
                if response.lower() == 'y':
                    try:
                        checkpoint_data = np.load(checkpoint_file)
                        all_embeddings.append(checkpoint_data)
                        start_idx = last_idx
                        print(f"✅ Resumed from {start_idx} logs")
                    except Exception as e:
                        print(f"⚠️ Could not load checkpoint: {e}")
                        print("   Starting from beginning")
        
        print(f"📊 Processing {total_logs} logs (starting from {start_idx})...")
        
        # Process in batches with progress bar
        for idx in tqdm(range(start_idx, total_logs, batch_size), desc="Processing batches"):
            end_idx = min(idx + batch_size, total_logs)
            batch = log_list[idx:end_idx]
            
            try:
                # Tokenize batch
                inputs = self.embedder.tokenizer(
                    batch,
                    return_tensors='pt',
                    max_length=512,
                    truncation=True,
                    padding=True
                )
                
                # Move to GPU if available
                if self.use_gpu:
                    try:
                        inputs = {k: v.cuda() for k, v in inputs.items()}
                    except Exception as e:
                        print(f"\n⚠️ GPU transfer failed: {e}")
                        print("   Falling back to CPU for this batch")
                        self.use_gpu = False
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.embedder.model(**inputs)
                
                # Get embeddings and move to CPU
                batch_emb = outputs.last_hidden_state.mean(dim=1)
                if self.use_gpu:
                    batch_emb = batch_emb.cpu()
                
                all_embeddings.append(batch_emb.numpy())
                
                # Save checkpoint every save_interval logs
                if ((end_idx % save_interval == 0) or (end_idx == total_logs)) and end_idx > start_idx:
                    checkpoint_emb = np.vstack(all_embeddings)
                    checkpoint_file = os.path.join(
                        self.checkpoint_dir, 
                        f'checkpoint_{end_idx}.npy'
                    )
                    np.save(checkpoint_file, checkpoint_emb)
                    print(f"\n💾 Checkpoint saved: {checkpoint_file}")
                    
            except Exception as e:
                print(f"\n❌ Error processing batch {idx}-{end_idx}: {e}")
                print("   Saving checkpoint and exiting...")
                if all_embeddings:
                    checkpoint_emb = np.vstack(all_embeddings)
                    checkpoint_file = os.path.join(
                        self.checkpoint_dir, 
                        f'checkpoint_error_{idx}.npy'
                    )
                    np.save(checkpoint_file, checkpoint_emb)
                    print(f"   Saved to {checkpoint_file}")
                raise
        
        # Combine all embeddings
        if not all_embeddings:
            raise ValueError("No embeddings were generated!")
        
        final_embeddings = np.vstack(all_embeddings)
        
        print(f"\n✅ Successfully processed {len(final_embeddings)} logs")
        print(f"   Shape: {final_embeddings.shape}")
        print(f"   Memory: {final_embeddings.nbytes / 1024 / 1024:.2f} MB")
        
        return final_embeddings
    
    def _find_latest_checkpoint(self) -> Tuple[Optional[str], int]:
        """Find the latest checkpoint file"""
        if not os.path.exists(self.checkpoint_dir):
            return None, 0
        
        checkpoint_files = [
            f for f in os.listdir(self.checkpoint_dir) 
            if f.startswith('checkpoint_') and f.endswith('.npy')
        ]
        
        if not checkpoint_files:
            return None, 0
        
        # Extract indices and find max
        indices = []
        for f in checkpoint_files:
            try:
                idx = int(f.replace('checkpoint_', '').replace('.npy', '').replace('error_', ''))
                indices.append((idx, f))
            except ValueError:
                continue
        
        if not indices:
            return None, 0
        
        latest_idx, latest_file = max(indices, key=lambda x: x[0])
        return os.path.join(self.checkpoint_dir, latest_file), latest_idx
    
    def estimate_time(self, num_logs: int, batch_size: int = 64, sample_size: int = 100) -> float:
        """
        Estimate processing time for a dataset
        
        Args:
            num_logs: Total number of logs to process
            batch_size: Batch size to use
            sample_size: Number of logs to test with
        
        Returns:
            Estimated total time in seconds
        """
        print(f"⏱️ Estimating processing time...")
        
        # Create test logs
        test_logs = ["Sample log entry for timing test"] * min(sample_size, num_logs)
        
        import time
        start = time.time()
        
        try:
            _ = self.embedder.embed_batch(test_logs, batch_size=batch_size)
            elapsed = time.time() - start
        except Exception as e:
            print(f"⚠️ Estimation failed: {e}")
            return 0.0
        
        # Calculate estimate
        total_batches = num_logs / batch_size
        test_batches = len(test_logs) / batch_size
        estimated_total = (elapsed / test_batches) * total_batches
        
        minutes = int(estimated_total // 60)
        seconds = int(estimated_total % 60)
        
        print(f"   Sample: {len(test_logs)} logs in {elapsed:.2f}s")
        print(f"   Estimated total: {minutes}m {seconds}s")
        print(f"   Speed: ~{len(test_logs) / elapsed:.1f} logs/sec")
        
        return estimated_total
    
    def cleanup_checkpoints(self, keep_latest: bool = True):
        """
        Clean up checkpoint files
        
        Args:
            keep_latest: Keep the most recent checkpoint
        """
        if not os.path.exists(self.checkpoint_dir):
            return
        
        checkpoint_files = [
            f for f in os.listdir(self.checkpoint_dir) 
            if f.startswith('checkpoint_') and f.endswith('.npy')
        ]
        
        if keep_latest and checkpoint_files:
            _, latest_file = self._find_latest_checkpoint()
            checkpoint_files = [f for f in checkpoint_files if f != os.path.basename(latest_file)]
        
        for f in checkpoint_files:
            filepath = os.path.join(self.checkpoint_dir, f)
            try:
                os.remove(filepath)
                print(f"🗑️ Removed {f}")
            except Exception as e:
                print(f"⚠️ Could not remove {f}: {e}")
        
        print(f"✅ Cleanup complete")


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("BATCH PROCESSOR TEST")
    print("=" * 60)
    
    # Initialize processor
    processor = BatchProcessor(use_gpu=False)
    
    # Create test data
    print("\n📝 Creating test data...")
    test_logs = [
        f"Test log entry number {i}: This is a sample ICS log message" 
        for i in range(500)
    ]
    print(f"   Created {len(test_logs)} test logs")
    
    # Estimate time
    print("\n" + "=" * 60)
    processor.estimate_time(len(test_logs), batch_size=64)
    
    # Process
    print("\n" + "=" * 60)
    print("PROCESSING TEST DATASET")
    print("=" * 60)
    
    try:
        embeddings = processor.process_large_dataset(
            test_logs, 
            batch_size=64,
            save_interval=200,
            resume_from_checkpoint=False
        )
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"✅ Final shape: {embeddings.shape}")
        print(f"✅ Data type: {embeddings.dtype}")
        print(f"✅ Memory usage: {embeddings.nbytes / 1024 / 1024:.2f} MB")
        
        # Save final output
        output_file = 'data/test_embeddings.npy'
        os.makedirs('data', exist_ok=True)
        np.save(output_file, embeddings)
        print(f"✅ Saved to {output_file}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
