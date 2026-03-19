import requests

# Get first 100 words
r = requests.get('http://localhost:5002/asl/dictionary/all?limit=100')
data = r.json()

print(f"Total words: {data['total']}")
print(f"\nFirst 30 words:")
for i, word in enumerate(data['words'][:30], 1):
    print(f"{i}. {word['word']} ({word['category']})")

print(f"\nWords 50-70:")
r2 = requests.get('http://localhost:5002/asl/dictionary/all?limit=20&offset=50')
data2 = r2.json()
for i, word in enumerate(data2['words'], 51):
    print(f"{i}. {word['word']} ({word['category']})")
