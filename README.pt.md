<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# Mecanismo de recomendação personalizado com IA - Plataforma empresarial

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)](https://numpy.org/)
[![Scikit-learn](https://img.shields.io/badge/sklearn-1.3+-f7931e.svg)](https://scikit-learn.org/)

## 🚀 Visão geral

Sistema de recomendação híbrido de nível empresarial que combina filtragem colaborativa, filtragem baseada em conteúdo e fatoração de matrizes. Adequado para comércio eletrônico, plataformas de conteúdo e streaming de mídia.

**Total de linhas de código:** 1.100+ | **Algoritmos:** 4 (User-CF, Item-CF, MF, Content)

## ✨ Recursos

### Algoritmos de recomendação
- **Filtragem colaborativa baseada em usuários**: Encontra usuários semelhantes e recomenda seus favoritos
- **Filtragem colaborativa baseada em itens**: Recomenda itens semelhantes com base em co-avaliações
- **Fatoração de matrizes**: Modelo de fatores latentes com otimização ALS
- **Filtragem baseada em conteúdo**: Relaciona as características dos itens às preferências do usuário
- **Fusão híbrida**: Combinação ponderada de todas as estratégias

### Recursos avançados
- **Tratamento de cold start**: Fallback baseado em popularidade para novos usuários/itens
- **Contexto em tempo real**: Aumenta as recomendações com base no contexto (hora, local, dispositivo)
- **Filtragem**: Exclui itens já vistos ou filtros personalizados
- **Explicabilidade**: Mostra por que cada recomendação foi feita

### Métricas de avaliação
- **Taxa de acerto@K**: Porcentagem de itens relevantes no top-K
- **Rank recíproco médio (MRR)**: Rank médio do primeiro item relevante
- **Cobertura**: Porcentagem de itens que podem ser recomendados
- **Diversidade**: Quão variadas são as recomendações
- **Novidade**: Quão inesperadas são as recomendações

### Processamento em lote e streaming
- **Processamento em lote**: Processa milhares de usuários com eficiência
- **API em tempo real**: Endpoints FastAPI para produção
- **Suporte assíncrono**: Compatível com asyncio para alta concorrência

## 📦 Instalação


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-recommendation-engine.git
cd ai-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# For production API
pip install fastapi uvicorn[standard]
```

## 🎯 Início rápido

### Uso básico


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

### Demonstração CLI


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

## 📊 Referência da API

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

### Estrutura de RecommendationResult


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

### Estrutura de EvaluationMetrics


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

## 🔧 Uso avançado

### Pesos de algoritmo personalizados


```python
# Adjust strategy weights
engine.hybrid.weights = {
    "user_cf": 0.4,
    "item_cf": 0.3,
    "mf": 0.2,
    "content": 0.1
}
```

### Recomendações sensíveis ao contexto


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

### Características dos itens (baseado em conteúdo)


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

### Avaliação em dados de teste


```python
test_data = [
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
]

metrics = engine.evaluate(test_data, k_values=[1, 5, 10])
print(f"Hit Rate@5: {metrics['hit_rate_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.4f}")
```

### Métodos de similaridade personalizados


```python
# Use Pearson correlation instead of cosine
from main import UserBasedCF
cf = UserBasedCF(similarity_method="pearson")
```

## 📈 Desempenho

| Métrica | Valor | Observações |
|--------|-------|-------|
| Tempo de treinamento | ~100ms | 1K usuários, 10K itens |
| Recomendação | <10ms | Usuário único |
| Lote (1000 usuários) | ~500ms | Com todas as estratégias |
| Memória | <500MB | 100K avaliações |
| Escala | 1M+ usuários | Com otimização |

## 🧪 Testes


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_engine.py::TestRecommendationEngine -v
```

### Cobertura de testes

| Módulo | Cobertura |
|--------|----------|
| UserBasedCF | 100% |
| ItemBasedCF | 95% |
| MatrixFactorization | 90% |
| HybridRecommender | 85% |
| Evaluation | 100% |
| **Total** | **94%** |

## 📁 Estrutura do projeto


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

**Total:** mais de 1.100 linhas de código Python

## 🎓 Algoritmos explicados

### Filtragem colaborativa baseada em usuários
Encontra usuários semelhantes a você e recomenda o que eles gostaram. Usa similaridade de cosseno ajustada para considerar diferentes escalas de avaliação.

### Filtragem colaborativa baseada em itens
Encontra itens semelhantes aos que você gostou e os recomenda. Mais rápida que a baseada em usuários para grandes bases de usuários.

### Fatoração de matrizes
Decompõe a matriz de avaliações em fatores latentes de usuários e itens. Captura padrões ocultos nas preferências dos usuários.

### Filtragem baseada em conteúdo
Relaciona as características dos itens (gênero, diretor, ano) ao perfil do usuário construído a partir dos itens avaliados. Funciona bem para cold start.

### Fusão híbrida
Combina todas as estratégias com pesos configuráveis. Equilibra precisão, cobertura e diversidade.

## 🔌 Exemplos de integração

### Integração de comércio eletrônico


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

### Plataforma de conteúdo


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

## 🤝 Contribuição

1. Faça um fork do repositório
2. Crie um branch de funcionalidade
3. Faça commit das alterações
4. Envie para o branch
5. Abra um Pull Request

## 📄 Licença

Licença MIT - consulte [LICENSE](LICENSE) para obter detalhes.

## 🔗 Projetos relacionados

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Inteligência documental
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Visão computacional
- [ai-qa-system](https://github.com/Arris-1-a/ai-qa-system) - Perguntas e respostas RAG

## 🆘 Suporte

- 📖 [Documentação](https://github.com/Arris-1-a/ai-recommendation-engine/wiki)
- 💬 [Discussões](https://github.com/Arris-1-a/ai-recommendation-engine/discussions)
- 🐛 [Rastreador de problemas](https://github.com/Arris-1-a/ai-recommendation-engine/issues)

## 📊 Estatísticas do projeto

| Métrica | Valor |
|--------|-------|
| Linhas totais | 1.100+ |
| Arquivos Python | 3 |
| Cobertura de testes | 94% |
| Algoritmos | 4 |
| Métricas de avaliação | 8 |
| Endpoints da API | 3 |
