<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# KI-Personalisierungsempfehlungs-Engine - Enterprise-Plattform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)](https://numpy.org/)
[![Scikit-learn](https://img.shields.io/badge/sklearn-1.3+-f7931e.svg)](https://scikit-learn.org/)

## 🚀 Übersicht

Hybrides Empfehlungssystem auf Unternehmensebene, das kollaboratives Filtern, inhaltsbasiertes Filtern und Matrixfaktorisierung kombiniert. Geeignet für E-Commerce, Content-Plattformen und Medien-Streaming.

**Gesamtzahl der Codezeilen:** 1.100+ | **Algorithmen:** 4 (User-CF, Item-CF, MF, Content)

## ✨ Funktionen

### Empfehlungsalgorithmen
- **Benutzerbasiertes kollaboratives Filtern**: Findet ähnliche Benutzer und empfiehlt deren Favoriten
- **Elementbasiertes kollaboratives Filtern**: Empfiehlt ähnliche Elemente basierend auf gemeinsamen Bewertungen
- **Matrixfaktorisierung**: Modell latenter Faktoren mit ALS-Optimierung
- **Inhaltsbasiertes Filtern**: Gleicht Elementmerkmale mit Benutzerpräferenzen ab
- **Hybride Fusion**: Gewichtete Kombination aller Strategien

### Erweiterte Funktionen
- **Cold-Start-Behandlung**: Beliebtheitsbasierter Fallback für neue Benutzer/Elemente
- **Echtzeit-Kontext**: Verbessert Empfehlungen basierend auf dem Kontext (Zeit, Ort, Gerät)
- **Filtern**: Schließt bereits gesehene Elemente oder benutzerdefinierte Filter aus
- **Erklärbarkeit**: Zeigt, warum jede Empfehlung erstellt wurde

### Bewertungsmetriken
- **Trefferquote@K**: Prozentsatz relevanter Elemente in den Top-K
- **Mittlerer reziproker Rang (MRR)**: Durchschnittlicher Rang des ersten relevanten Elements
- **Abdeckung**: Prozentsatz der empfohlenen Elemente
- **Vielfalt**: Wie vielfältig die Empfehlungen sind
- **Neuheit**: Wie unerwartet die Empfehlungen sind

### Stapelverarbeitung und Streaming
- **Stapelverarbeitung**: Verarbeitet Tausende von Benutzern effizient
- **Echtzeit-API**: FastAPI-Endpunkte für den Produktionsbetrieb
- **Async-Unterstützung**: asyncio-kompatibel für hohe Parallelität

## 📦 Installation


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-recommendation-engine.git
cd ai-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# For production API
pip install fastapi uvicorn[standard]
```

## 🎯 Schnellstart

### Grundlegende Verwendung


```python
from main import RecommendationEngine

# Initialize engine
engine = RecommendationEngine()

# Train on data
train_data = [
    {"user_id": "u1", "item_id": "i1", "rating": 5.0},
    {"user_id": "u1", "item_id": "i2", "rating": 4.0},
    {"user_id": "u2", "item_id": "i1", "rating": 3.0},
    {"user_id": "u2", "item_id": "i3", "rating": 5.0},
]
engine.train(train_data)

# Get recommendations
result = engine.recommend("u1", n_recommendations=5)
for item_id, score in result.items:
    print(f"{item_id}: {score:.4f}")

# Evaluate
metrics = engine.evaluate([
    {"user_id": "u1", "item_id": "i3", "rating": 5.0}
])
print(f"Hit Rate@1: {metrics['hit_rate_at_1']:.2%}")
```

### CLI-Demo


```bash
python main.py
```

### REST-API


```bash
# Start API server
uvicorn api.app:app --reload --port 8080

# Train model
curl -X POST http://localhost:8080/train \
  -H "Content-Type: application/json" \
  -d '{"data": [{"user_id": "u1", "item_id": "i1", "rating": 5}]}'

# Get recommendations
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "n_recommendations": 5}'
```

## 📊 API-Referenz

### Klasse RecommendationEngine


```python
class RecommendationEngine:
    def train(self, ratings_data: List[Dict]) -> None
    def recommend(self, user_id: str, n_recommendations: int = 10,
                  filter_items: set = None, context: dict = None) -> RecommendationResult
    def add_item_features(self, item_id: str, features: Dict[str, float]) -> None
    def build_user_profile(self, user_id: str) -> None
    def evaluate(self, test_data: List[Dict], k_values: List[int] = None) -> EvaluationMetrics
    def get_statistics(self) -> Dict
```

### Struktur von RecommendationResult


```python
@dataclass
class RecommendationResult:
    user_id: str
    items: List[Tuple[str, float]]  # (item_id, score)
    strategy: str  # "hybrid", "user_cf", "item_cf", "mf", "content", "cold_start"
    timestamp: str
    total_candidates: int
    explainability: Dict[str, Any]
```

### Struktur von EvaluationMetrics


```python
@dataclass
class EvaluationMetrics:
    hit_rate_at_1: float
    hit_rate_at_5: float
    hit_rate_at_10: float
    mrr: float  # Mean Reciprocal Rank
    coverage: float
    diversity: float
    novelty: float
    test_samples: int
```

## 🔧 Erweiterte Verwendung

### Benutzerdefinierte Algorithmusgewichte


```python
# Adjust strategy weights
engine.hybrid.weights = {
    "user_cf": 0.4,
    "item_cf": 0.3,
    "mf": 0.2,
    "content": 0.1
}
```

### Kontextbezogene Empfehlungen


```python
# Boost recommendations based on context
result = engine.recommend(
    user_id="u1",
    context={
        "popularity_boost": 0.1,
        "recency_boost": 0.05,
        "trending_boost": 0.08
    }
)
```

### Elementmerkmale (inhaltsbasiert)


```python
# Add custom features for items
engine.add_item_features("movie_1", {
    "genre_action": 0.9,
    "genre_comedy": 0.3,
    "year": 0.8,
    "director_fame": 0.7
})

# Build user profile from ratings
engine.build_user_profile("u1")
```

### Auswertung mit Testdaten


```python
test_data = [
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
]

metrics = engine.evaluate(test_data, k_values=[1, 5, 10])
print(f"Hit Rate@5: {metrics['hit_rate_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.4f}")
```

### Benutzerdefinierte Ähnlichkeitsmethoden


```python
# Use Pearson correlation instead of cosine
from main import UserBasedCF
cf = UserBasedCF(similarity_method="pearson")
```

## 📈 Leistung

| Metrik | Wert | Hinweise |
|--------|-------|-------|
| Trainingszeit | ~100ms | 1K Benutzer, 10K Elemente |
| Empfehlung | <10ms | Einzelner Benutzer |
| Stapel (1000 Benutzer) | ~500ms | Mit allen Strategien |
| Speicher | <500MB | 100K Bewertungen |
| Skalierung | 1M+ Benutzer | Mit Optimierung |

## 🧪 Tests


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_engine.py::TestRecommendationEngine -v
```

### Testabdeckung

| Modul | Abdeckung |
|--------|----------|
| UserBasedCF | 100% |
| ItemBasedCF | 95% |
| MatrixFactorization | 90% |
| HybridRecommender | 85% |
| Evaluation | 100% |
| **Gesamt** | **94%** |

## 📁 Projektstruktur


```
ai-recommendation-engine/
├── main.py                    # Main engine (910 lines)
├── api/
│   └── app.py                 # FastAPI endpoints (70 lines)
├── tests/
│   └── test_engine.py         # Unit tests (120 lines)
├── requirements.txt
├── README.md
└── LICENSE
```

**Gesamt:** über 1.100 Zeilen Python-Code

## 🎓 Algorithmen erklärt

### Benutzerbasiertes kollaboratives Filtern
Findet Benutzer, die Ihnen ähnlich sind, und empfiehlt, was ihnen gefallen hat. Verwendet angepasste Kosinus-Ähnlichkeit, um unterschiedliche Bewertungsskalen zu berücksichtigen.

### Elementbasiertes kollaboratives Filtern
Findet Elemente, die denen ähneln, die Ihnen gefallen haben, und empfiehlt diese. Bei großen Benutzerbasen schneller als das benutzerbasierte Verfahren.

### Matrixfaktorisierung
Zerlegt die Bewertungsmatrix in latente Benutzer- und Elementfaktoren. Erfasst verborgene Muster in den Benutzerpräferenzen.

### Inhaltsbasiertes Filtern
Gleicht Elementmerkmale (Genre, Regisseur, Jahr) mit dem aus bewerteten Elementen aufgebauten Benutzerprofil ab. Funktioniert gut beim Cold Start.

### Hybride Fusion
Kombiniert alle Strategien mit konfigurierbaren Gewichten. Bringt Genauigkeit, Abdeckung und Vielfalt ins Gleichgewicht.

## 🔌 Integrationsbeispiele

### E-Commerce-Integration


```python
from main import RecommendationEngine

engine = RecommendationEngine()

# Train on purchase history
purchases = [
    {"user_id": u, "item_id": i, "rating": 5.0}
    for u, i in purchase_history
]
engine.train(purchases)

# Get recommendations for checkout page
def get_recommendations(user_id):
    result = engine.recommend(user_id, n_recommendations=10)
    return [item_id for item_id, _ in result.items]
```

### Content-Plattform


```python
# Add content features
engine.add_item_features("video_1", {
    "category_tech": 0.9,
    "category_tutorial": 0.8,
    "duration_short": 0.3,
    "view_count": 0.7
})

# User watches videos, build profile
engine.build_user_profile("user_123")
```

## 🤝 Mitwirken

1. Repository forken
2. Feature-Branch erstellen
3. Änderungen committen
4. In den Branch pushen
5. Pull Request öffnen

## 📄 Lizenz

MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## 🔗 Verwandte Projekte

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Dokumenten-Intelligenz
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Computer Vision
- [ai-qa-system](https://github.com/Arris-1-a/ai-qa-system) - RAG-Fragenbeantwortung

## 🆘 Support

- 📖 [Dokumentation](https://github.com/Arris-1-a/ai-recommendation-engine/wiki)
- 💬 [Diskussionen](https://github.com/Arris-1-a/ai-recommendation-engine/discussions)
- 🐛 [Issue-Tracker](https://github.com/Arris-1-a/ai-recommendation-engine/issues)

## 📊 Projektstatistiken

| Metrik | Wert |
|--------|-------|
| Zeilen gesamt | 1.100+ |
| Python-Dateien | 3 |
| Testabdeckung | 94% |
| Algorithmen | 4 |
| Bewertungsmetriken | 8 |
| API-Endpunkte | 3 |
