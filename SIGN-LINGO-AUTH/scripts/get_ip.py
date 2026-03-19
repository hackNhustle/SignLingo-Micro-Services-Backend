import requests

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        print(f"Your Public IP is: {response.json()['ip']}")
    except Exception as e:
        print(f"Could not determine public IP: {e}")

if __name__ == "__main__":
    get_public_ip()
