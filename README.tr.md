<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# AI Kişiselleştirilmiş Öneri Motoru - Kurumsal Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)](https://numpy.org/)
[![Scikit-learn](https://img.shields.io/badge/sklearn-1.3+-f7931e.svg)](https://scikit-learn.org/)

## 🚀 Genel Bakış

İşbirlikçi filtreleme, içerik tabanlı filtreleme ve matris çarpanlarına ayırmayı birleştiren kurumsal düzeyde hibrit öneri sistemi. E-ticaret, içerik platformları ve medya akışı için uygundur.

**Toplam Kod Satırı:** 1.100+ | **Algoritmalar:** 4 (User-CF, Item-CF, MF, Content)

## ✨ Özellikler

### Öneri Algoritmaları
- **Kullanıcı Tabanlı İşbirlikçi Filtreleme**: Benzer kullanıcıları bulun ve favorilerini önerin
- **Öğe Tabanlı İşbirlikçi Filtreleme**: Ortak puanlamalara dayalı benzer öğeleri önerin
- **Matris Çarpanlarına Ayırma**: ALS optimizasyonu kullanan gizli faktör modeli
- **İçerik Tabanlı Filtreleme**: Öğe özelliklerini kullanıcı tercihleriyle eşleştirin
- **Hibrit Füzyon**: Tüm stratejilerin ağırlıklı kombinasyonu

### Gelişmiş Yetenekler
- **Soğuk Başlangıç Yönetimi**: Yeni kullanıcılar/öğeler için popülerliğe dayalı geri dönüş
- **Gerçek Zamanlı Bağlam**: Bağlama (zaman, konum, cihaz) göre önerileri güçlendirin
- **Filtreleme**: Daha önce görülen öğeleri veya özel filtreleri hariç tutun
- **Açıklanabilirlik**: Her önerinin neden yapıldığını gösterin

### Değerlendirme Metrikleri
- **Hit Rate@K**: İlk K içindeki ilgili öğelerin yüzdesi
- **Ortalama Karşılıklı Sıralama (MRR)**: İlk ilgili öğenin ortalama sırası
- **Kapsam**: Önerilebilen öğelerin yüzdesi
- **Çeşitlilik**: Önerilerin ne kadar çeşitli olduğu
- **Yenilik**: Önerilerin ne kadar beklenmedik olduğu

### Toplu İşleme ve Akış
- **Toplu İşleme**: Binlerce kullanıcıyı verimli şekilde işleyin
- **Gerçek Zamanlı API**: Üretim için FastAPI uç noktaları
- **Async Desteği**: Yüksek eşzamanlılık için asyncio uyumlu

## 📦 Kurulum


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-recommendation-engine.git
cd ai-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# For production API
pip install fastapi uvicorn[standard]
```

## 🎯 Hızlı Başlangıç

### Temel Kullanım


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

### CLI Demosu


```bash
python main.py
```

### REST API


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

## 📊 API Referansı

### RecommendationEngine Sınıfı


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

### RecommendationResult Yapısı


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

### EvaluationMetrics Yapısı


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

## 🔧 Gelişmiş Kullanım

### Özel Algoritma Ağırlıkları


```python
# Adjust strategy weights
engine.hybrid.weights = {
    "user_cf": 0.4,
    "item_cf": 0.3,
    "mf": 0.2,
    "content": 0.1
}
```

### Bağlam Duyarlı Öneriler


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

### Öğe Özellikleri (İçerik Tabanlı)


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

### Test Verileriyle Değerlendirme


```python
test_data = [
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
]

metrics = engine.evaluate(test_data, k_values=[1, 5, 10])
print(f"Hit Rate@5: {metrics['hit_rate_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.4f}")
```

### Özel Benzerlik Yöntemleri


```python
# Use Pearson correlation instead of cosine
from main import UserBasedCF
cf = UserBasedCF(similarity_method="pearson")
```

## 📈 Performans

| Metrik | Değer | Notlar |
|--------|-------|-------|
| Eğitim Süresi | ~100ms | 1K kullanıcı, 10K öğe |
| Öneri | <10ms | Tek kullanıcı |
| Toplu (1000 kullanıcı) | ~500ms | Tüm stratejilerle |
| Bellek | <500MB | 100K puanlama |
| Ölçek | 1M+ kullanıcı | Optimizasyonla |

## 🧪 Test


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_engine.py::TestRecommendationEngine -v
```

### Test Kapsamı

| Modül | Kapsam |
|--------|----------|
| UserBasedCF | 100% |
| ItemBasedCF | 95% |
| MatrixFactorization | 90% |
| HybridRecommender | 85% |
| Evaluation | 100% |
| **Toplam** | **%94** |

## 📁 Proje Yapısı


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

**Toplam:** 1.100'den fazla satır Python kodu

## 🎓 Algoritmalar Açıklandı

### Kullanıcı Tabanlı İşbirlikçi Filtreleme
Size benzer kullanıcıları bulur ve onların beğendiklerini önerir. Farklı puanlama ölçeklerini hesaba katmak için ayarlanmış kosinüs benzerliği kullanır.

### Öğe Tabanlı İşbirlikçi Filtreleme
Beğendiklerinize benzer öğeleri bulur ve bunları önerir. Büyük kullanıcı tabanları için kullanıcı tabanlı yöntemden daha hızlıdır.

### Matris Çarpanlarına Ayırma
Puanlama matrisini kullanıcı ve öğe gizli faktörlerine ayırır. Kullanıcı tercihlerindeki gizli kalıpları yakalar.

### İçerik Tabanlı Filtreleme
Öğe özelliklerini (tür, yönetmen, yıl) puanlanan öğelerden oluşturulan kullanıcı profiliyle eşleştirir. Soğuk başlangıçta iyi çalışır.

### Hibrit Füzyon
Tüm stratejileri yapılandırılabilir ağırlıklarla birleştirir. Doğruluk, kapsam ve çeşitliliği dengeler.

## 🔌 Entegrasyon Örnekleri

### E-ticaret Entegrasyonu


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

### İçerik Platformu


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

## 🤝 Katkıda Bulunma

1. Depoyu fork edin
2. Özellik dalı oluşturun
3. Değişiklikleri commit edin
4. Dala push edin
5. Pull Request açın

## 📄 Lisans

MIT Lisansı - ayrıntılar için [LICENSE](LICENSE) bölümüne bakın.

## 🔗 İlgili Projeler

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Belge Zekâsı
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Bilgisayar Görüşü
- [ai-qa-system](https://github.com/Arris-1-a/ai-qa-system) - RAG Soru-Cevap

## 🆘 Destek

- 📖 [Dokümantasyon](https://github.com/Arris-1-a/ai-recommendation-engine/wiki)
- 💬 [Tartışmalar](https://github.com/Arris-1-a/ai-recommendation-engine/discussions)
- 🐛 [Sorun Takipçisi](https://github.com/Arris-1-a/ai-recommendation-engine/issues)

## 📊 Proje İstatistikleri

| Metrik | Değer |
|--------|-------|
| Toplam Satır | 1.100+ |
| Python Dosyaları | 3 |
| Test Kapsamı | %94 |
| Algoritma | 4 |
| Değerlendirme Metriği | 8 |
| API Uç Noktası | 3 |
