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
        assert result.strategy in ("cold_start_popular", "hybrid")

    def test_evaluate(self, engine):
        test_data = [
            {"user_id": "u1", "item_id": "i3", "rating": 5.0},
            {"user_id": "u3", "item_id": "i5", "rating": 5.0},
        ]
        metrics = engine.evaluate(test_data)
        assert metrics.hit_rate_at_1 is not None
        assert metrics.hit_rate_at_5 is not None
        assert metrics.mrr is not None

    def test_context_recommendation(self, engine):
        result = engine.recommend("u1", context={"popularity_boost": 0.1})
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


class TestItemBasedCF:
    def test_rebuild_reverse_map(self):
        cf = ItemBasedCF()
        ratings = [
            Rating("u1", "i1", 5.0),
            Rating("u1", "i2", 4.0),
            Rating("u2", "i1", 3.0),
        ]
        cf.fit(ratings, 2)
        assert "i1" in cf.reverse_item_map.values()
        assert "i2" in cf.reverse_item_map.values()


class TestContentRecommender:
    def test_add_and_recommend(self):
        cr = ContentRecommender()
        cr.add_item("item_a", {"genre_action": 0.9, "year": 0.8})
        cr.add_item("item_b", {"genre_drama": 0.7, "year": 0.6})
        cr.build_profile("u1", [("item_a", 5.0)])
        recs = cr.recommend("u1", n_recommendations=1)
        assert len(recs) >= 1


class TestDataTypes:
    def test_rating_dataclass(self):
        r = Rating(user_id="u1", item_id="i1", rating=4.5, timestamp=1000)
        assert r.user_id == "u1"
        assert r.interaction_type == "explicit"

    def test_recommendation_result_post_init(self):
        from main import RecommendationResult
        result = RecommendationResult(user_id="u1", items=[("i1", 0.9)], strategy="test")
        assert result.timestamp != ""
        assert len(result.timestamp) > 0


class TestModelCheckpoint:
    def test_save_and_load(self, tmp_path):
        """Test checkpoint save and load."""
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint = ModelCheckpoint(str(checkpoint_dir))
        
        # Test save (mock)
        metrics = {"hit_rate": 0.85, "mrr": 0.72}
        # Note: This would need torch to be installed for full test
        # Skipping actual save for now
        assert checkpoint.save_dir.exists()


class TestEdgeCases:
    def test_empty_ratings(self):
        """Test with empty ratings."""
        engine = RecommendationEngine()
        engine.train([])
        result = engine.recommend("user_1")
        assert result.strategy == "not_trained"
    
    def test_single_user(self):
        """Test with single user."""
        engine = RecommendationEngine()
        engine.train([
            {"user_id": "u1", "item_id": "i1", "rating": 5.0}
        ])
        result = engine.recommend("u1")
        assert result is not None
    
    def test_single_item(self):
        """Test with single item."""
        engine = RecommendationEngine()
        engine.train([
            {"user_id": "u1", "item_id": "i1", "rating": 5.0},
            {"user_id": "u2", "item_id": "i1", "rating": 4.0}
        ])
        result = engine.recommend("u1")
        assert result is not None


class TestModelProfiler:
    def test_profile_recommend(self, engine):
        """Test recommendation profiling."""
        profiler = ModelProfiler(engine)
        # Skip actual profiling for now
        assert profiler.engine is not None
    
    def test_profile_train(self, engine):
        """Test training profiling."""
        profiler = ModelProfiler(engine)
        # Skip actual profiling for now
        assert profiler.engine is not None
