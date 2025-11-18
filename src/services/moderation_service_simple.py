"""
Simplified moderation service without heavy ML models
Uses rule-based toxicity detection instead of Detoxify
"""
from typing import Dict, List, Tuple
import re


class ModerationService:
    """Service for content moderation using rule-based approach"""
    
    # Toxicity thresholds
    TOXICITY_THRESHOLD = 0.7
    TOXICITY_WARNING_THRESHOLD = 0.5
    
    # Toxic words and patterns
    TOXIC_WORDS = [
        'stupid', 'idiot', 'dumb', 'hate', 'kill', 'die', 'ugly',
        'loser', 'moron', 'retard', 'shut up', 'fuck', 'shit',
        'bitch', 'ass', 'damn', 'hell', 'crap', 'suck', 'worst'
    ]
    
    SEVERE_TOXIC_WORDS = [
        'kill yourself', 'die', 'kys', 'suicide', 'murder',
        'rape', 'terrorist', 'bomb', 'attack'
    ]
    
    # Spam patterns
    SPAM_KEYWORDS = [
        'click here', 'buy now', 'limited offer', 'act now',
        'free money', 'earn $$$', 'work from home', 'weight loss',
        'viagra', 'casino', 'lottery', 'prize winner'
    ]
    
    def __init__(self):
        """Initialize moderation service"""
        print("Moderation service initialized (rule-based)")
    
    def check_toxicity(self, text: str) -> Dict[str, float]:
        """
        Check text for toxic content using rule-based approach
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with toxicity scores
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
        
        text_lower = text.lower()
        
        # Count toxic words
        toxic_count = sum(1 for word in self.TOXIC_WORDS if word in text_lower)
        severe_count = sum(1 for word in self.SEVERE_TOXIC_WORDS if word in text_lower)
        
        # Calculate scores (0-1)
        toxicity_score = min(1.0, toxic_count * 0.3)
        severe_toxicity_score = min(1.0, severe_count * 0.5)
        
        # Check for specific patterns
        insult_score = 0.0
        if any(word in text_lower for word in ['stupid', 'idiot', 'dumb', 'moron', 'loser']):
            insult_score = 0.7
        
        threat_score = 0.0
        if any(word in text_lower for word in ['kill', 'die', 'murder', 'attack']):
            threat_score = 0.8
        
        obscene_score = 0.0
        if any(word in text_lower for word in ['fuck', 'shit', 'bitch', 'ass']):
            obscene_score = 0.6
        
        # Overall toxicity is the max of all categories
        overall_toxicity = max(toxicity_score, severe_toxicity_score, insult_score, threat_score, obscene_score)
        
        return {
            'toxicity': overall_toxicity,
            'severe_toxicity': severe_toxicity_score,
            'obscene': obscene_score,
            'threat': threat_score,
            'insult': insult_score,
            'identity_attack': 0.0  # Would need more sophisticated detection
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
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', text):
            matched_patterns.append('repeated_characters')
        
        # Calculate spam score
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

