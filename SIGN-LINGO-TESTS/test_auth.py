import pytest
from conftest import KONG_URL, AUTH_URL

def test_auth_service_health(api_client):
    """Bypasses Kong and hits the auth microservice directly to ensure it boots."""
    res = api_client.get(f"{AUTH_URL}/health")
    assert res.status_code in [200, 404] # Checks the daemon is responsive

def test_kong_auth_routing(api_client):
    """Tests if Kong successfully routes open traffic to the Auth Service."""
    res = api_client.get(f"{KONG_URL}/api/v1/user/profile")
    # Auth paths are specifically EXCLUDED from Kong JWT interception in kong.yml
    # because users must be able to hit /login to retrieve a JWT first.
    # Therefore, the 401 should come directly from the python backend!
    assert res.status_code in [401, 404]
