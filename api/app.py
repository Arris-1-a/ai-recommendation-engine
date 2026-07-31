"""FastAPI service for the Recommendation Engine."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import time

from main import RecommendationEngine

app = FastAPI(title="AI Recommendation Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RecommendationEngine()


class TrainRequest(BaseModel):
    data: List[Dict] = Field(..., description="Training data with user_id, item_id, rating")
    user_column: str = "user_id"
    item_column: str = "item_id"
    rating_column: str = "rating"


class RecommendRequest(BaseModel):
    user_id: str
    n_recommendations: int = Field(10, ge=1, le=100)
    filter_items: Optional[List[str]] = None
    context: Optional[Dict[str, float]] = None


class RecommendResponse(BaseModel):
    user_id: str
    items: List[Dict]
    strategy: str
    timestamp: str
    request_time_ms: int


@app.post("/train")
async def train(request: TrainRequest):
    try:
        engine.train(request.data)
        return {"status": "success", "message": "Model trained"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    start = time.time()
    filter_set = set(request.filter_items) if request.filter_items else None
    result = engine.recommend(
        request.user_id,
        n_recommendations=request.n_recommendations,
        filter_items=filter_set,
        context=request.context
    )
    elapsed_ms = int((time.time() - start) * 1000)
    return RecommendResponse(
        user_id=request.user_id,
        items=[{"item_id": iid, "score": round(score, 4)} for iid, score in result.items],
        strategy=result.strategy,
        timestamp=result.timestamp,
        request_time_ms=elapsed_ms
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "trained": engine.is_trained}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
