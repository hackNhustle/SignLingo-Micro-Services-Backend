import requests

r = requests.get('http://localhost:5002/asl/dictionary/categories')
categories = r.json()['categories']

print("Categories returned by API:")
print("=" * 50)
for i, cat in enumerate(categories, 1):
    print(f"{i}. {cat['name']}")
    print(f"   Display Name: {cat['display_name']}")
    print(f"   Count: {cat['count']}")
    print(f"   Preview: {cat['preview']}")
    print()
