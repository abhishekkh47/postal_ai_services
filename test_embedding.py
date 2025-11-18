#!/usr/bin/env python3
"""
Simple test to check if embedding generation works
"""
import sys
sys.path.append('.')

print("Testing embedding generation...")

try:
    print("1. Importing EmbeddingsService...")
    from src.services.embeddings_service import EmbeddingsService
    
    print("2. Creating service instance...")
    service = EmbeddingsService()
    
    print("3. Testing simple text...")
    test_text = "Hello world"
    print(f"   Input: '{test_text}'")
    
    print("4. Generating embedding...")
    embedding = service.generate_embedding(test_text)
    
    print(f"5. Success! Generated embedding with {len(embedding)} dimensions")
    print(f"   First 5 values: {embedding[:5]}")
    
    print("\n✓ Embedding service is working!")
    
except Exception as e:
    import traceback
    print(f"\n✗ Error: {e}")
    print(traceback.format_exc())
    sys.exit(1)

