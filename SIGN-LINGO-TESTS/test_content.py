import pytest
from conftest import KONG_URL, CONTENT_URL

def test_content_direct_bypass(api_client):
    """
    Attempts to hit the content service directly bypassing Kong. 
    It should explicitly FAIL with 401 because the native Kong 
    X-Consumer-Username headers are missing.
    """
    res = api_client.get(f"{CONTENT_URL}/api/v1/alphabet/list")
    assert res.status_code == 401
    assert "Missing Kong Gateway" in res.text

def test_content_kong_no_jwt(api_client):
    """Hits Kong without a JWT. Kong must block it BEFORE routing to Python."""
    res = api_client.get(f"{KONG_URL}/api/v1/alphabet/list")
    assert res.status_code == 401 # Kong standard unauthorized response
    assert "Unauthorized" in res.text

def test_content_kong_with_valid_jwt(api_client, auth_headers):
    """Hits Kong with a mathematically valid JWT. 
    Kong should accept it, dynamically inject X-Consumer headers, 
    and the Content service should implicitly trust and process it."""
    res = api_client.get(f"{KONG_URL}/api/v1/alphabet/list", headers=auth_headers)
    # As long as we don't get a 401 from Kong, the gateway auth sequence passed!
    assert res.status_code != 401 
