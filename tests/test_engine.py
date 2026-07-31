"""Tests for the AI Recommendation Engine."""

import pytest
from main import RecommendationEngine, UserBasedCF, ItemBasedCF, ContentRecommender, Rating


SAMPLE_RATINGS = [
    {"user_id": "u1", "item_id": "i1", "rating": 5.0},
    {"user_id": "u1", "item_id": "i2", "rating": 4.0},
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
    {"user_id": "u2", "item_id": "i4", "rating": 5.0},
    {"user_id": "u3", "item_id": "i2", "rating": 3.0},
    {"user_id": "u3", "item_id": "i3", "rating": 4.0},
    {"user_id": "u3", "item_id": "i4", "rating": 5.0},
    {"user_id": "u3", "item_id": "i5", "rating": 5.0},
    {"user_id": "u4", "item_id": "i5", "rating": 4.0},
    {"user_id": "u4", "item_id": "i2", "rating": 5.0},
]


@pytest.fixture
def engine():
    e = RecommendationEngine()
    e.train(SAMPLE_RATINGS)
    return e


class TestRecommendationEngine:
    def test_train_and_recommend(self, engine):
        assert engine.is_trained
        result = engine.recommend("u1", n_recommendations=3)
        assert result.items
        assert isinstance(result.strategy, str)

    def test_recommend_with_filter(self, engine):
        result = engine.recommend("u1", filter_items={"i1"})
        for item_id, _ in result.items:
            assert item_id != "i1"

    def test_cold_start_user(self, engine):
        result = engine.recommend("unknown_user_xyz", n_recommendations=3)
        assert len(result.items) >= 1
        assert result.strategy == "cold_start_popular"

    def test_evaluate(self, engine):
        test_data = [
            {"user_id": "u1", "item_id": "i3", "rating": 5.0},
            {"user_id": "u3", "item_id": "i5", "rating": 5.0},
        ]
        metrics = engine.evaluate(test_data)
        assert "hit_rate_at_1" in metrics

    def test_context_recommendation(self, engine):
        result = engine.recommend("u1", context={"popularity": 0.5})
        assert result.items


class TestUserBasedCF:
    def test_basic_recommendation(self):
        cf = UserBasedCF(similarity_threshold=0.0)
        ratings = [
            Rating("u1", "i1", 5.0, 1),
            Rating("u1", "i2", 4.0, 2),
            Rating("u2", "i1", 3.0, 3),
            Rating("u2", "i3", 5.0, 4),
        ]
        cf.fit(ratings, 2, 3)
        recs = cf.recommend("u1", n_recommendations=1)
        assert isinstance(recs, list)

    def test_predict(self):
        cf = UserBasedCF(similarity_threshold=0.0)
        ratings = [
            Rating("u1", "i1", 5.0, 1),
            Rating("u1", "i2", 4.0, 2),
            Rating("u2", "i1", 3.0, 3),
        ]
        cf.fit(ratings, 2, 2)
        pred = cf.predict("u1", "i1")
        assert pred is not None


class TestContentRecommender:
    def test_add_and_recommend(self):
        cr = ContentRecommender()
        cr.add_item("item_a", {"genre_action": 0.9, "year": 0.8})
        cr.add_item("item_b", {"genre_drama": 0.7, "year": 0.6})
        cr.build_profile("u1", [("item_a", 5.0)])
        recs = cr.recommend("u1", n_recommendations=1)
        assert len(recs) >= 1
        assert recs[0][0] == "item_b"


class TestDataUtils:
    def test_rating_dataclass(self):
        r = Rating(user_id="u1", item_id="i1", rating=4.5, timestamp=1000)
        assert r.user_id == "u1"
        assert r.interaction_type == "explicit"
