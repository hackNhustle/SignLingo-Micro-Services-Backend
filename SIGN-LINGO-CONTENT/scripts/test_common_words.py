import requests

# Test common_words category
r = requests.get('http://localhost:5002/asl/dictionary/category/common_words?limit=20')
data = r.json()

print(f"Common Words Category:")
print(f"Category: {data['category']}")
print(f"Count: {data['count']}")
print(f"\nFirst 20 words:")
for i, word in enumerate(data['words'][:20], 1):
    print(f"{i}. {word['word']}")
