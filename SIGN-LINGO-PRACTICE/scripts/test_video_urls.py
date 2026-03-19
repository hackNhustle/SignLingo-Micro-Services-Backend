import requests

r = requests.get('http://localhost:5002/asl/dictionary/all?limit=5')
words = r.json()['words']

print("Video URLs being returned:")
print("=" * 70)
for w in words:
    print(f"{w['word']} -> {w['video_url']}")
