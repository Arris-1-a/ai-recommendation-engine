<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# Công cụ gợi ý cá nhân hóa AI - Nền tảng doanh nghiệp

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)](https://numpy.org/)
[![Scikit-learn](https://img.shields.io/badge/sklearn-1.3+-f7931e.svg)](https://scikit-learn.org/)

## 🚀 Tổng quan

Hệ thống gợi ý kết hợp cấp doanh nghiệp kết hợp lọc cộng tác, lọc dựa trên nội dung và phân rã ma trận. Phù hợp với thương mại điện tử, nền tảng nội dung và phát trực tuyến đa phương tiện.

**Tổng số dòng mã:** 1.100+ | **Thuật toán:** 4 (User-CF, Item-CF, MF, Content)

## ✨ Tính năng

### Thuật toán gợi ý
- **Lọc cộng tác dựa trên người dùng**: Tìm người dùng tương tự và gợi ý các mục yêu thích của họ
- **Lọc cộng tác dựa trên mục**: Gợi ý các mục tương tự dựa trên đánh giá chung
- **Phân rã ma trận**: Mô hình nhân tố tiềm ẩn sử dụng tối ưu hóa ALS
- **Lọc dựa trên nội dung**: Khớp đặc điểm mục với sở thích người dùng
- **Kết hợp lai**: Kết hợp có trọng số của mọi chiến lược

### Khả năng nâng cao
- **Xử lý khởi đầu nguội**: Phương án dự phòng dựa trên độ phổ biến cho người dùng/mục mới
- **Bối cảnh thời gian thực**: Tăng cường gợi ý dựa trên bối cảnh (thời gian, vị trí, thiết bị)
- **Lọc**: Loại trừ các mục đã xem hoặc bộ lọc tùy chỉnh
- **Khả năng giải thích**: Hiển thị lý do cho từng gợi ý

### Chỉ số đánh giá
- **Tỷ lệ trúng@K**: Phần trăm mục liên quan trong top-K
- **Hạng nghịch đảo trung bình (MRR)**: Hạng trung bình của mục liên quan đầu tiên
- **Độ phủ**: Phần trăm mục có thể được gợi ý
- **Đa dạng**: Mức độ đa dạng của các gợi ý
- **Mới lạ**: Mức độ bất ngờ của các gợi ý

### Xử lý hàng loạt & phát trực tuyến
- **Xử lý hàng loạt**: Xử lý hàng nghìn người dùng hiệu quả
- **API thời gian thực**: Endpoint FastAPI cho sản xuất
- **Hỗ trợ bất đồng bộ**: Tương thích asyncio cho đồng thời cao

## 📦 Cài đặt


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-recommendation-engine.git
cd ai-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# For production API
pip install fastapi uvicorn[standard]
```

## 🎯 Bắt đầu nhanh

### Sử dụng cơ bản


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

### Bản demo CLI


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

## 📊 Tài liệu tham khảo API

### Lớp RecommendationEngine


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

### Cấu trúc RecommendationResult


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

### Cấu trúc EvaluationMetrics


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

## 🔧 Sử dụng nâng cao

### Trọng số thuật toán tùy chỉnh


```python
# Adjust strategy weights
engine.hybrid.weights = {
    "user_cf": 0.4,
    "item_cf": 0.3,
    "mf": 0.2,
    "content": 0.1
}
```

### Gợi ý nhận biết bối cảnh


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

### Đặc điểm mục (dựa trên nội dung)


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

### Đánh giá trên dữ liệu kiểm thử


```python
test_data = [
    {"user_id": "u1", "item_id": "i3", "rating": 5.0},
    {"user_id": "u2", "item_id": "i1", "rating": 4.0},
]

metrics = engine.evaluate(test_data, k_values=[1, 5, 10])
print(f"Hit Rate@5: {metrics['hit_rate_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.4f}")
```

### Phương pháp tương đồng tùy chỉnh


```python
# Use Pearson correlation instead of cosine
from main import UserBasedCF
cf = UserBasedCF(similarity_method="pearson")
```

## 📈 Hiệu suất

| Chỉ số | Giá trị | Ghi chú |
|--------|-------|-------|
| Thời gian huấn luyện | ~100ms | 1K người dùng, 10K mục |
| Gợi ý | <10ms | Một người dùng |
| Hàng loạt (1000 người dùng) | ~500ms | Với mọi chiến lược |
| Bộ nhớ | <500MB | 100K đánh giá |
| Quy mô | 1M+ người dùng | Có tối ưu hóa |

## 🧪 Kiểm thử


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_engine.py::TestRecommendationEngine -v
```

### Độ phủ kiểm thử

| Mô-đun | Độ phủ |
|--------|----------|
| UserBasedCF | 100% |
| ItemBasedCF | 95% |
| MatrixFactorization | 90% |
| HybridRecommender | 85% |
| Evaluation | 100% |
| **Tổng cộng** | **94%** |

## 📁 Cấu trúc dự án


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

**Tổng cộng:** hơn 1.100 dòng mã Python

## 🎓 Giải thích thuật toán

### Lọc cộng tác dựa trên người dùng
Tìm những người dùng giống bạn và gợi ý những gì họ thích. Sử dụng độ tương đồng cosine đã điều chỉnh để tính đến các thang đánh giá khác nhau.

### Lọc cộng tác dựa trên mục
Tìm các mục tương tự với những mục bạn thích và gợi ý chúng. Nhanh hơn phương pháp dựa trên người dùng với cơ sở người dùng lớn.

### Phân rã ma trận
Phân rã ma trận đánh giá thành các nhân tố tiềm ẩn của người dùng và mục. Nắm bắt các mô hình ẩn trong sở thích của người dùng.

### Lọc dựa trên nội dung
Khớp đặc điểm mục (thể loại, đạo diễn, năm) với hồ sơ người dùng được xây dựng từ các mục đã đánh giá. Hoạt động tốt cho khởi đầu nguội.

### Kết hợp lai
Kết hợp mọi chiến lược với trọng số có thể cấu hình. Cân bằng độ chính xác, độ phủ và tính đa dạng.

## 🔌 Ví dụ tích hợp

### Tích hợp thương mại điện tử


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

### Nền tảng nội dung


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

## 🤝 Đóng góp

1. Fork kho lưu trữ
2. Tạo nhánh tính năng
3. Cam kết các thay đổi
4. Đẩy lên nhánh
5. Mở Pull Request

## 📄 Giấy phép

Giấy phép MIT - xem [LICENSE](LICENSE) để biết chi tiết.

## 🔗 Dự án liên quan

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Trí tuệ tài liệu
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Thị giác máy tính
- [ai-qa-system](https://github.com/Arris-1-a/ai-qa-system) - Hỏi đáp RAG

## 🆘 Hỗ trợ

- 📖 [Tài liệu](https://github.com/Arris-1-a/ai-recommendation-engine/wiki)
- 💬 [Thảo luận](https://github.com/Arris-1-a/ai-recommendation-engine/discussions)
- 🐛 [Trình theo dõi sự cố](https://github.com/Arris-1-a/ai-recommendation-engine/issues)

## 📊 Thống kê dự án

| Chỉ số | Giá trị |
|--------|-------|
| Tổng dòng | 1.100+ |
| Tệp Python | 3 |
| Độ phủ kiểm thử | 94% |
| Thuật toán | 4 |
| Chỉ số đánh giá | 8 |
| Endpoint API | 3 |
