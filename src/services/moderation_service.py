from typing import Dict, List, Tuple
import re
import os

# Set environment variables BEFORE importing PyTorch or transformers
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Now import PyTorch and Detoxify
import torch
torch.set_num_threads(1)

from detoxify import Detoxify


class ModerationService:
    """Service for content moderation (toxicity and spam detection)"""
    
    # Toxicity thresholds
    TOXICITY_THRESHOLD = 0.7  # Above this is flagged as toxic
    TOXICITY_WARNING_THRESHOLD = 0.5  # Above this shows warning
    
    # Spam patterns
    SPAM_KEYWORDS = [
        'click here', 'buy now', 'limited offer', 'act now',
        'free money', 'earn $$$', 'work from home', 'weight loss',
        'viagra', 'casino', 'lottery', 'prize winner'
    ]
    
    def __init__(self):
        """Initialize moderation models"""
        print("Loading toxicity detection model...")
        self.toxicity_model = Detoxify('original', device='cpu')
        print("Toxicity detection model loaded successfully")
    
    def check_toxicity(self, text: str) -> Dict[str, float]:
        """
        Check text for toxic content
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with toxicity scores for different categories
        """
        if not text or not text.strip():
            return {
                'toxicity': 0.0,
                'severe_toxicity': 0.0,
                'obscene': 0.0,
                'threat': 0.0,
                'insult': 0.0,
                'identity_attack': 0.0
            }
        
        try:
            results = self.toxicity_model.predict(text)
            # Convert numpy types to Python floats
            return {k: float(v) for k, v in results.items()}
        except Exception as e:
            print(f"Error in toxicity detection: {e}")
            return {
                'toxicity': 0.0,
                'severe_toxicity': 0.0,
                'obscene': 0.0,
                'threat': 0.0,
                'insult': 0.0,
                'identity_attack': 0.0
            }
    
    def check_spam(self, text: str) -> Tuple[float, List[str]]:
        """
        Check text for spam patterns
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (spam_score, matched_patterns)
        """
        if not text or not text.strip():
            return 0.0, []
        
        text_lower = text.lower()
        matched_patterns = []
        
        # Check for spam keywords
        for keyword in self.SPAM_KEYWORDS:
            if keyword in text_lower:
                matched_patterns.append(keyword)
        
        # Check for excessive URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(urls) > 2:
            matched_patterns.append('excessive_urls')
        
        # Check for excessive capitalization
        if len(text) > 10:
            capital_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if capital_ratio > 0.5:
                matched_patterns.append('excessive_caps')
        
        # Check for excessive exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            matched_patterns.append('excessive_exclamation')
        
        # Check for repeated characters (e.g., "hellooooo")
        if re.search(r'(.)\1{4,}', text):
            matched_patterns.append('repeated_characters')
        
        # Calculate spam score (0-1)
        spam_score = min(1.0, len(matched_patterns) * 0.2)
        
        return spam_score, matched_patterns
    
    def moderate_content(
        self,
        text: str,
        check_toxicity: bool = True,
        check_spam: bool = True
    ) -> Dict:
        """
        Perform full content moderation
        
        Args:
            text: Text to moderate
            check_toxicity: Whether to check for toxicity
            check_spam: Whether to check for spam
            
        Returns:
            Dictionary with moderation results
        """
        results = {
            'is_safe': True,
            'toxicity_score': 0.0,
            'spam_score': 0.0,
            'categories': {},
            'flagged_reasons': []
        }
        
        # Check toxicity
        if check_toxicity:
            toxicity_results = self.check_toxicity(text)
            results['toxicity_score'] = toxicity_results.get('toxicity', 0.0)
            results['categories'] = toxicity_results
            
            # Check if content should be flagged
            if results['toxicity_score'] >= self.TOXICITY_THRESHOLD:
                results['is_safe'] = False
                results['flagged_reasons'].append('high_toxicity')
            elif results['toxicity_score'] >= self.TOXICITY_WARNING_THRESHOLD:
                results['flagged_reasons'].append('moderate_toxicity')
            
            # Check specific categories
            if toxicity_results.get('severe_toxicity', 0) > 0.5:
                results['is_safe'] = False
                results['flagged_reasons'].append('severe_toxicity')
            if toxicity_results.get('threat', 0) > 0.5:
                results['is_safe'] = False
                results['flagged_reasons'].append('threat')
            if toxicity_results.get('identity_attack', 0) > 0.5:
                results['is_safe'] = False
                results['flagged_reasons'].append('identity_attack')
        
        # Check spam
        if check_spam:
            spam_score, spam_patterns = self.check_spam(text)
            results['spam_score'] = spam_score
            
            if spam_score > 0.6:
                results['is_safe'] = False
                results['flagged_reasons'].append('spam')
                results['spam_patterns'] = spam_patterns
            elif spam_score > 0.4:
                results['flagged_reasons'].append('possible_spam')
                results['spam_patterns'] = spam_patterns
        
        return results

