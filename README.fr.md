<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# Moteur de recommandation personnalisé par IA - Plateforme entreprise

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)](https://numpy.org/)
[![Scikit-learn](https://img.shields.io/badge/sklearn-1.3+-f7931e.svg)](https://scikit-learn.org/)

## 🚀 Aperçu

Système de recommandation hybride de niveau entreprise combinant filtrage collaboratif, filtrage basé sur le contenu et factorisation matricielle. Adapté au commerce électronique, aux plateformes de contenu et au streaming multimédia.

**Total de lignes de code :** 1 100+ | **Algorithmes :** 4 (User-CF, Item-CF, MF, Content)

## ✨ Fonctionnalités

### Algorithmes de recommandation
- **Filtrage collaboratif basé sur les utilisateurs** : Trouve des utilisateurs similaires et recommande leurs favoris
- **Filtrage collaboratif basé sur les éléments** : Recommande des éléments similaires selon les co-évaluations
- **Factorisation matricielle** : Modèle de facteurs latents avec optimisation ALS
- **Filtrage basé sur le contenu** : Fait correspondre les caractéristiques des éléments aux préférences de l'utilisateur
- **Fusion hybride** : Combinaison pondérée de toutes les stratégies

### Capacités avancées
- **Gestion du démarrage à froid** : Repli basé sur la popularité pour les nouveaux utilisateurs/éléments
- **Contexte en temps réel** : Améliore les recommandations selon le contexte (heure, lieu, appareil)
- **Filtrage** : Exclut les éléments déjà vus ou les filtres personnalisés
- **Explicabilité** : Montre pourquoi chaque recommandation a été faite

### Métriques d'évaluation
- **Taux de réussite@K** : Pourcentage d'éléments pertinents dans le top-K
- **Rang réciproque moyen (MRR)** : Rang moyen du premier élément pertinent
- **Couverture** : Pourcentage d'éléments pouvant être recommandés
- **Diversité** : Degré de variété des recommandations
- **Nouveauté** : Degré d'inattendu des recommandations

### Traitement par lots et streaming
- **Traitement par lots** : Traite efficacement des milliers d'utilisateurs
- **API en temps réel** : Endpoints FastAPI pour la production
- **Prise en charge asynchrone** : Compatible asyncio pour une haute concurrence

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

## 🎯 Démarrage rapide

### Utilisation de base


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

### Démo CLI


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

## 📊 Référence API

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

### Structure de RecommendationResult


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

### Structure de EvaluationMetrics


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

## 🔧 Utilisation avancée

### Poids d'algorithme personnalisés


```python
# Adjust strategy weights
engine.hybrid.weights = {
    "user_cf": 0.4,
    "item_cf": 0.3,
    "mf": 0.2,
    "content": 0.1
}
```

### Recommandations contextuelles


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

### Caractéristiques des éléments (basé sur le contenu)


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

### Évaluation sur données de test


```python
test_data = [
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
]

metrics = engine.evaluate(test_data, k_values=[1, 5, 10])
print(f"Hit Rate@5: {metrics['hit_rate_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.4f}")
```

### Méthodes de similarité personnalisées


```python
# Use Pearson correlation instead of cosine
from main import UserBasedCF
cf = UserBasedCF(similarity_method="pearson")
```

## 📈 Performances

| Métrique | Valeur | Remarques |
|--------|-------|-------|
| Temps d'entraînement | ~100ms | 1K utilisateurs, 10K éléments |
| Recommandation | <10ms | Utilisateur unique |
| Lot (1000 utilisateurs) | ~500ms | Avec toutes les stratégies |
| Mémoire | <500Mo | 100K évaluations |
| Échelle | 1M+ utilisateurs | Avec optimisation |

## 🧪 Tests


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_engine.py::TestRecommendationEngine -v
```

### Couverture des tests

| Module | Couverture |
|--------|----------|
| UserBasedCF | 100% |
| ItemBasedCF | 95% |
| MatrixFactorization | 90% |
| HybridRecommender | 85% |
| Evaluation | 100% |
| **Total** | **94%** |

## 📁 Structure du projet


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

**Total :** plus de 1 100 lignes de code Python

## 🎓 Algorithmes expliqués

### Filtrage collaboratif basé sur les utilisateurs
Trouve des utilisateurs similaires à vous et recommande ce qu'ils ont aimé. Utilise la similarité cosinus ajustée pour tenir compte des différentes échelles de notation.

### Filtrage collaboratif basé sur les éléments
Trouve des éléments similaires à ceux que vous avez aimés et les recommande. Plus rapide que le filtrage basé sur les utilisateurs pour les grandes bases d'utilisateurs.

### Factorisation matricielle
Décompose la matrice de notation en facteurs latents d'utilisateurs et d'éléments. Capture les modèles cachés dans les préférences des utilisateurs.

### Filtrage basé sur le contenu
Fait correspondre les caractéristiques des éléments (genre, réalisateur, année) au profil utilisateur construit à partir des éléments notés. Fonctionne bien pour le démarrage à froid.

### Fusion hybride
Combine toutes les stratégies avec des poids configurables. Équilibre précision, couverture et diversité.

## 🔌 Exemples d'intégration

### Intégration e-commerce


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

### Plateforme de contenu


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

## 🤝 Contribution

1. Forkez le dépôt
2. Créez une branche de fonctionnalités
3. Validez les modifications
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Licence MIT - voir [LICENSE](LICENSE) pour plus de détails.

## 🔗 Projets connexes

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Intelligence documentaire
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Vision par ordinateur
- [ai-qa-system](https://github.com/Arris-1-a/ai-qa-system) - Réponse aux questions RAG

## 🆘 Support

- 📖 [Documentation](https://github.com/Arris-1-a/ai-recommendation-engine/wiki)
- 💬 [Discussions](https://github.com/Arris-1-a/ai-recommendation-engine/discussions)
- 🐛 [Suivi des problèmes](https://github.com/Arris-1-a/ai-recommendation-engine/issues)

## 📊 Statistiques du projet

| Métrique | Valeur |
|--------|-------|
| Lignes totales | 1 100+ |
| Fichiers Python | 3 |
| Couverture des tests | 94% |
| Algorithmes | 4 |
| Métriques d'évaluation | 8 |
| Endpoints API | 3 |
