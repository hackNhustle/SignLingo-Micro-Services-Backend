import pytest
from conftest import KONG_URL, CONTENT_URL

def test_content_direct_bypass(api_client):
    """
    Attempts to hit the content service directly bypassing the Gateway. 
    It should FAIL with 401 because verify_signature=True and no token is passed.
    """
    res = api_client.get(f"{CONTENT_URL}/api/v1/alphabet/list")
    assert res.status_code in [401, 403]
    # In FastAPI HTTPBearer, missing header returns 403 Not Authenticated 
    # but based on deps.py logic it might be 401. So we check for both.

def test_content_gateway_no_jwt(api_client):
    """Hits Gateway without a JWT. Gateway must block it."""
    res = api_client.get(f"{KONG_URL}/api/v1/alphabet/list")
    assert res.status_code == 401 
    assert "Missing or invalid Authorization header" in res.text

def test_content_gateway_with_valid_jwt(api_client, auth_headers):
    """Hits Gateway with a mathematically valid JWT. 
    Gateway should accept it and proxy it to Content."""
    res = api_client.get(f"{KONG_URL}/api/v1/alphabet/list", headers=auth_headers)
    assert res.status_code != 401 
