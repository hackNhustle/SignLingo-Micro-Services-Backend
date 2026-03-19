import pytest
from conftest import KONG_URL, PRACTICE_URL

def test_practice_direct_bypass(api_client):
    """
    Attempts to hit the practice service directly bypassing the Gateway. 
    It should FAIL with 401/403 because verify_signature=True and no token is passed.
    """
    res = api_client.get(f"{PRACTICE_URL}/api/v1/progress/overview")
    assert res.status_code in [401, 403]

def test_practice_gateway_no_jwt(api_client):
    """Hits Gateway without a JWT. Gateway must block it BEFORE routing."""
    res = api_client.get(f"{KONG_URL}/api/v1/progress/overview")
    assert res.status_code == 401 
    assert "Missing or invalid Authorization header" in res.text

def test_practice_gateway_with_valid_jwt(api_client, auth_headers):
    """Hits Gateway with a mathematically valid JWT. 
    Gateway should accept it and the Practice service should trust it."""
    res = api_client.get(f"{KONG_URL}/api/v1/progress/overview", headers=auth_headers)
    assert res.status_code != 401 
