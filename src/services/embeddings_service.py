from typing import List, Union
import numpy as np
from src.core.config import settings
import os

# Set environment variables BEFORE importing PyTorch or transformers
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Now import PyTorch and sentence-transformers
import torch
torch.set_num_threads(1)

from sentence_transformers import SentenceTransformer


class EmbeddingsService:
    """Service for generating text embeddings using sentence-transformers"""
    
    def __init__(self):
        """Initialize the embeddings model"""
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        # Load model with device='cpu' explicitly
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL, device='cpu')
        self.dimension = settings.EMBEDDING_DIMENSION
        print(f"Embedding model loaded successfully. Dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimension
        
        # Disable multiprocessing and use single batch
        embedding = self.model.encode(
            text, 
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=1
        )
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Replace empty strings with placeholder
        processed_texts = [text if text.strip() else " " for text in texts]
        
        embeddings = self.model.encode(processed_texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1 (higher is more similar)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    
    def generate_user_embedding(self, user_data: dict) -> List[float]:
        """
        Generate embedding for a user based on their profile
        
        Args:
            user_data: Dictionary containing user information (firstName, lastName, bio, etc.)
            
        Returns:
            Embedding vector for the user
        """
        # Combine user information into a single text
        text_parts = []
        
        if user_data.get('firstName'):
            text_parts.append(user_data['firstName'])
        if user_data.get('lastName'):
            text_parts.append(user_data['lastName'])
        if user_data.get('bio'):
            text_parts.append(user_data['bio'])
        
        # Create a descriptive text
        user_text = " ".join(text_parts)
        
        if not user_text.strip():
            user_text = "user profile"  # Fallback for empty profiles
        
        return self.generate_embedding(user_text)
    
    def generate_post_embedding(self, post_data: dict) -> List[float]:
        """
        Generate embedding for a post
        
        Args:
            post_data: Dictionary containing post information (post text, etc.)
            
        Returns:
            Embedding vector for the post
        """
        post_text = post_data.get('post', '')
        
        if not post_text.strip():
            post_text = "post content"  # Fallback for empty posts
        
        return self.generate_embedding(post_text)

