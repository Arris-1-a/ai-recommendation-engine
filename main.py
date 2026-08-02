#!/usr/bin/env python3
"""
AI Personalized Recommendation Engine - Enterprise Platform
Advanced hybrid recommendation system with multiple algorithms
Features: Collaborative Filtering, Content-Based, Matrix Factorization, Deep Learning
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, lil_matrix
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from pathlib import Path
import logging
import time
from datetime import datetime

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "recommendations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== Data Models ====================

@dataclass
class Rating:
    """User-item interaction record."""
    user_id: str
    item_id: str
    rating: float
    timestamp: int = 0
    interaction_type: str = "explicit"  # explicit, implicit, view, click
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'item_id': self.item_id,
            'rating': self.rating,
            'timestamp': self.timestamp,
            'type': self.interaction_type
        }


@dataclass
class RecommendationResult:
    """Single recommendation result for a user."""
    user_id: str
    items: List[Tuple[str, float]]
    strategy: str
    timestamp: str = ""
    total_candidates: int = 0
    explainability: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'recommendations': [{'item_id': iid, 'score': round(s, 4)} for iid, s in self.items],
            'strategy': self.strategy,
            'total_candidates': self.total_candidates,
            'explainability': self.explainability
        }


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for recommendation system."""
    hit_rate_at_1: float = 0.0
    hit_rate_at_5: float = 0.0
    hit_rate_at_10: float = 0.0
    mrr: float = 0.0  # Mean Reciprocal Rank
    precision_at_k: Dict[int, float] = field(default_factory=dict)
    recall_at_k: Dict[int, float] = field(default_factory=dict)
    ndcg_at_k: Dict[int, float] = field(default_factory=dict)
    coverage: float = 0.0
    diversity: float = 0.0
    novelty: float = 0.0
    test_samples: int = 0

    def to_dict(self) -> Dict:
        return {
            'hit_rate_at_1': round(self.hit_rate_at_1, 4),
            'hit_rate_at_5': round(self.hit_rate_at_5, 4),
            'hit_rate_at_10': round(self.hit_rate_at_10, 4),
            'mrr': round(self.mrr, 4),
            'coverage': round(self.coverage, 4),
            'diversity': round(self.diversity, 4),
            'novelty': round(self.novelty, 4),
            'test_samples': self.test_samples
        }


# ==================== Similarity Computation ====================

class SimilarityComputer:
    """Compute various similarity metrics."""

    @staticmethod
    def cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
        """Compute cosine similarity matrix."""
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = matrix / norms
        return np.dot(normalized, normalized.T)

    @staticmethod
    def adjusted_cosine_similarity(ratings: np.ndarray,
                                   user_means: np.ndarray) -> np.ndarray:
        """Adjusted cosine similarity (subtracting user means)."""
        adjusted = ratings - user_means.reshape(-1, 1)
        return SimilarityComputer.cosine_similarity_matrix(adjusted)

    @staticmethod
    def pearson_correlation(ratings: np.ndarray) -> np.ndarray:
        """Compute Pearson correlation matrix."""
        means = np.mean(ratings, axis=1)
        centered = ratings - means.reshape(-1, 1)
        denom = np.linalg.norm(centered, axis=1)
        denom[denom == 0] = 1
        normalized = centered / denom.reshape(-1, 1)
        return np.dot(normalized, normalized.T) / ratings.shape[1]

    @staticmethod
    def jaccard_similarity(binary_matrix: np.ndarray) -> np.ndarray:
        """Compute Jaccard similarity for binary interactions."""
        dot_product = binary_matrix @ binary_matrix.T
        norm_a = np.linalg.norm(binary_matrix, axis=1)
        norm_b = norm_a.reshape(-1, 1)
        intersection = dot_product
        union = norm_a.reshape(-1, 1) + norm_b - dot_product
        union[union == 0] = 1
        return intersection / union


# ==================== Collaborative Filtering ====================

class UserBasedCF:
    """User-based collaborative filtering with multiple similarity methods."""

    def __init__(self, similarity_threshold: float = 0.1,
                 n_neighbors: int = 50,
                 similarity_method: str = "cosine"):
        self.similarity_threshold = similarity_threshold
        self.n_neighbors = n_neighbors
        self.similarity_method = similarity_method
        self.user_item_matrix: Optional[np.ndarray] = None
        self.user_similarity: Optional[np.ndarray] = None
        self.user_map: Dict[str, int] = {}
        self.item_map: Dict[str, int] = {}
        self.user_means: Dict[int, float] = {}
        self._reverse_item_map: Dict[int, str] = {}

    def fit(self, ratings: List[Rating], n_users: int, n_items: int) -> None:
        """Train the model on rating data."""
        logger.info("Training User-Based CF...")
        start_time = time.time()

        # Build mappings
        for r in ratings:
            if r.user_id not in self.user_map:
                self.user_map[r.user_id] = len(self.user_map)
            if r.item_id not in self.item_map:
                self.item_map[r.item_id] = len(self.item_map)

        # Build rating matrix
        self.user_item_matrix = np.zeros((n_users, n_items))
        for r in ratings:
            u_idx = self.user_map[r.user_id]
            i_idx = self.item_map[r.item_id]
            self.user_item_matrix[u_idx][i_idx] = r.rating

        # Compute user means
        valid_rows = self.user_item_matrix.sum(axis=1) > 0
        self.user_means = {}
        for i in range(n_users):
            if valid_rows[i]:
                self.user_means[i] = np.mean(self.user_item_matrix[i][self.user_item_matrix[i] > 0])
            else:
                self.user_means[i] = 0

        # Build reverse map
        self._reverse_item_map = {v: k for k, v in self.item_map.items()}

        # Compute similarity
        if self.similarity_method == "adjusted_cosine":
            self.user_similarity = SimilarityComputer.adjusted_cosine_similarity(
                self.user_item_matrix, np.array([self.user_means.get(i, 0) for i in range(n_users)])
            )
        elif self.similarity_method == "pearson":
            self.user_similarity = SimilarityComputer.pearson_correlation(self.user_item_matrix)
        else:
            self.user_similarity = SimilarityComputer.cosine_similarity_matrix(self.user_item_matrix)

        np.fill_diagonal(self.user_similarity, 0)

        elapsed = time.time() - start_time
        logger.info(f"User-Based CF trained in {elapsed:.2f}s ({n_users} users, {len(self.item_map)} items)")

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  exclude_seen: bool = True) -> List[Tuple[str, float]]:
        """Generate recommendations for a user."""
        if self.user_similarity is None:
            return []

        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return []

        # Get similar users
        similar_users = np.argsort(-self.user_similarity[user_idx])[:self.n_neighbors]

        # Get items user has already seen
        seen_items = set(np.nonzero(self.user_item_matrix[user_idx] > 0)[0])

        # Predict ratings for unseen items
        predicted = defaultdict(float)
        weight_sum = defaultdict(float)

        for sim_idx in similar_users:
            sim_score = self.user_similarity[user_idx][sim_idx]
            if sim_score < self.similarity_threshold:
                continue

            user_ratings = self.user_item_matrix[sim_idx]
            for item_idx, rating in enumerate(user_ratings):
                if rating > 0 and item_idx not in seen_items:
                    item_id = self._idx_to_item_id(item_idx)
                    predicted[item_id] += sim_score * rating
                    weight_sum[item_id] += abs(sim_score)

        # Calculate weighted average
        final_scores = {}
        for item_id, score in predicted.items():
            w = weight_sum[item_id]
            if w > 0:
                final_scores[item_id] = score / w

        # Sort by score
        results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        return [(iid, round(s, 4)) for iid, s in results]

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        """Predict rating for a user-item pair."""
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
        """Convert index to item ID."""
        return self._reverse_item_map.get(idx, f"item_{idx}")


class ItemBasedCF:
    """Item-based collaborative filtering."""

    def __init__(self):
        self.user_item_matrix: Optional[np.ndarray] = None
        self.item_similarity: Optional[np.ndarray] = None
        self.item_map: Dict[str, int] = {}
        self.reverse_item_map: Dict[int, str] = {}
        self.user_map: Dict[str, int] = {}

    def fit(self, ratings: List[Rating], n_items: int) -> None:
        """Train item-based CF model."""
        logger.info("Training Item-Based CF...")
        start_time = time.time()

        # Build mappings
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

        # Compute item similarity
        self.item_similarity = SimilarityComputer.cosine_similarity_matrix(self.user_item_matrix.T)

        elapsed = time.time() - start_time
        logger.info(f"Item-Based CF trained in {elapsed:.2f}s ({len(self.item_map)} items)")

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  seed_items: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        """Generate recommendations using item-based CF."""
        if self.item_similarity is None:
            return []

        user_idx = self.user_map.get(user_id)
        if user_idx is None:
            return []

        # Get items user has rated
        user_ratings = self.user_item_matrix[user_idx]
        rated_items = set(np.nonzero(user_ratings > 0)[0])

        if len(rated_items) == 0:
            return []

        # Aggregate similarities
        predicted = defaultdict(float)
        for rated_idx in rated_items:
            similarities = self.item_similarity[rated_idx]
            for candidate_idx in np.argsort(-similarities):
                if candidate_idx in rated_items:
                    continue
                predicted[candidate_idx] += similarities[candidate_idx]

        # Normalize
        for idx in predicted:
            predicted[idx] /= len(rated_items)

        # Get top items
        results = sorted(predicted.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        items = [(self.reverse_item_map.get(i, f"item_{i}"), round(s, 4)) for i, s in results]
        return items

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        """Predict rating using item-based CF."""
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


# ==================== Matrix Factorization ====================

class MatrixFactorization:
    """Latent factor model using alternating least squares."""

    def __init__(self, n_factors: int = 50, learning_rate: float = 0.01,
                 regularization: float = 0.02, n_epochs: int = 100):
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.n_epochs = n_epochs
        self.user_factors = None
        self.item_factors = None
        self.user_map: Dict[str, int] = {}
        self.item_map: Dict[str, int] = {}

    def fit(self, ratings: List[Rating], n_users: int, n_items: int) -> None:
        """Train matrix factorization model."""
        logger.info(f"Training Matrix Factorization ({self.n_factors} factors)...")
        start_time = time.time()

        # Initialize factors randomly
        np.random.seed(42)
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))

        # Build rating dictionary
        rating_dict = defaultdict(list)
        for r in ratings:
            if r.user_id not in self.user_map:
                self.user_map[r.user_id] = len(self.user_map)
            if r.item_id not in self.item_map:
                self.item_map[r.item_id] = len(self.item_map)
            u_idx = self.user_map[r.user_id]
            i_idx = self.item_map[r.item_id]
            rating_dict[u_idx].append((i_idx, r.rating))

        # ALS training
        for epoch in range(self.n_epochs):
            # Update user factors
            for u in range(n_users):
                if u in rating_dict and rating_dict[u]:
                    item_indices = [r[0] for r in rating_dict[u]]
                    ratings_u = [r[1] for r in rating_dict[u]]
                    I_u = self.item_factors[item_indices]
                    self.user_factors[u] = self._update_factor(
                        I_u, ratings_u, self.user_factors[u]
                    )

            # Update item factors
            for i in range(n_items):
                # Find users who rated this item
                users_i = [u for u, rating_list in rating_dict.items()
                          for idx, r in rating_list if idx == i]
                if users_i:
                    user_vecs = self.user_factors[users_i]
                    ratings_i = [r for u in users_i
                                 for idx, r in rating_dict[u] if idx == i]
                    self.item_factors[i] = self._update_factor(
                        user_vecs, ratings_i, self.item_factors[i]
                    )

            # Compute loss
            if (epoch + 1) % 10 == 0:
                mse = self._compute_mse(ratings)
                logger.info(f"Epoch {epoch+1}/{self.n_epochs}, MSE: {mse:.4f}")

        elapsed = time.time() - start_time
        logger.info(f"Matrix Factorization trained in {elapsed:.2f}s")

    def _update_factor(self, others: np.ndarray, targets: List[float],
                       factor: np.ndarray) -> np.ndarray:
        """Update a factor vector using regularized least squares."""
        A = others.T @ others + self.regularization * np.eye(self.n_factors)
        b = others.T @ np.array(targets)
        return np.linalg.solve(A, b)

    def _compute_mse(self, ratings: List[Rating]) -> float:
        """Compute mean squared error on training data."""
        errors = []
        for r in ratings:
            u_idx = self.user_map.get(r.user_id)
            i_idx = self.item_map.get(r.item_id)
            if u_idx is not None and i_idx is not None:
                pred = np.dot(self.user_factors[u_idx], self.item_factors[i_idx])
                errors.append((pred - r.rating) ** 2)
        return np.mean(errors) if errors else 0.0

    def predict(self, user_id: str, item_id: str) -> Optional[float]:
        """Predict rating using MF model."""
        u_idx = self.user_map.get(user_id)
        i_idx = self.item_map.get(item_id)
        if u_idx is None or i_idx is None:
            return None
        return float(np.dot(self.user_factors[u_idx], self.item_factors[i_idx]))


# ==================== Content-Based Recommender ====================

class ContentRecommender:
    """Content-based recommendation using item features."""

    def __init__(self):
        self.item_features: Dict[str, np.ndarray] = {}
        self.user_profiles: Dict[str, np.ndarray] = {}
        self.feature_names: List[str] = []
        self.item_popularity: Dict[str, int] = defaultdict(int)

    def add_item(self, item_id: str, features: Dict[str, float]) -> None:
        """Add item with feature vector."""
        vec = np.array(list(features.values()), dtype=float)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        self.item_features[item_id] = vec
        if not self.feature_names:
            self.feature_names = list(features.keys())

    def build_profile(self, user_id: str, rated_items: List[Tuple[str, float]]) -> None:
        """Build user profile from rated items."""
        vectors = []
        weights = []
        for item_id, rating in rated_items:
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
                  exclude_ids: Optional[Set[str]] = None) -> List[Tuple[str, float]]:
        """Generate content-based recommendations."""
        profile = self.user_profiles.get(user_id)
        if profile is None or not self.item_features:
            return []

        exclude = exclude_ids or set()
        scored = []

        for item_id, features in self.item_features.items():
            if item_id in exclude:
                continue
            sim = float(np.dot(profile, features))
            scored.append((item_id, round(sim, 4)))

        return sorted(scored, key=lambda x: x[1], reverse=True)[:n_recommendations]

    def add_popularity(self, item_id: str, count: int = 1) -> None:
        """Track item popularity."""
        self.item_popularity[item_id] += count


# ==================== Hybrid Recommender ====================

class HybridRecommender:
    """Hybrid recommender combining multiple strategies."""

    DEFAULT_WEIGHTS = {"user_cf": 0.3, "item_cf": 0.3, "mf": 0.2, "content": 0.2}

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.user_cf = UserBasedCF()
        self.item_cf = ItemBasedCF()
        self.mf = MatrixFactorization()
        self.content_rec = ContentRecommender()
        self.ratings_cache: List[Rating] = []

    def train(self, ratings: List[Rating], n_users: int, n_items: int) -> None:
        """Train all sub-models."""
        logger.info("Training hybrid recommender...")
        start_time = time.time()

        # Train collaborative filtering models
        self.user_cf.fit(ratings, n_users, n_items)
        self.item_cf.fit(ratings, n_items)
        self.mf.fit(ratings, n_users, n_items)

        # Build content features from ratings
        item_stats = defaultdict(lambda: {'count': 0, 'ratings': []})
        for r in ratings:
            item_stats[r.item_id]['count'] += 1
            item_stats[r.item_id]['ratings'].append(r.rating)

        max_count = max(s['count'] for s in item_stats.values()) if item_stats else 1
        for item_id, stats in item_stats.items():
            avg_rating = np.mean(stats['ratings'])
            pop_norm = stats['count'] / max_count
            self.content_rec.add_item(item_id, {
                'popularity': round(pop_norm, 3),
                'avg_rating': round(avg_rating / 5.0, 3)
            })
            self.content_rec.add_popularity(item_id, stats['count'])

        self.ratings_cache = ratings
        elapsed = time.time() - start_time
        logger.info(f"Hybrid model trained in {elapsed:.2f}s")

    def add_item_features(self, item_id: str, features: Dict[str, float]) -> None:
        """Add custom item features."""
        self.content_rec.add_item(item_id, features)

    def build_user_profile(self, user_id: str) -> None:
        """Build user profile from history."""
        user_ratings = [(r.item_id, r.rating) for r in self.ratings_cache
                       if r.user_id == user_id]
        self.content_rec.build_profile(user_id, user_ratings)

    def recommend(self, user_id: str, n_recommendations: int = 10,
                  exclude_seen: bool = True) -> RecommendationResult:
        """Generate hybrid recommendations."""
        # Collect predictions from each model
        strategies: Dict[str, Dict[str, float]] = {}

        try:
            uc_results = self.user_cf.recommend(user_id, n_recommendations)
            if uc_results:
                strategies["user_cf"] = dict(uc_results)
        except Exception as e:
            logger.warning(f"User-CF failed: {e}")

        try:
            ic_results = self.item_cf.recommend(user_id, n_recommendations)
            if ic_results:
                strategies["item_cf"] = dict(ic_results)
        except Exception as e:
            logger.warning(f"Item-CF failed: {e}")

        try:
            mf_results = self._mf_recommend(user_id, n_recommendations)
            if mf_results:
                strategies["mf"] = dict(mf_results)
        except Exception as e:
            logger.warning(f"MF failed: {e}")

        try:
            cr_results = self.content_rec.recommend(user_id, n_recommendations)
            if cr_results:
                strategies["content"] = dict(cr_results)
        except Exception as e:
            logger.warning(f"Content rec failed: {e}")

        # Handle cold start
        if not strategies:
            return self._cold_start_recommend(user_id, n_recommendations)

        # Weighted fusion
        final_scores: Dict[str, float] = defaultdict(float)
        strategy_weights: Dict[str, float] = defaultdict(float)

        for strat_name, results in strategies.items():
            weight = self.weights.get(strat_name, 0.25)
            max_score = max(results.values()) if results else 1.0
            for item_id, score in results.items():
                normalized = score / max_score if max_score > 0 else 0
                final_scores[item_id] += normalized * weight
                strategy_weights[item_id] += weight

        # Normalize by total weight
        for item_id in final_scores:
            if strategy_weights[item_id] > 0:
                final_scores[item_id] /= strategy_weights[item_id]

        # Sort and select top items
        ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]

        # Build explainability
        explainability = {
            'strategies_used': list(strategies.keys()),
            'final_scores': {iid: round(s, 4) for iid, s in ranked[:5]}
        }

        return RecommendationResult(
            user_id=user_id,
            items=[(iid, round(s, 4)) for iid, s in ranked],
            strategy="hybrid",
            total_candidates=len(final_scores),
            explainability=explainability
        )

    def _mf_recommend(self, user_id: str, n: int) -> List[Tuple[str, float]]:
        """Get MF recommendations for a user."""
        results = []
        for item_id in self.mf.item_map.keys():
            pred = self.mf.predict(user_id, item_id)
            if pred is not None:
                results.append((item_id, pred))
        return sorted(results, key=lambda x: x[1], reverse=True)[:n]

    def _cold_start_recommend(self, user_id: str, n: int) -> RecommendationResult:
        """Cold start recommendations based on popularity."""
        popular = defaultdict(int)
        for r in self.ratings_cache:
            popular[r.item_id] += 1

        top_items = sorted(popular.items(), key=lambda x: x[1], reverse=True)[:n]
        max_pop = max(popular.values()) if popular else 1
        items = [(iid, round(c / max_pop * 0.8, 4)) for iid, c in top_items]

        if not items:
            items = [(f"default_{i}", 0.1) for i in range(n)]

        return RecommendationResult(
            user_id=user_id,
            items=items,
            strategy="cold_start_popular",
            total_candidates=len(popular)
        )


# ==================== Evaluation ====================

class RecommendationEvaluator:
    """Evaluate recommendation system performance."""

    def evaluate(self, engine: 'RecommendationEngine',
                 test_data: List[Dict],
                 k_values: List[int] = None) -> EvaluationMetrics:
        """Evaluate recommendation quality."""
        if k_values is None:
            k_values = [1, 5, 10]

        metrics = EvaluationMetrics(test_samples=len(test_data))
        all_recommended_items = set()
        relevant_items_per_user = {}

        for record in test_data:
            user_id = str(record["user_id"])
            true_item = str(record["item_id"])

            # Get recommendations
            result = engine.recommend(user_id, n_recommendations=max(k_values))
            recommended_items = [iid for iid, _ in result.items]

            # Track coverage
            all_recommended_items.update(recommended_items)

            # Track relevant items
            if user_id not in relevant_items_per_user:
                relevant_items_per_user[user_id] = set()
            relevant_items_per_user[user_id].add(true_item)

            # Hit rate@K
            for k in k_values:
                top_k = recommended_items[:k]
                if true_item in top_k:
                    if k == 1:
                        metrics.hit_rate_at_1 += 1
                    elif k == 5:
                        metrics.hit_rate_at_5 += 1
                    elif k == 10:
                        metrics.hit_rate_at_10 += 1

            # MRR
            for rank, (iid, _) in enumerate(recommended_items, 1):
                if iid == true_item:
                    metrics.mrr += 1.0 / rank
                    break

        # Calculate averages
        n = len(test_data)
        metrics.hit_rate_at_1 /= n
        metrics.hit_rate_at_5 /= n
        metrics.hit_rate_at_10 /= n
        metrics.mrr /= n

        # Coverage
        all_items = set()
        for r in engine.hybrid.ratings_cache:
            all_items.add(r.item_id)
        metrics.coverage = len(all_recommended_items) / len(all_items) if all_items else 0

        return metrics


# ==================== Main Engine ====================

class RecommendationEngine:
    """Main recommendation engine with unified interface."""

    def __init__(self):
        self.hybrid = HybridRecommender()
        self.is_trained = False
        self.config = {
            "default_n_recommendations": 10,
            "similarity_threshold": 0.1,
        }
        self.evaluator = RecommendationEvaluator()

    def train(self, ratings_data: List[Dict]) -> None:
        """Train the recommendation engine."""
        logger.info("Training recommendation engine...")
        start_time = time.time()

        # Convert to Rating objects
        ratings = []
        for d in ratings_data:
            ratings.append(Rating(
                user_id=str(d["user_id"]),
                item_id=str(d["item_id"]),
                rating=float(d.get("rating", 0)),
                timestamp=int(d.get("timestamp", 0)),
                interaction_type=d.get("type", "explicit")
            ))

        # Count unique users and items
        users = set(r.user_id for r in ratings)
        items = set(r.item_id for r in ratings)

        # Train hybrid model
        self.hybrid.train(ratings, len(users), len(items))
        self.is_trained = True

        elapsed = time.time() - start_time
        logger.info(f"Recommendation engine trained in {elapsed:.2f}s "
                   f"({len(users)} users, {len(items)} items)")

    def recommend(self, user_id: str,
                  n_recommendations: Optional[int] = None,
                  filter_items: Optional[Set[str]] = None,
                  context: Optional[Dict] = None) -> RecommendationResult:
        """Generate recommendations for a user."""
        if not self.is_trained:
            return RecommendationResult(user_id=user_id, items=[], strategy="not_trained")

        n = n_recommendations or self.config["default_n_recommendations"]
        result = self.hybrid.recommend(user_id, n, exclude_seen=bool(filter_items))

        # Apply filters
        if filter_items:
            result.items = [(iid, s) for iid, s in result.items if iid not in filter_items]

        # Apply context boosts
        if context:
            boosted_items = []
            for iid, s in result.items:
                bonus = sum(context.get(k, 0) * v for k, v in {
                    "popularity_boost": 0.1,
                    "recency_boost": 0.05,
                    "trending_boost": 0.08
                }.items())
                boosted_items.append((iid, round(s + bonus, 4)))
            result.items = boosted_items

        return result

    def add_item_features(self, item_id: str, features: Dict[str, float]) -> None:
        """Add custom features for an item."""
        self.hybrid.add_item_features(item_id, features)

    def build_user_profile(self, user_id: str) -> None:
        """Build personalized user profile."""
        self.hybrid.build_user_profile(user_id)

    def evaluate(self, test_data: List[Dict], k_values: List[int] = None) -> EvaluationMetrics:
        """Evaluate the recommendation system."""
        return self.evaluator.evaluate(self, test_data, k_values)

    def get_statistics(self) -> Dict:
        """Get engine statistics."""
        return {
            'is_trained': self.is_trained,
            'ratings_count': len(self.hybrid.ratings_cache),
            'strategies': list(self.hybrid.weights.keys()),
            'weights': self.hybrid.weights
        }


# ==================== Demo Function ====================

def demo():
    """Run demonstration of the recommendation system."""
    print("=" * 70)
    print("🎯 AI Personalized Recommendation Engine - Enterprise Platform")
    print("=" * 70)

    # Sample data
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
        {"user_id": "u4", "item_id": "movie_1", "rating": 3.0},
    ]

    engine = RecommendationEngine()
    engine.train(sample_data)

    print("\n📊 Evaluation Metrics:")
    metrics = engine.evaluate([
        {"user_id": "u1", "item_id": "movie_3", "rating": 5.0},
        {"user_id": "u3", "item_id": "movie_5", "rating": 5.0},
        {"user_id": "u2", "item_id": "movie_1", "rating": 4.0},
        {"user_id": "u4", "item_id": "movie_2", "rating": 5.0},
    ])
    metrics_dict = metrics.to_dict()
    for k, v in metrics_dict.items():
        if isinstance(v, float):
            print(f"   {k}: {v:.4f}")
        else:
            print(f"   {k}: {v}")

    print("\n🔮 Recommendations for 'u1' (top 3):")
    result = engine.recommend("u1", n_recommendations=3)
    print(f"   Strategy: {result.strategy}")
    print(f"   Candidates: {result.total_candidates}")
    for item_id, score in result.items:
        print(f"      → {item_id}: {score:.4f}")

    print("\n🔮 Recommendations for 'u3' (top 3):")
    result2 = engine.recommend("u3", n_recommendations=3)
    for item_id, score in result2.items:
        print(f"      → {item_id}: {score:.4f}")

    print("\n❄️  Cold-start for new user:")
    result3 = engine.recommend("new_user_999", n_recommendations=3)
    for item_id, score in result3.items:
        print(f"      → {item_id}: {score:.4f}")

    print("\n✅ Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo()


class ModelCheckpoint:
    """Save and load model checkpoints."""
    
    def __init__(self, save_dir: str = "checkpoints"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, engine: RecommendationEngine, epoch: int, metrics: Dict) -> str:
        """Save model checkpoint."""
        filename = f"checkpoint_epoch_{epoch}.pth"
        filepath = self.save_dir / filename
        
        checkpoint = {
            'epoch': epoch,
            'model_state': engine.hybrid.state_dict() if hasattr(engine.hybrid, 'state_dict') else {},
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        torch.save(checkpoint, filepath)
        logger.info(f"Checkpoint saved: {filepath}")
        return str(filepath)
    
    def load(self, filepath: str) -> Dict:
        """Load model checkpoint."""
        checkpoint = torch.load(filepath, map_location='cpu')
        logger.info(f"Checkpoint loaded: {filepath}")
        return checkpoint


class ModelProfiler:
    """Profile model performance."""
    
    def __init__(self, engine: RecommendationEngine):
        self.engine = engine
        self.timings: Dict[str, List[float]] = defaultdict(list)
    
    def profile_recommend(self, user_id: str, runs: int = 100) -> Dict:
        """Profile recommendation time."""
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            self.engine.recommend(user_id)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        
        return {
            'user_id': user_id,
            'runs': runs,
            'avg_ms': sum(times) / len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'p50_ms': sorted(times)[len(times) // 2],
            'p95_ms': sorted(times)[int(len(times) * 0.95)]
        }
    
    def profile_train(self, data_size: int) -> Dict:
        """Profile training time."""
        # Generate random data
        import random
        data = []
        for i in range(data_size):
            data.append({
                'user_id': f'u{random.randint(0, 100)}',
                'item_id': f'i{random.randint(0, 50)}',
                'rating': round(random.uniform(1, 5), 1)
            })
        
        start = time.perf_counter()
        self.engine.train(data)
        elapsed = time.perf_counter() - start
        
        return {
            'data_size': data_size,
            'training_time_ms': elapsed * 1000
        }


class DataExporter:
    """Export processed data to various formats."""
    
    def __init__(self, processor: DocumentProcessor):
        self.processor = processor
    
    def export_json(self, output_path: str) -> str:
        """Export results to JSON."""
        data = [r.to_dict() for r in self.processor.results]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_path
    
    def export_csv(self, output_path: str) -> str:
        """Export results to CSV."""
        if not self.processor.results:
            return ""
        
        import csv
        fieldnames = ['filename', 'doc_type', 'summary', 'entities', 'keywords']
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.processor.results:
                writer.writerow({
                    'filename': r.filename,
                    'doc_type': r.doc_type,
                    'summary': r.summary[:200],
                    'entities': '; '.join([e.text for e in r.entities]),
                    'keywords': '; '.join([k for k, _ in r.keywords[:10]])
                })
        return output_path
    
    def export_markdown(self, output_path: str) -> str:
        """Export results to Markdown."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Document Processing Report\n\n")
            for r in self.processor.results:
                f.write(f"## {r.filename}\n\n")
                f.write(f"**Type:** {r.doc_type}\n\n")
                f.write(f"**Words:** {r.metadata.word_count}\n\n")
                f.write(f"**Summary:**\n\n{r.summary}\n\n")
                f.write(f"**Entities:**\n\n")
                for e in r.entities[:10]:
                    f.write(f"- [{e.type}] {e.text}\n")
                f.write("\n---\n\n")
        return output_path
