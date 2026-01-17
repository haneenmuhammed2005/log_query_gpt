"""
test_bert.py

Simple sanity check to verify:
- transformers is installed
- torch is working
- BERT can generate embeddings
"""

from transformers import AutoTokenizer, AutoModel
import torch


def main():
    print("🔍 Testing BERT installation...")

    model_name = "bert-base-uncased"

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Sample log message
    test_log = "authentication failed for user admin from ip 192.168.1.100"

    # Tokenize input
    inputs = tokenizer(
        test_log,
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    # Forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling to get sentence embedding
    embeddings = outputs.last_hidden_state.mean(dim=1)

    print("✅ BERT is working correctly!")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Sample values: {embeddings[0][:5]}")


if __name__ == "__main__":
    main()
