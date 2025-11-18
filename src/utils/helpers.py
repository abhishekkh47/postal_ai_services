from typing import List, Any
import numpy as np


def normalize_scores(scores: List[float]) -> List[float]:
    """
    Normalize scores to 0-1 range
    
    Args:
        scores: List of scores
        
    Returns:
        Normalized scores
    """
    if not scores:
        return []
    
    scores_array = np.array(scores)
    min_score = scores_array.min()
    max_score = scores_array.max()
    
    if max_score == min_score:
        return [1.0] * len(scores)
    
    normalized = (scores_array - min_score) / (max_score - min_score)
    return normalized.tolist()


def deduplicate_list(items: List[Any]) -> List[Any]:
    """
    Remove duplicates while preserving order
    
    Args:
        items: List with potential duplicates
        
    Returns:
        List without duplicates
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def merge_recommendations(
    recommendations1: List[tuple],
    recommendations2: List[tuple],
    weight1: float = 0.5,
    weight2: float = 0.5
) -> List[tuple]:
    """
    Merge two lists of recommendations with weights
    
    Args:
        recommendations1: List of (id, score) tuples
        recommendations2: List of (id, score) tuples
        weight1: Weight for first recommendations
        weight2: Weight for second recommendations
        
    Returns:
        Merged and sorted list of (id, score) tuples
    """
    score_map = {}
    
    for item_id, score in recommendations1:
        score_map[item_id] = score_map.get(item_id, 0) + (score * weight1)
    
    for item_id, score in recommendations2:
        score_map[item_id] = score_map.get(item_id, 0) + (score * weight2)
    
    # Sort by score
    merged = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    return merged

