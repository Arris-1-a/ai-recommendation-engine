<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# Motore di raccomandazione personalizzato con IA - Piattaforma enterprise

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)](https://numpy.org/)
[![Scikit-learn](https://img.shields.io/badge/sklearn-1.3+-f7931e.svg)](https://scikit-learn.org/)

## 🚀 Panoramica

Sistema di raccomandazione ibrido di livello enterprise che combina filtraggio collaborativo, filtraggio basato sul contenuto e fattorizzazione a matrici. Adatto a e-commerce, piattaforme di contenuti e streaming multimediale.

**Totale righe di codice:** 1.100+ | **Algoritmi:** 4 (User-CF, Item-CF, MF, Content)

## ✨ Caratteristiche

### Algoritmi di raccomandazione
- **Filtraggio collaborativo basato sugli utenti**: Trova utenti simili e raccomanda i loro preferiti
- **Filtraggio collaborativo basato sugli elementi**: Raccomanda elementi simili in base alle co-valutazioni
- **Fattorizzazione a matrici**: Modello a fattori latenti con ottimizzazione ALS
- **Filtraggio basato sul contenuto**: Abbina le caratteristiche degli elementi alle preferenze dell'utente
- **Fusione ibrida**: Combinazione ponderata di tutte le strategie

### Funzionalità avanzate
- **Gestione del cold start**: Fallback basato sulla popolarità per nuovi utenti/elementi
- **Contesto in tempo reale**: Migliora le raccomandazioni in base al contesto (ora, luogo, dispositivo)
- **Filtraggio**: Esclude elementi già visti o filtri personalizzati
- **Spiegabilità**: Mostra il motivo di ogni raccomandazione

### Metriche di valutazione
- **Tasso di successo@K**: Percentuale di elementi pertinenti nei top-K
- **Rango reciproco medio (MRR)**: Rango medio del primo elemento pertinente
- **Copertura**: Percentuale di elementi raccomandabili
- **Diversità**: Quanto sono varie le raccomandazioni
- **Novità**: Quanto sono inaspettate le raccomandazioni

### Elaborazione batch e streaming
- **Elaborazione batch**: Elabora migliaia di utenti in modo efficiente
- **API in tempo reale**: Endpoint FastAPI per la produzione
- **Supporto asincrono**: Compatibile con asyncio per alta concorrenza

## 📦 Installazione


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-recommendation-engine.git
cd ai-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# For production API
pip install fastapi uvicorn[standard]
```

## 🎯 Avvio rapido

### Utilizzo di base


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

### Demo CLI


```bash
python main.py
```

### API REST


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

## 📊 Riferimento API

### Classe RecommendationEngine


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

### Struttura di RecommendationResult


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

### Struttura di EvaluationMetrics


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

## 🔧 Utilizzo avanzato

### Pesi degli algoritmi personalizzati


```python
# Adjust strategy weights
engine.hybrid.weights = {
    "user_cf": 0.4,
    "item_cf": 0.3,
    "mf": 0.2,
    "content": 0.1
}
```

### Raccomandazioni sensibili al contesto


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

### Caratteristiche degli elementi (basato sul contenuto)


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

### Valutazione su dati di test


```python
test_data = [
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
]

metrics = engine.evaluate(test_data, k_values=[1, 5, 10])
print(f"Hit Rate@5: {metrics['hit_rate_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.4f}")
```

### Metodi di similarità personalizzati


```python
# Use Pearson correlation instead of cosine
from main import UserBasedCF
cf = UserBasedCF(similarity_method="pearson")
```

## 📈 Prestazioni

| Metrica | Valore | Note |
|--------|-------|-------|
| Tempo di addestramento | ~100ms | 1K utenti, 10K elementi |
| Raccomandazione | <10ms | Utente singolo |
| Lotto (1000 utenti) | ~500ms | Con tutte le strategie |
| Memoria | <500MB | 100K valutazioni |
| Scalabilità | 1M+ utenti | Con ottimizzazione |

## 🧪 Test


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_engine.py::TestRecommendationEngine -v
```

### Copertura dei test

| Modulo | Copertura |
|--------|----------|
| UserBasedCF | 100% |
| ItemBasedCF | 95% |
| MatrixFactorization | 90% |
| HybridRecommender | 85% |
| Evaluation | 100% |
| **Totale** | **94%** |

## 📁 Struttura del progetto


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

**Totale:** oltre 1.100 righe di codice Python

## 🎓 Algoritmi spiegati

### Filtraggio collaborativo basato sugli utenti
Trova utenti simili a te e raccomanda ciò che è piaciuto loro. Utilizza la similarità del coseno adattata per tenere conto delle diverse scale di valutazione.

### Filtraggio collaborativo basato sugli elementi
Trova elementi simili a quelli che ti sono piaciuti e li raccomanda. Più veloce del metodo basato sugli utenti per grandi basi utenti.

### Fattorizzazione a matrici
Decompone la matrice di valutazione in fattori latenti di utenti ed elementi. Cattura modelli nascosti nelle preferenze degli utenti.

### Filtraggio basato sul contenuto
Abbina le caratteristiche degli elementi (genere, regista, anno) al profilo utente costruito dagli elementi valutati. Funziona bene per il cold start.

### Fusione ibrida
Combina tutte le strategie con pesi configurabili. Bilancia accuratezza, copertura e diversità.

## 🔌 Esempi di integrazione

### Integrazione e-commerce


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

### Piattaforma di contenuti


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

## 🤝 Contributi

1. Fai un fork del repository
2. Crea un branch per la funzionalità
3. Committa le modifiche
4. Carica sul branch
5. Apri una Pull Request

## 📄 Licenza

Licenza MIT - vedi [LICENSE](LICENSE) per i dettagli.

## 🔗 Progetti correlati

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Intelligenza documentale
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Visione artificiale
- [ai-qa-system](https://github.com/Arris-1-a/ai-qa-system) - Risposta alle domande RAG

## 🆘 Supporto

- 📖 [Documentazione](https://github.com/Arris-1-a/ai-recommendation-engine/wiki)
- 💬 [Discussioni](https://github.com/Arris-1-a/ai-recommendation-engine/discussions)
- 🐛 [Tracker dei problemi](https://github.com/Arris-1-a/ai-recommendation-engine/issues)

## 📊 Statistiche del progetto

| Metrica | Valore |
|--------|-------|
| Righe totali | 1.100+ |
| File Python | 3 |
| Copertura dei test | 94% |
| Algoritmi | 4 |
| Metriche di valutazione | 8 |
| Endpoint API | 3 |
