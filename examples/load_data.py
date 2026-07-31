import json
from pathlib import Path

def load_sample_data(filepath: str = None) -> dict:
    """Load sample data for testing."""
    if filepath is None:
        filepath = Path(__file__).parent / "sample_data.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_training_data() -> list:
    """Get training data for recommendation engine."""
    data = load_sample_data()
    return data['ratings']

def get_users() -> list:
    """Get user list."""
    data = load_sample_data()
    return data['users']

def get_products() -> list:
    """Get product list."""
    data = load_sample_data()
    return data['products']

if __name__ == "__main__":
    data = load_sample_data()
    print(f"Users: {len(data['users'])}")
    print(f"Products: {len(data['products'])}")
    print(f"Ratings: {len(data['ratings'])}")
    print(f"\nSample rating: {data['ratings'][0]}")
