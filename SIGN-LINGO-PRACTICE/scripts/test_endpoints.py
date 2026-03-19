import requests
import json

BASE_URL = "http://localhost:5002/api/v1"

def test_text_to_sign():
    print("Testing POST /convert/text-to-sign...")
    payload = {
        "text": "Hello world",
        "language": "en",
        "speed": "normal"
    }
    try:
        response = requests.post(f"{BASE_URL}/convert/text-to-sign", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code == 200:
            print("SUCCESS: Endpoint is working!")
        else:
            print("FAILED: Endpoint returned error.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_text_to_sign()
