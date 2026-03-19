import pytest
import time
from conftest import KONG_URL, AUTH_URL

def test_kong_routing_overhead(benchmark, api_client):
    """
    Benchmarks the hardware latency overhead of routing a packet through the Kong 
    Nginx proxy layer before reaching the backend architecture.
    """
    def route_kong():
        api_client.get(f"{KONG_URL}/health")

    # Pedantic mode ensures intensive, high-cadence testing for deep metrics
    benchmark.pedantic(route_kong, iterations=10, rounds=100)

def test_direct_service_latency(benchmark, api_client):
    """
    Benchmarks hitting the python FastAPI Auth layer directly to establish 
    the baseline hardware latency for comparisons against the Kong layer.
    """
    def route_direct():
        api_client.get(f"{AUTH_URL}/health")

    benchmark.pedantic(route_direct, iterations=10, rounds=100)
