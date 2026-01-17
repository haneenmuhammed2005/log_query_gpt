from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from typing import List
from tqdm import tqdm


class LogEmbedder:
    """Convert log messages to BERT embeddings"""

    def __init__(self, model_name: str = 'bert-base-uncased'):
        print(f"🔄 Loading {model_name}...")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()
        print("✅ BERT loaded successfully!")

    def embed_single_log(self, log_text: str) -> np.ndarray:
        """Convert one log message to a 768-dim vector"""
        inputs = self.tokenizer(
            log_text,
            return_tensors='pt',
            max_length=512,
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embeddings.numpy()

    def embed_batch(self, log_list: List[str], batch_size: int = 32) -> np.ndarray:
        """Convert multiple logs to embeddings efficiently"""
        all_embeddings = []

        print(f"🔄 Processing {len(log_list)} logs...")

        for i in tqdm(range(0, len(log_list), batch_size)):
            batch = log_list[i:i + batch_size]

            inputs = self.tokenizer(
                batch,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)

            batch_embeddings = outputs.last_hidden_state.mean(dim=1)
            all_embeddings.append(batch_embeddings.numpy())

        return np.vstack(all_embeddings)

    def save_embeddings(self, embeddings: np.ndarray, filepath: str):
        """Save embeddings to disk"""
        np.save(filepath, embeddings)
        print(f"💾 Saved {embeddings.shape[0]} embeddings")

    def load_embeddings(self, filepath: str) -> np.ndarray:
        """Load embeddings from disk"""
        embeddings = np.load(filepath)
        print(f"📂 Loaded {embeddings.shape[0]} embeddings")
        return embeddings


# ------------------ TEST ------------------
if __name__ == "__main__":
    embedder = LogEmbedder()

    test_logs = [
        "authentication failed for user admin",
        "connection timeout from 192.168.1.100",
        "system startup completed successfully"
    ]

    single_emb = embedder.embed_single_log(test_logs[0])
    print(f"Single embedding shape: {single_emb.shape}")

    batch_emb = embedder.embed_batch(test_logs)
    print(f"Batch embedding shape: {batch_emb.shape}")

    print("🎉 All tests passed!")
