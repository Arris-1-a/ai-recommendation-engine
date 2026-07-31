# Example usage and demo scripts for all AI projects

## Quick Start Examples

### 1. Document Processor

```python
from main import DocumentProcessor
import asyncio

processor = DocumentProcessor()

# Process a file
result = processor.process_file("document.txt")
print(f"Summary: {result.summary[:200]}...")
print(f"Entities: {len(result.entities)}")
print(f"Keywords: {[k for k, _ in result.keywords[:10]]}")

# Process directory
results = asyncio.run(processor.process_directory("./documents"))
processor.save_results("output.json")
```

### 2. Image Recognition

```python
from main import ImageRecognizer

recognizer = ImageRecognizer(conf_threshold=0.5)

# Detect objects
results = recognizer.detect_objects("photo.jpg")
for det in results:
    print(f"{det.class_name}: {det.confidence:.2%}")

# Classify image
classes = recognizer.classify_image("photo.jpg", top_k=5)
for cls, prob in classes:
    print(f"{cls}: {prob:.2%}")

# Draw annotations
recognizer.draw_detections("photo.jpg", "output.jpg")
```

### 3. QA System

```python
from main import QASystem
import asyncio

qa = QASystem()

# Add documents
qa.add_documents([
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks."
])

# Ask questions
result = asyncio.run(qa.ask("What is machine learning?"))
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence:.2%}")

# Multi-turn conversation
conv_id = qa.conversation_manager.create()
r1 = asyncio.run(qa.ask("What is AI?", conv_id))
r2 = asyncio.run(qa.ask("How does it work?", conv_id))
```

### 4. Recommendation Engine

```python
from main import RecommendationEngine

engine = RecommendationEngine()

# Train
data = [
    {"user_id": "u1", "item_id": "i1", "rating": 5.0},
    {"user_id": "u1", "item_id": "i2", "rating": 4.0},
    {"user_id": "u2", "item_id": "i1", "rating": 3.0},
]
engine.train(data)

# Get recommendations
result = engine.recommend("u1", n_recommendations=5)
for item_id, score in result.items:
    print(f"{item_id}: {score:.4f}")

# Evaluate
metrics = engine.evaluate([{"user_id": "u1", "item_id": "i2", "rating": 4.0}])
print(f"Hit Rate@1: {metrics['hit_rate_at_1']:.2%}")
```

## Demo Scripts

Run each project's demo:

```bash
# Document Processor
cd ai-document-processor && python main.py ./sample_documents/

# Image Recognition
cd ai-image-recognition && python main.py --mode detect --input sample.jpg

# QA System
cd ai-qa-system && python main.py

# Recommendation Engine
cd ai-recommendation-engine && python main.py
```

## API Examples

### Document Processor API
```bash
# Upload and analyze
curl -X POST http://localhost:5000/analyze \
  -F "file=@document.pdf"
```

### QA System API
```bash
# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'

# Upload document
curl -X POST http://localhost:8000/documents \
  -F "files=@knowledge.txt"
```

### Recommendation API
```bash
# Train model
curl -X POST http://localhost:8080/train \
  -H "Content-Type: application/json" \
  -d '{"data": [{"user_id": "u1", "item_id": "i1", "rating": 5}]}'

# Get recommendations
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "n_recommendations": 5}'
```
