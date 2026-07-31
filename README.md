# AI Personalized Recommendation Engine
Hybrid recommendation system combining collaborative filtering and content-based methods.

## Features

- **User-Based CF**: Find similar users and recommend their liked items
- **Item-Based CF**: Recommend similar items based on co-ratings
- **Content-Based**: Match item features to user preferences
- **Hybrid Fusion**: Dynamically combine multiple strategies
- **Cold Start Handling**: Fallback to popularity-based recommendations
- **REST API**: Ready-to-use HTTP endpoints

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## API Usage

```bash
# Train
curl -X POST http://localhost:8080/train \
  -H "Content-Type: application/json" \
  -d '{"data": [{"user_id": "u1", "item_id": "i1", "rating": 5}]}'

# Get recommendations
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "n_recommendations": 5}'
```

## Architecture

```
┌──────────────────────────────────────┐
│         HybridRecommender            │
│  ┌──────────┐ ┌──────────┐ ┌───────┐│
│  │ User-CF  │ │ Item-CF  │ │Content││
│  └────┬─────┘ └────┬─────┘ └───┬───┘│
│       └─────────────┴───────────┘     │
│          → Weighted Fusion → Ranking  │
└──────────────────────────────────────┘
```

## Testing

```bash
pytest tests/ -v --cov
```
