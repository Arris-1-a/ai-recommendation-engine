#!/usr/bin/env python3
"""
AI Personalized Recommendation Engine
Hybrid recommendation system combining collaborative filtering and content-based approaches.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
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
    """User-based collaborative filtering with adjusted cosine similarity."""

    def __init__(self, similarity_threshold: float = 0.1):
        self.similarity_threshold = similarity_threshold
        self.user_item_matrix: Optional[np.ndarray] = None
        self.user_similarity: Optional[np.ndarray] = None
        self.user_map: Dict[str, int] = {}
        self.item_map: Dict[str, int] = {}
        self.mean_ratings: Dict[int, float] = {}

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

        # Compute mean ratings per user for adjustment
        user_means = np.nanmean(self.user_item_matrix, axis=1)
        user_means = np.where(np.isnan(user_means), 0, user_means)
        self.mean_ratings = {i: float(m) for i, m in enumerate(user_means)}

        # Adjusted cosine similarity
        adjusted = self.user_item_matrix - np.array([self.mean_ratings.get(i, 0) for i in range(n_users)]).reshape(-1, 1)
        self.user_similarity = self._cosine_similarity_matrix(adjusted)
        np.fill_diagonal(self.user_similarity, 0)
        logger.info(f"User-Based CF trained: {n_users} users, {len(self.item_map)} items")

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  exclude_seen: bool = True) -> List[Tuple[str, float]]:
        if self.user_similarity is None:
            return []

        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return []

        similar_users = np.argsort(-self.user_similarity[user_idx])[:100]
        user_ratings = self.user_item_matrix[user_idx]
        seen_items = set(np.nonzero(user_ratings > 0)[0])

        predicted = defaultdict(float)
        weight_sum = defaultdict(float)

        for sim_idx in similar_users:
            sim_score = self.user_similarity[user_idx][sim_idx]
            if sim_score < self.similarity_threshold:
                continue
            for item_idx, rating in enumerate(self.user_item_matrix[sim_idx]):
                if rating > 0 and item_idx not in seen_items:
                    item_id = self._idx_to_item_id(item_idx)
                    predicted[item_id] += sim_score * rating
                    weight_sum[item_id] += abs(sim_score)

        final_scores = {}
        for idx, score in predicted.items():
            w = weight_sum[idx]
            if w > 0:
                final_scores[idx] = score / w

        results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        return [(iid, round(s, 4)) for iid, s in results]

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        if self.user_similarity is None or item_id not in self.item_map:
            return None
        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return None
        item_idx = self.item_map[item_id]
        sims = self.user_similarity[user_idx]
        ratings = self.user_item_matrix[:, item_idx]
        valid = (ratings > 0) & (sims > self.similarity_threshold)
        if not np.any(valid):
            return None
        return float((sims[valid] * ratings[valid]).sum() / valid.sum())

    def _idx_to_item_id(self, idx: int) -> str:
        for k, v in self.item_map.items():
            if v == idx:
                return k
        return f"item_{idx}"

    @staticmethod
    def _cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = matrix / norms
        return np.dot(normalized, normalized.T)


class ItemBasedCF:
    """Item-based collaborative filtering."""

    def __init__(self):
        self.user_item_matrix: Optional[np.ndarray] = None
        self.item_similarity: Optional[np.ndarray] = None
        self.item_map: Dict[str, int] = {}
        self.reverse_item_map: Dict[int, str] = {}
        self.user_map: Dict[str, int] = {}

    def fit(self, ratings: List[Rating], n_items: int) -> None:
        logger.info("Training Item-Based CF...")
        for r in ratings:
            if r.user_id not in self.user_map:
                self.user_map[r.user_id] = len(self.user_map)
            if r.item_id not in self.item_map:
                self.item_map[r.item_id] = len(self.item_map)

        n_users = len(self.user_map)
        self.user_item_matrix = np.zeros((n_users, n_items))
        for r in ratings:
            u = self.user_map[r.user_id]
            i = self.item_map[r.item_id]
            self.user_item_matrix[u][i] = r.rating

        # Build reverse map
        self.reverse_item_map = {v: k for k, v in self.item_map.items()}

        self.item_similarity = self._cosine_similarity_matrix(self.user_item_matrix.T)
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
        items = [(self.reverse_item_map.get(i, f"item_{i}"), round(s, 4)) for i, s in results]
        return items

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        if self.item_similarity is None or item_id not in self.item_map:
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

    @staticmethod
    def _cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = matrix / norms
        return np.dot(normalized, normalized.T)


class ContentRecommender:
    """Content-based recommender using item feature vectors."""

    def __init__(self):
        self.item_features: Dict[str, np.ndarray] = {}
        self.user_profiles: Dict[str, np.ndarray] = {}
        self.feature_names: List[str] = []

    def add_item(self, item_id: str, features: Dict[str, float]) -> None:
        vec = np.array(list(features.values()), dtype=float)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        self.item_features[item_id] = vec
        if not self.feature_names:
            self.feature_names = list(features.keys())

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
            scored.append((item_id, round(sim, 4)))
        return sorted(scored, key=lambda x: x[1], reverse=True)[:n_recommendations]


class HybridRecommender:
    """Hybrid recommender combining multiple strategies."""

    DEFAULT_WEIGHTS = {"user_cf": 0.35, "item_cf": 0.35, "content": 0.30}

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
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

        # Build content features from rating patterns
        item_popularity = defaultdict(int)
        item_avg_rating = defaultdict(list)
        for r in ratings:
            item_popularity[r.item_id] += 1
            item_avg_rating[r.item_id].append(r.rating)

        max_pop = max(item_popularity.values()) if item_popularity else 1
        for item_id in items:
            pop_norm = item_popularity[item_id] / max_pop
            avg_r = np.mean(item_avg_rating[item_id]) if item_avg_rating[item_id] else 0
            self.content_rec.add_item(item_id, {
                "popularity": round(pop_norm, 3),
                "avg_rating": round(avg_r / 5.0, 3)
            })

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

        # Weighted fusion
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
            items=[(iid, round(s, 4)) for iid, s in ranked],
            strategy="hybrid",
            total_candidates=len(final_scores)
        )

    def _cold_start(self, user_id: str, n: int) -> RecommendationResult:
        popular = defaultdict(int)
        for r in self.ratings_cache:
            popular[r.item_id] += 1
        top = sorted(popular.items(), key=lambda x: x[1], reverse=True)[:n]
        max_pop = max(popular.values()) if popular else 1
        items = [(iid, round(c / max_pop * 0.8, 4)) for iid, c in top]
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
        self.config = {"default_n_recommendations": 10, "similarity_threshold": 0.1}

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
            return RecommendationResult(user_id=user_id, items=[], strategy="not_trained")

        n = n_recommendations or self.config["default_n_recommendations"]
        result = self.hybrid.recommend(user_id, n)

        if filter_items:
            result.items = [(iid, s) for iid, s in result.items if iid not in filter_items]

        if context:
            new_items = []
            for iid, s in result.items:
                bonus = sum(context.get(k, 0) * v for k, v in {
                    "popularity_boost": 0.1, "recency_boost": 0.05
                }.items())
                new_items.append((iid, round(s + bonus, 4)))
            result.items = new_items

        return result

    def add_item_features(self, item_id: str, features: Dict[str, float]) -> None:
        self.hybrid.add_item_features(item_id, features)

    def get_similarity_matrix(self, user_ids: List[str]) -> Optional[np.ndarray]:
        if not self.is_trained:
            return None
        return self.hybrid.user_cf.user_similarity

    def evaluate(self, test_data: List[Dict], metric: str = "hit_rate") -> Dict[str, float]:
        if not self.is_trained or not test_data:
            return {}

        hits_at_1 = 0
        hits_at_5 = 0
        mrr_sum = 0.0

        for record in test_data:
            pred = self.recommend(str(record["user_id"]), n_recommendations=5)
            true_item = str(record["item_id"])
            if pred.items:
                if pred.items[0][0] == true_item:
                    hits_at_1 += 1
                if true_item in [iid for iid, _ in pred.items]:
                    hits_at_5 += 1
                # MRR
                for rank, (iid, _) in enumerate(pred.items, 1):
                    if iid == true_item:
                        mrr_sum += 1.0 / rank
                        break

        n = len(test_data)
        return {
            "hit_rate_at_1": round(hits_at_1 / n, 4),
            "hit_rate_at_5": round(hits_at_5 / n, 4),
            "mrr": round(mrr_sum / n, 4),
            "test_samples": n
        }


def demo():
    print("=" * 60)
    print("AI Personalized Recommendation Engine - Demo")
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

    print("\nEvaluation on held-out data:")
    metrics = engine.evaluate([
        {"user_id": "u1", "item_id": "movie_3", "rating": 5.0},
        {"user_id": "u3", "item_id": "movie_5", "rating": 5.0},
        {"user_id": "u2", "item_id": "movie_1", "rating": 4.0},
    ])
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print("\nRecommendations for 'u1' (top 3):")
    result = engine.recommend("u1", n_recommendations=3)
    print(f"  Strategy: {result.strategy} | Candidates: {result.total_candidates}")
    for item_id, score in result.items:
        print(f"     -> {item_id}: {score:.4f}")

    print("\nRecommendations for 'u3' (top 3):")
    result2 = engine.recommend("u3", n_recommendations=3)
    for item_id, score in result2.items:
        print(f"     -> {item_id}: {score:.4f}")

    print("\nCold-start recommendation for unknown user:")
    result3 = engine.recommend("new_user_999", n_recommendations=3)
    for item_id, score in result3.items:
        print(f"     -> {item_id}: {score:.4f}")

    print("\nDemo complete!")


if __name__ == "__main__":
    demo()
