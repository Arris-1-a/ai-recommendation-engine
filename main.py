#!/usr/bin/env python3
"""
AI Personalized Recommendation Engine
Hybrid recommendation system combining collaborative filtering and content-based approaches.
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('recommendations.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@dataclass
class Rating:
    user_id: str
    item_id: str
    rating: float
    timestamp: int = 0
    interaction_type: str = "explicit"


@dataclass
class RecommendationResult:
    user_id: str
    items: List[Tuple[str, float]]
    strategy: str
    timestamp: str = ""
    total_candidates: int = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class UserBasedCF:
    """User-based collaborative filtering."""

    def __init__(self, similarity_threshold: float = 0.1):
        self.similarity_threshold = similarity_threshold
        self.user_item_matrix: Optional[np.ndarray] = None
        self.user_similarity: Optional[np.ndarray] = None
        self.user_map: Dict[str, int] = {}
        self.reverse_user_map: Dict[int, str] = {}
        self.item_map: Dict[str, int] = {}
        self.reverse_item_map: Dict[int, str] = {}

    def fit(self, ratings: List[Rating], n_users: int, n_items: int) -> None:
        logger.info("Training User-Based CF...")
        for r in ratings:
            if r.user_id not in self.user_map:
                self.user_map[r.user_id] = len(self.user_map)
            if r.item_id not in self.item_map:
                self.item_map[r.item_id] = len(self.item_map)

        self.user_item_matrix = np.zeros((n_users, n_items))
        for r in ratings:
            u_idx = self.user_map[r.user_id]
            i_idx = self.item_map[r.item_id]
            self.user_item_matrix[u_idx][i_idx] = r.rating

        self.user_similarity = cosine_similarity(self.user_item_matrix)
        np.fill_diagonal(self.user_similarity, 0)
        logger.info(f"User-Based CF trained: {n_users} users, {n_items} items")

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  exclude_seen: bool = True) -> List[Tuple[str, float]]:
        if self.user_similarity is None:
            return []

        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return []

        similar_users = np.argsort(-self.user_similarity[user_idx])[:50]
        seen_items = set(
            self.reverse_item_map[i_idx]
            for i_idx in np.nonzero(self.user_item_matrix[user_idx] > 0)[0]
        )

        predicted = defaultdict(float)
        weight_sum = defaultdict(float)

        for sim_idx in similar_users:
            sim_score = self.user_similarity[user_idx][sim_idx]
            if sim_score < self.similarity_threshold:
                continue
            for item_idx, rating in enumerate(self.user_item_matrix[sim_idx]):
                if rating > 0:
                    item_id = self.reverse_item_map.get(item_idx, f"item_{item_idx}")
                    if exclude_seen and item_id in seen_items:
                        continue
                    predicted[item_id] += sim_score * rating
                    weight_sum[item_id] += sim_score

        final_scores = {
            item: score / w for item, (score, w) in
            zip(predicted.keys(), weight_sum.values()) if w > 0
        }
        return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        if self.user_similarity is None:
            return None
        user_idx = self.user_map.get(user_id)
        item_idx = self.item_map.get(item_id)
        if user_idx is None or item_idx is None:
            return None
        sims = self.user_similarity[user_idx]
        ratings = self.user_item_matrix[:, item_idx]
        valid = (ratings > 0) & (sims > self.similarity_threshold)
        if not np.any(valid):
            return None
        return float((sims[valid] * ratings[valid]).sum() / valid.sum())


class ItemBasedCF:
    """Item-based collaborative filtering."""

    def __init__(self):
        self.user_item_matrix: Optional[np.ndarray] = None
        self.item_similarity: Optional[np.ndarray] = None
        self.item_map: Dict[str, int] = {}
        self.reverse_item_map: Dict[int, str] = {}
        self.user_map: Dict[str, int] = {}
        self.rating_dict: Dict[str, List[str]] = defaultdict(list)

    def fit(self, ratings: List[Rating], n_items: int) -> None:
        logger.info("Training Item-Based CF...")
        for r in ratings:
            if r.user_id not in self.user_map:
                self.user_map[r.user_id] = len(self.user_map)
            if r.item_id not in self.item_map:
                self.item_map[r.item_id] = len(self.item_map)
            self.rating_dict[r.user_id].append(r.item_id)

        n_users = len(self.user_map)
        self.user_item_matrix = np.zeros((n_users, n_items))
        for r in ratings:
            u = self.user_map[r.user_id]
            i = self.item_map[r.item_id]
            self.user_item_matrix[u][i] = r.rating

        self.item_similarity = cosine_similarity(self.user_item_matrix.T)
        logger.info(f"Item-Based CF trained: {len(self.item_map)} items")

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  seed_items: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        if self.item_similarity is None:
            return []

        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return []

        user_ratings = self.user_item_matrix[user_idx]
        seen_items = set(np.nonzero(user_ratings > 0)[0])

        if len(seen_items) == 0:
            return []

        predicted = defaultdict(float)
        for seen_idx in seen_items:
            similarities = self.item_similarity[seen_idx]
            for candidate_idx in np.argsort(-similarities):
                if candidate_idx in seen_items:
                    continue
                predicted[candidate_idx] += similarities[candidate_idx]

        for idx in predicted:
            predicted[idx] /= len(seen_items)

        results = sorted(predicted.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        items = [(self.reverse_item_map[i] if i in self.reverse_item_map else f"item_{i}", s)
                 for i, s in results]
        return items

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        if self.item_similarity is None:
            return None
        if item_id not in self.item_map:
            return None
        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return None
        item_idx = self.item_map[item_id]
        user_ratings = self.user_item_matrix[user_idx]
        sims = self.item_similarity[item_idx]
        valid = (user_ratings > 0) & (sims > 0)
        if not np.any(valid):
            return None
        return float((user_ratings[valid] * sims[valid]).sum() / sims[valid].sum())

    def __post_init__(self):
        # Fix: build reverse map after item_map is populated
        for item_id, idx in self.item_map.items():
            self.reverse_item_map[idx] = item_id


class ContentRecommender:
    """Content-based recommender using item feature vectors."""

    def __init__(self):
        self.item_features: Dict[str, np.ndarray] = {}
        self.user_profiles: Dict[str, np.ndarray] = {}

    def add_item(self, item_id: str, features: Dict[str, float]) -> None:
        vec = np.array(list(features.values()), dtype=float)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        self.item_features[item_id] = vec

    def build_profile(self, user_id: str, rated: List[Tuple[str, float]]) -> None:
        vectors = []
        weights = []
        for item_id, rating in rated:
            if item_id in self.item_features:
                vectors.append(self.item_features[item_id])
                weights.append(rating)
        if vectors:
            arr = np.array(vectors)
            w = np.array(weights)
            self.user_profiles[user_id] = (arr.T @ w) / w.sum()
        else:
            dim = len(next(iter(self.item_features.values()))) if self.item_features else 1
            self.user_profiles[user_id] = np.zeros(dim)

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  exclude_ids: Optional[set] = None) -> List[Tuple[str, float]]:
        profile = self.user_profiles.get(user_id)
        if profile is None or len(self.item_features) == 0:
            return []
        exclude = exclude_ids or set()
        scored = []
        for item_id, features in self.item_features.items():
            if item_id in exclude:
                continue
            sim = float(np.dot(profile, features))
            scored.append((item_id, sim))
        return sorted(scored, key=lambda x: x[1], reverse=True)[:n_recommendations]


class HybridRecommender:
    """Hybrid recommender that combines multiple strategies."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {"user_cf": 0.4, "item_cf": 0.4, "content": 0.2}
        self.user_cf = UserBasedCF()
        self.item_cf = ItemBasedCF()
        self.content_rec = ContentRecommender()
        self.ratings_cache: List[Rating] = []

    def train(self, ratings: List[Rating]) -> None:
        logger.info("Training hybrid recommender...")
        users = set(r.user_id for r in ratings)
        items = set(r.item_id for r in ratings)
        self.user_cf.fit(ratings, len(users), len(items))
        self.item_cf.fit(ratings, len(items))
        self.ratings_cache = ratings

        # Build popularity-based content fallback
        item_popularity = defaultdict(int)
        for r in ratings:
            item_popularity[r.item_id] += 1
        max_pop = max(item_popularity.values()) if item_popularity else 1
        for item_id, pop in item_popularity.items():
            self.content_rec.add_item(item_id, {"popularity": pop / max_pop})

        logger.info("Hybrid model trained.")

    def add_item_features(self, item_id: str, features: Dict[str, float]) -> None:
        self.content_rec.add_item(item_id, features)

    def recommend(self, user_id: str, n_recommendations: int = 10) -> RecommendationResult:
        strategies: Dict[str, Dict[str, float]] = {}

        try:
            uc = self.user_cf.recommend(user_id, n_recommendations)
            if uc:
                strategies["user_cf"] = dict(uc)
        except Exception as e:
            logger.warning(f"User-CF failed: {e}")

        try:
            ic = self.item_cf.recommend(user_id, n_recommendations)
            if ic:
                strategies["item_cf"] = dict(ic)
        except Exception as e:
            logger.warning(f"Item-CF failed: {e}")

        try:
            cr = self.content_rec.recommend(user_id, n_recommendations)
            if cr:
                strategies["content"] = dict(cr)
        except Exception as e:
            logger.warning(f"Content rec failed: {e}")

        if not strategies:
            return self._cold_start(user_id, n_recommendations)

        final_scores: Dict[str, float] = defaultdict(float)
        for strat_name, results in strategies.items():
            weight = self.weights.get(strat_name, 0.3)
            max_s = max(results.values()) if results else 1.0
            for item_id, score in results.items():
                normalized = score / max_s if max_s > 0 else 0
                final_scores[item_id] += normalized * weight

        ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        return RecommendationResult(
            user_id=user_id,
            items=ranked,
            strategy="hybrid",
            total_candidates=len(final_scores)
        )

    def _cold_start(self, user_id: str, n: int) -> RecommendationResult:
        popular = defaultdict(int)
        for r in self.ratings_cache:
            popular[r.item_id] += 1
        top = sorted(popular.items(), key=lambda x: x[1], reverse=True)[:n]
        max_pop = max(popular.values()) if popular else 1
        items = [(iid, c / max_pop * 0.8) for iid, c in top]
        if not items:
            items = [(f"default_{i}", 0.1) for i in range(n)]
        return RecommendationResult(
            user_id=user_id,
            items=items,
            strategy="cold_start_popular",
            total_candidates=len(popular)
        )


class RecommendationEngine:
    """Main recommendation engine with unified interface."""

    def __init__(self):
        self.hybrid = HybridRecommender()
        self.is_trained = False
        self.config = {
            "default_n_recommendations": 10,
            "similarity_threshold": 0.1,
        }

    def train(self, ratings_data: List[Dict]) -> None:
        logger.info("Training recommendation engine...")
        ratings = [
            Rating(
                user_id=str(d["user_id"]),
                item_id=str(d["item_id"]),
                rating=float(d.get("rating", 0)),
                timestamp=int(d.get("timestamp", 0)),
                interaction_type=d.get("type", "explicit")
            )
            for d in ratings_data
        ]
        self.hybrid.train(ratings)
        self.is_trained = True
        logger.info("Recommendation engine trained.")

    def recommend(self, user_id: str,
                  n_recommendations: Optional[int] = None,
                  filter_items: Optional[set] = None,
                  context: Optional[Dict] = None) -> RecommendationResult:
        if not self.is_trained:
            return self._fallback(user_id)
        n = n_recommendations or self.config["default_n_recommendations"]
        result = self.hybrid.recommend(user_id, n)

        if context and result.items:
            filtered_items = [(iid, s) for iid, s in result.items
                              if filter_items is None or iid not in filter_items]
            result.items = filtered_items[:n]

        return result

    def add_item_features(self, item_id: str, features: Dict[str, float]) -> None:
        self.hybrid.add_item_features(item_id, features)

    def _fallback(self, user_id: str) -> RecommendationResult:
        return RecommendationResult(
            user_id=user_id,
            items=[],
            strategy="not_trained"
        )

    def evaluate(self, test_data: List[Dict]) -> Dict[str, float]:
        if not self.is_trained or not test_data:
            return {}
        hits = 0
        for record in test_data:
            pred = self.recommend(str(record["user_id"]))
            if pred.items and pred.items[0][0] == str(record["item_id"]):
                hits += 1
        return {"hit_rate_at_1": hits / len(test_data)}


def demo():
    print("=" * 60)
    print("🎯 AI Personalized Recommendation Engine - Demo")
    print("=" * 60)

    sample_data = [
        {"user_id": "u1", "item_id": "movie_1", "rating": 5.0},
        {"user_id": "u1", "item_id": "movie_2", "rating": 4.0},
        {"user_id": "u1", "item_id": "movie_3", "rating": 5.0},
        {"user_id": "u2", "item_id": "movie_1", "rating": 4.0},
        {"user_id": "u2", "item_id": "movie_4", "rating": 5.0},
        {"user_id": "u3", "item_id": "movie_2", "rating": 3.0},
        {"user_id": "u3", "item_id": "movie_3", "rating": 4.0},
        {"user_id": "u3", "item_id": "movie_4", "rating": 5.0},
        {"user_id": "u3", "item_id": "movie_5", "rating": 5.0},
        {"user_id": "u4", "item_id": "movie_5", "rating": 4.0},
        {"user_id": "u4", "item_id": "movie_2", "rating": 5.0},
    ]

    engine = RecommendationEngine()
    engine.train(sample_data)

    print("\n🔮 Recommendations for 'u1' (top 3):")
    result = engine.recommend("u1", n_recommendations=3)
    print(f"   Strategy: {result.strategy}")
    for item_id, score in result.items:
        print(f"      → {item_id}: {score:.3f}")

    print("\n🔮 Recommendations for 'u3' (top 3):")
    result2 = engine.recommend("u3", n_recommendations=3)
    for item_id, score in result2.items:
        print(f"      → {item_id}: {score:.3f}")

    print("\n❄️  Cold-start recommendation for unknown user:")
    result3 = engine.recommend("new_user_999", n_recommendations=3)
    for item_id, score in result3.items:
        print(f"      → {item_id}: {score:.3f}")

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo()
