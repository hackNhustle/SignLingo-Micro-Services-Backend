import pytest
from conftest import KONG_URL

def test_convert_service_health(api_client):
    """Tests if the Gateway successfully routes traffic to the Convert Service."""
    res = api_client.get(f"{KONG_URL}/api/v1/convert/health")
    assert res.status_code == 200
    assert res.json()["service"] == "convert-service"

def test_convert_open_endpoint(api_client):
    """
    Tests an open endpoint on the Convert service.
    Convert service endpoints are typically public (no JWT) in the ROUTE_TABLE.
    """
    res = api_client.get(f"{KONG_URL}/api/v1/convert/health")
    assert res.status_code == 200
