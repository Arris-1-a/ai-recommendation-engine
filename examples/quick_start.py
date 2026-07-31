"""Quick Start Guide for AI Recommendation Engine"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import RecommendationEngine

def main():
    engine = RecommendationEngine()
    
    print("🎯 AI Recommendation Engine - Quick Start")
    print("=" * 50)
    
    # Training data
    data = [
        {"user_id": "user_1", "item_id": "item_1", "rating": 5.0},
        {"user_id": "user_1", "item_id": "item_2", "rating": 4.0},
        {"user_id": "user_1", "item_id": "item_3", "rating": 5.0},
        {"user_id": "user_2", "item_id": "item_1", "rating": 4.0},
        {"user_id": "user_2", "item_id": "item_4", "rating": 5.0},
        {"user_id": "user_3", "item_id": "item_2", "rating": 3.0},
        {"user_id": "user_3", "item_id": "item_3", "rating": 4.0},
        {"user_id": "user_3", "item_id": "item_4", "rating": 5.0},
    ]
    
    print("\n📊 Training model...")
    engine.train(data)
    print("✅ Model trained")
    
    # Get recommendations
    print("\n🔮 Getting recommendations...")
    result = engine.recommend("user_1", n_recommendations=3)
    
    print(f"\nRecommendations for user_1:")
    print(f"   Strategy: {result.strategy}")
    print(f"   Candidates: {result.total_candidates}")
    for item_id, score in result.items:
        print(f"      → {item_id}: {score:.4f}")
    
    # Evaluate
    print("\n📈 Evaluating model...")
    metrics = engine.evaluate([
        {"user_id": "user_1", "item_id": "item_3", "rating": 5.0},
        {"user_id": "user_3", "item_id": "item_4", "rating": 5.0},
    ])
    print(f"   Hit Rate@1: {metrics['hit_rate_at_1']:.2%}")
    print(f"   MRR: {metrics['mrr']:.4f}")
    
    print("\n" + "=" * 50)
    print("✅ Quick start complete!")

if __name__ == "__main__":
    main()
