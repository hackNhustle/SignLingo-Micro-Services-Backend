import pytest
import httpx
from conftest import KONG_URL, AUTH_URL, CONTENT_URL, PRACTICE_URL

# Mapping services to URLs
SERVICES = {
    "AUTH": AUTH_URL,
    "CONTENT": CONTENT_URL,
    "PRACTICE": PRACTICE_URL,
    "CONVERT": "http://localhost:5005", # Default port for convert
    "GATEWAY": "http://localhost:8000",
}

def extract_metrics(response):
    """Safely extracts profiling headers from a response."""
    try:
        cpu_time = float(response.headers.get("X-Profiling-CPU-Time-MS", 0))
        mem_delta = float(response.headers.get("X-Profiling-Mem-Delta-MB", 0))
        rss = float(response.headers.get("X-Profiling-RSS-MB", 0))
        return {
            "cpu_time_ms": cpu_time,
            "mem_delta_mb": mem_delta,
            "rss_mb": rss
        }
    except (ValueError, TypeError):
        return None

def test_profiling_all_services(api_client):
    """
    Triggers health endpoints for all services and collects profiling metrics.
    """
    results = {}
    
    for service_name, url in SERVICES.items():
        try:
            # Hit the health endpoint
            response = api_client.get(f"{url}/health")
            assert response.status_code == 200, f"{service_name} at {url} is not responding with 200"
            
            metrics = extract_metrics(response)
            if metrics:
                results[service_name] = metrics
            else:
                pytest.fail(f"Could not extract profiling metrics from {service_name}")
        except httpx.ConnectError:
            pytest.skip(f"{service_name} is not running at {url}")

    # Log results to console
    print("\n\n" + "="*60)
    print(f"{'SERVICE':<15} | {'CPU (ms)':<10} | {'MEM Δ (MB)':<10} | {'RSS (MB)':<10}")
    print("-" * 60)
    for name, m in results.items():
        print(f"{name:<15} | {m['cpu_time_ms']:>8.3f}   | {m['mem_delta_mb']:>+8.3f}   | {m['rss_mb']:>8.3f}")
    print("="*60 + "\n")

@pytest.mark.parametrize("endpoint", [
    "/api/v1/auth/login", # Should be 405 or 422 if called with GET
    "/api/v1/auth/register",
])
def test_auth_intensive_endpoints(api_client, endpoint):
    """Tests memory and CPU usage on more intensive Auth endpoints."""
    url = f"{AUTH_URL}{endpoint}"
    # Using GET to trigger a failure/validation path for quick profiling
    response = api_client.get(url)
    metrics = extract_metrics(response)
    if metrics:
        print(f"\nIntensive endpoint {endpoint}: CPU={metrics['cpu_time_ms']}ms, MemΔ={metrics['mem_delta_mb']}MB")
